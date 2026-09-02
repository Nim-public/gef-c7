# 01 — Agent Foundations: What They Are, the Loop, First Demo

> Week 10 index: [README.md](README.md)

**Session 1 topics:** *Agents: What are they? What can they do? Some demos.*

---

## What you'll learn

- A precise definition of an agent — and what separates it from a chatbot and a pipeline
- The agent loop (plan → act → observe) implemented with no framework
- What agents can do well, can't do, and shouldn't be used for
- Your first working agent demo: hand-rolled, ~50 lines

## 1. Definition

**Agent = an LLM, in a loop, with tools and memory, working toward a goal.**

```
goal ─► ┌────────────────────────────────────────┐
        │ LLM decides ─► tool call ─► observation│──┐
        │        ▲                               │  │
        │        └────────── loop until done ◄───┘  │
        └────────────────────────────────────────┘
                  memory: history + scratchpad
```

Contrast with everything you've built:

| System | Behavior | Control flow |
|---|---|---|
| Chatbot (W3) | one call per turn | you wrote it |
| RAG pipeline (W4–6) | fixed steps: retrieve → generate | you wrote it |
| **Agent** | *model* chooses which tools, in what order, how many times | **the LLM writes the control flow** |

That last row is the whole idea — and the whole risk. The model deciding control flow buys flexibility (novel question shapes) and costs predictability (W3-05: agents are the *most flexible, least predictable* lever).

## 2. What agents can do (and the honest limits)

**Good fits** — where the *sequence* of steps isn't knowable in advance:

- open-ended questions spanning sources ("compare refund policy with the warranty doc, check ticket 1001's status") → mixed tools, dynamic order
- multi-step tasks with branching (triage → retrieve → compute → reply)
- actions on systems (W13/W14: write tickets, file PRs) with gates

**Bad fits:**

- fixed pipelines (your W4–6 RAG flow is already optimal — an agent wrapper adds latency and failure modes)
- tasks needing guaranteed latency/cost ceilings (the loop is unbounded by default)
- anything where a wrong tool call is irreversible and human review isn't possible

## 3. The loop, hand-rolled (no framework — do this once)

```python
import json
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o-mini"
TOOLS = {                      # name -> python function (the executor)
    "search_knowledge": None,  # filled below — reuse W9-05's contract
    "sql_query": None,
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_knowledge",
        "description": "Search capstone knowledge base (docs+tables). Returns hits with ids, sources, text.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"},
            "k": {"type": "integer", "default": 5}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "sql_query",
        "description": "Run a read-only SELECT against capstone tables. Returns columns+rows.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string"}}, "required": ["question"]}}},
]

SYSTEM = """You are the capstone assistant. Answer ONLY using tools:
- search_knowledge: prose/documents questions
- sql_query: counts, sums, comparisons over tables
Rules: one tool per step; after each result decide 'done' or the next tool.
When you can answer, reply with 'FINAL:' followed by the answer with [id] citations."""

def run_agent(goal: str, max_steps: int = 8) -> str:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": goal}]
    for step in range(max_steps):
        resp = client.chat.completions.create(
            model=MODEL, temperature=0, messages=messages,
            tools=TOOL_SCHEMAS)
        msg = resp.choices[0].message

        if msg.content and msg.content.startswith("FINAL:"):
            return msg.content[len("FINAL:"):].strip()      # terminate

        if not msg.tool_calls:                               # no tool, no final -> force decision
            messages.append({"role": "user", "content":
                             "Use a tool or answer with FINAL:."})
            continue

        messages.append(msg)                                 # assistant's tool call(s)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)       # YOU execute (W10-02)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)[:2000]})
    return "Stopped at max steps."
```

Wire the tools to your real systems — this is the whole capstone seam (W9-05's contract + W6's read-only SQL):

```python
from retrieve import search_knowledge      # W9-05 (pure function, dicts in/out)
from text2sql import answer_structured     # W6-03

TOOLS["search_knowledge"] = search_knowledge
TOOLS["sql_query"] = lambda question: {"sql_answer": answer_structured(question)}

print(run_agent("How many GPU orders did we get, and what does the handbook say about refunds?"))
```

Read that loop against the SDK you'll meet in W11: `Runner.run` *is* this loop (with steps 1–4: invoke → final? → handoff? → tools → repeat), `max_steps` is `max_turns`, and the forced-decision nudge is what frameworks call a "planner prompt".

## 4. Demos that teach the concept

Run these three through the same loop and watch the trajectories:

1. **Single-tool question** — "what does the handbook say about refunds?" → 1 search call, 2 steps. (An agent was overkill — W3-05.)
2. **Multi-tool question** — the GPU+refunds example → search, then sql, then final. (The loop earns its keep.)
3. **Impossible question** — "who won yesterday's match?" → tools return nothing relevant → FINAL "I don't have that information." (The insufficiency escape, now model-driven — verify it, W4-01.)

Log every step (`step, tool, args, latency, tokens`) — file 04 turns these logs into metrics.

## Exercises

1. Run the three demos; log trajectories. Compute steps and tokens per demo.
2. Add a third tool `get_current_date()` and a question "refunds opened in the last 30 days" — watch the agent chain it into `sql_query`.
3. Set `max_steps=2` on the multi-tool demo — what failure mode appears? (This is `MaxTurnsExceeded` in the SDK.)
4. Break tool `search_knowledge` (raise an exception inside). Handle it: catch, feed the error text back as the observation. Does the agent recover?
5. Write the one-paragraph "agent vs pipeline" decision for your capstone: which queries route to `run_agent`, which to the fixed W4 flow, and why.

## Pitfalls

- **Infinite loops** — no max steps, no FINAL-forcing; every agent needs both
- **Unvalidated tool args** — `json.loads` then straight execution; validate against the schema before calling (W10-02)
- **Observations too big** — a 50k-token tool result eats the context budget (W10-05); truncate *before* appending
- **Silent failures** — a tool exception surfacing as an empty string teaches the model nothing; feed errors back explicitly
- **Agent for everything** — the fixed pipeline is faster/cheaper/more testable for known flows (W3-05)

## Resources

- ReAct paper (Yao et al., 2022) — the plan/act/observe loop, §2
- Anthropic, *Building effective agents* — workflows vs agents, the clearest taxonomy
- OpenAI docs, *Function calling* — the schema/message protocol your loop implements
- Lilian Weng, *LLM Powered Autonomous Agents* — planning/memory/tool-use framing
