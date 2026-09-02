# 02 — Project: Story Generator

> Week 13 index: [README.md](README.md)

**Session 1 project:** *Story Generator — an interactive story generator that: maintains story context in state; accepts user choices at decision points; generates narrative based on selections; tracks story progression through the graph — demonstrating creative applications of LangGraph's state management capabilities.*

---

## What you'll learn

- State-driven branching as a *creative* application (not just RAG plumbing)
- Human-in-the-loop via conditional edges waiting on user input
- Progression tracking in state (the story's world as a typed object)
- The template pattern for any "multi-stage interactive flow" your capstone needs

## 1. The design

```
START ─► setup ─► narrate ─► present_choices ─► [wait for choice] ─► apply_choice ─┐
                     ▲                                                            │
                     └────────────────────────────────────────────────────────────┘
                     ──(chapters < N)──► narrate … else ─► ending ─► END
```

State carries the whole story world:

```python
from typing import Annotated, TypedDict

class StoryState(TypedDict):
    premise: str
    genre: str
    chapters: Annotated[list[str], lambda a, b: a + [b]]   # append-only reducer
    current_options: list[str]
    user_choice: str
    world: dict                                            # tracked facts: characters, places
    chapter_count: int
    finished: bool
```

## 2. The nodes

```python
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
client = OpenAI()

def setup(state: StoryState):
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.9,
        messages=[{"role": "user", "content":
                   f"Create a one-paragraph premise for a {state['genre']} story. "
                   "End by naming the protagonist and the central mystery."}])
    return {"premise": resp.choices[0].message.content,
            "chapter_count": 0, "world": {}, "chapters": []}

def narrate(state: StoryState):
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.9,
        messages=[{"role": "user", "content":
                   f"Premise: {state['premise']}\nWorld so far: {state['world']}\n"
                   f"Write chapter {state['chapter_count'] + 1} (120 words), "
                   "ending on a decision point."}])
    chapter = resp.choices[0].message.content
    return {"chapters": [chapter], "chapter_count": state["chapter_count"] + 1}

def present_choices(state: StoryState):
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.7,
        messages=[{"role": "user", "content":
                   f"From this chapter, list exactly 3 short action options the "
                   f"protagonist could take. One per line, no numbers."}])
    return {"current_options": resp.choices[0].message.content.splitlines()}
```

`apply_choice` merges the user's decision into `world` (tracked facts):

```python
import json

def apply_choice(state: StoryState):
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content":
                   f"Choice: {state['user_choice']}\nUpdate this world fact JSON "
                   f"(add/modify keys only): {json.dumps(state['world'])}\n"
                   "Return only the updated JSON."}])
    try:
        world = json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        world = state["world"]                      # graceful fallback (W6-03 rule)
    return {"world": world, "user_choice": ""}
```

## 3. The graph — including the wait-for-human edge

```python
def route_after_choice(state: StoryState) -> str:
    if state["finished"] or state["chapter_count"] >= 5:     # the loop's exit condition
        return "ending"
    return "narrate"

g = StateGraph(StoryState)
g.add_node("setup", setup)
g.add_node("narrate", narrate)
g.add_node("present_choices", present_choices)
g.add_node("apply_choice", apply_choice)
g.add_node("ending", lambda s: {"finished": True})

g.add_edge(START, "setup")
g.add_edge("setup", "narrate")
g.add_edge("narrate", "present_choices")
# WAIT: instead of an automatic edge into apply_choice, the graph *interrupts* here
# (file 06's checkpointer) — or, in the simple version, the caller supplies the choice:
g.add_conditional_edges(
    "present_choices",
    lambda s: "apply_choice" if s.get("user_choice") else "WAIT",
    {"apply_choice": "apply_choice", "WAIT": END},          # pause: caller sets user_choice, re-invokes
)
g.add_conditional_edges("apply_choice", route_after_choice,
                        {"narrate": "narrate", "ending": "ending"})
g.add_edge("ending", END)

story = g.compile()
```

**The WAIT pattern** — returning `END` when `user_choice` is empty — is the simplest human-in-the-loop: the graph pauses, your app collects the choice, sets `user_choice`, and re-invokes with the *same state* (persist it, or use file 06's checkpointer for the robust version).

```python
state = story.invoke({"genre": "cyberpunk mystery"})
# ...present options, get input...
state["user_choice"] = "Hack the security terminal"
state = story.invoke(state)          # resumes with full story world intact
```

## 4. Why this toy matters (the transferable pattern)

Every interactive multi-stage flow is this graph:

| Story generator | Capstone analog |
|---|---|
| premise | ticket intake / query understanding |
| narrate | generate a response/analysis stage |
| choices + WAIT | human approval / clarification (W10-04 HITL) |
| `world` facts | accumulated findings/scratchpad (W10-02) |
| chapter_count bound | max-iterations guard (W11-03 anti-pattern fix) |

Your support-ticket router (file 03) is the same skeleton with domain nodes.

## Exercises

1. Run the generator for 5 chapters with scripted choices (pick randomly). Print the full `chapters` list — does the world JSON keep the narrative consistent?
2. Add a `characters` list reducer (append-only). Have `apply_choice` extract new characters per chapter.
3. Deliberately break the JSON in `apply_choice` (feed malformed JSON) — verify the fallback. Then remove the fallback and observe the graph crash: which failure class is worse in production?
4. Convert the WAIT pattern to LangGraph's real `interrupt_before` with a checkpointer (file 06) — what do you gain (state persistence, time travel)?
5. Genre A/B: run the same choices through two genres; diff the `world` dicts. What does this teach you about temperature and state?

## Pitfalls

- **Choices presented but never enforced** — the narrative must *reflect* the choice (apply_choice → world → next narrate reads world)
- **Unbounded chapters** — the `chapter_count >= 5` edge is the whole point; remove it and the graph loops forever (W11-03)
- **World JSON as free text** — no schema, no validation; use `output_type`-style parsing with fallback
- **Mutating state inside nodes** — nodes return *partial updates*; in-place mutation breaks checkpointing (file 06)
- **WAIT without persistence** — re-invoking with a fresh dict loses the story; persist state between invocations

## Resources

- LangGraph [concepts: graphs](https://langchain-ai.github.io/langgraph/concepts/low_level/) — StateGraph/nodes/edges reference
- LangGraph [human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) — the robust WAIT pattern (file 06)
- LangGraph examples repo — interactive/story-style flows
- W13-03 — the same skeleton, domain-serious
