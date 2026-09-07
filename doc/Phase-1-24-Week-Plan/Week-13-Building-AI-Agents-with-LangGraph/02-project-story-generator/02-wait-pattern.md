# The WAIT Pattern — Pausing for Human Choice

**What you'll learn:** pausing a graph mid-run for human input: the
interrupt/checkpoint mechanics, the resume contract, and the UI loop
around it. (Mechanics verified in file 06; this file applies them.)

## 1. The pause, mechanically

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(StoryState)
builder.add_node("generate", generate_chapter)
builder.add_node("apply", apply_choice)
builder.add_edge(START, "generate")
builder.add_conditional_edges(
    "generate",
    lambda s: END if s["done"] else "apply",
    {"apply": "apply", END: END},
)
builder.add_edge("apply", "generate")

graph = builder.compile(
    checkpointer=checkpointer,          # required for pauses
    interrupt_before=["apply"],         # pause BEFORE applying the choice
)
```

| Piece | Role |
|---|---|
| `checkpointer` | stores state at every step (durability) |
| `interrupt_before=["apply"]` | stops before the human's decision lands |
| `config["thread_id"]` | one story = one thread |
| `graph.invoke(None, config)` | resume after the human acts |

## 2. The resume contract

```python
config = {"configurable": {"thread_id": "story-42"}}

# first run: generates chapter + options, then pauses before apply
graph.invoke({"premise": "A city under a sleeping sea."}, config)

# human picks; update the state's chosen field, then resume
graph.update_state(config, {"chosen": "follow the whale song"})
graph.invoke(None, config)     # None = continue from the interrupt
```

| Step | Call | State after |
|---|---|---|
| start | `invoke(inputs, config)` | chapter 1 + options, paused |
| choose | `update_state(config, {"chosen": ...})` | chosen set |
| resume | `invoke(None, config)` | chapter 2 + new options |

The `invoke(None, ...)` resume is the WAIT pattern's whole secret: the
graph *stops* at the interrupt, the world waits in the checkpointer, and
the human's choice is just a state update before resuming.

## 3. The UI loop (Gradio, W9 style)

```python
def on_choice(pick: str):
    graph.update_state(CONFIG, {"chosen": pick})
    graph.invoke(None, CONFIG)                # advance to next pause
    return render_current(CONFIG)             # chapters + options
```

| UI event | Graph call |
|---|---|
| new story | `invoke(inputs, config)` |
| option clicked | `update_state` + `invoke(None, config)` |
| refresh | `get_state(config)` → render |

The UI never holds story state — the checkpointer does. A browser
refresh, a different device, a crashed server: same thread_id, same
story.

## 5. The pause/resume test suite (the pattern's contract)

```python
def test_pauses_before_apply():
    graph.invoke({"premise": P}, CONFIG)
    assert graph.get_state(CONFIG).next == ("apply",)

def test_resume_needs_choice():
    graph.invoke(None, CONFIG)                       # no choice set
    snap = graph.get_state(CONFIG)
    assert snap.next == ("apply",)                   # still paused? no:
    # it advanced with empty choice — the bug this test documents.
    # fix: the apply node re-prompts when chosen is empty (file 03).

def test_choice_recorded():
    graph.update_state(CONFIG, {"chosen": "follow the whale song"})
    graph.invoke(None, CONFIG)
    assert any("whale" in c for c in graph.get_state(CONFIG)["chapters"])
```

The suite is the WAIT pattern's contract in three tests: pause position,
choice necessity, choice effect. The middle test documents the *empty-
choice resume* bug class — resuming without a decision either loops or
guesses, and the test is where you decide which.

## Exercises

1. Run the story graph to the first pause; inspect `get_state`; verify
   `next == ("apply",)` and options are populated.
2. Resume drill: apply a choice; verify chapter 2 reflects it; repeat
   across 3 chapters.
3. Crash drill: kill the process mid-story; restart; resume from the
   same thread_id — durability, proven.
4. Suite drill: implement §5's three tests; make the middle one pass by
   fixing apply's empty-choice handling (re-prompt, once).

## Pitfalls

- Interrupts without a checkpointer — the pause has nowhere to live;
  the two are a pair.
- Resuming with `invoke(None)` *without* updating `chosen` — the apply
  node reads the stale option; update-then-resume is the contract.
- UI state kept in the browser — the thread_id is the story's identity;
  server-side, always.