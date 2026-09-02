# 01 — LangGraph Foundations: States, Nodes, Edges

> Week 13 index: [README.md](README.md)

**Session 1 topics:** *What is LangGraph. Building Blocks: States, Nodes, Edges in LangGraph.*

---

## What you'll learn

- Why an explicit graph: control flow as a *reviewable artifact* (vs W11's implicit loop)
- The three building blocks — State, Nodes, Edges — with reducers
- Conditional edges and the START/END lifecycle
- Compile, invoke, stream; reading a graph trace

## 1. What LangGraph is (and what it fixes)

LangGraph is a low-level orchestration framework: you define a **state machine** whose nodes are functions (LLM calls, tools, logic) and whose edges — including *conditional* ones — encode the control flow. Compare:

| | W11 SDK | LangGraph |
|---|---|---|
| control flow | implicit (the model's tool/handoff choices) | **explicit** (edges you wrote) |
| state | session/history + context | a typed `State` object every node reads/writes |
| loops | model-driven (max_turns) | cycles you draw (with exit conditions) |
| pause/resume | manual | **checkpoints + interrupts** built in |
| debugging | traces | graph trace + *time travel* (file 06) |

The W11-03 anti-patterns (ping-pong, manager spirals) are exactly what explicit graphs make *visible and preventable* — the loop is on the diagram, bounded by an edge condition you can point to.

## 2. The State — shared, typed, reducer-composed

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    question: str
    documents: list[str]                 # retrieved chunks
    answer: str
    messages: Annotated[list, add_messages]   # reducer: append, don't overwrite
```

- Every node receives the state, returns a **partial update** (only the keys it touched)
- `Annotated[list, add_messages]` = a **reducer**: instead of replacing `messages`, each node appends — the same append-vs-replace discipline as W1-07's history, declared in the type
- Pydantic models work too (validation in the state itself)

## 3. Nodes — functions over state

A node is any callable: `(state) -> partial state`.

```python
def retrieve(state: GraphState):
    hits = search_knowledge(state["question"], k=5)      # W9-05 contract
    return {"documents": [h["text"] for h in hits["hits"]]}

def generate(state: GraphState):
    context = "\n\n".join(state["documents"])
    resp = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "system", "content": "Answer ONLY from context; cite [doc:id]."},
                  {"role": "user", "content": f"{context}\n\nQ: {state['question']}"}])
    return {"answer": resp.choices[0].message.content}
```

Your W9 retrieval function and W4-01 prompt slot in unchanged — LangGraph orchestrates; your capstone components execute.

## 4. Edges — normal and conditional

```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade", grade_documents)     # LLM grades chunk relevance (W5-03 idea)
workflow.add_node("rewrite", rewrite_query)     # fallback arm
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges(
    "grade",
    decide_route,                               # state -> next node name
    {"rewrite": "rewrite", "generate": "generate"},
)
workflow.add_edge("rewrite", "retrieve")        # the loop back
workflow.add_conditional_edges(
    "generate",
    grade_generation,                           # grounded? useful?
    {"useful": END, "not supported": "generate", "not useful": "rewrite"},
)

app = workflow.compile()
```

The conditional function reads state, returns a key into the mapping dict — **the branching logic is a reviewed function**, not a model whim. This is Self-RAG's shape (the docs' canonical example): retrieve → grade → (rewrite→retrieve) or generate → grade → done/loop. Note the two loops (rewrite cycle, regenerate cycle) — each has an *exit condition you wrote*, the anti-pattern fix W11-03 promised.

## 5. Invoke, stream, inspect

```python
result = app.invoke({"question": "What is the refund timeline?"})
print(result["answer"])

for event in app.stream({"question": "What is the refund timeline?"}):
    for node, update in event.items():          # node-level streaming
        print(f"--- {node} ---")
        print(update)
```

`stream()` yields per-node updates — the observable execution path (your W10-04 trace habit, native here). LangSmith integration adds full span traces if configured (W14 uses the LangChain stack).

## 6. The graph vs your week-10 loop (the mapping, completed)

| W10 hand-rolled | LangGraph |
|---|---|
| `for step in range(max_steps)` | cycles + edge conditions (visible) |
| FINAL: termination convention | `END` edge |
| scratchpad tools (W10-02) | state fields |
| forced-decision nudge | a node whose edge condition forces a route |
| JSONL trace | built-in graph trace + checkpoints (file 06) |

## Exercises

1. Build the 4-node Self-RAG-style graph above over your W9 retriever; run 5 questions; print the node path each took (`stream()`).
2. Deliberately break the retriever (empty results); watch the `grade → rewrite → retrieve` loop fire. Add a max-retries counter to the state — the fix for unbounded cycles.
3. Convert W10-01's loop into a graph: nodes `plan → act → observe → decide`, conditional edge back to `act`. Compare LOC and readability with the hand-rolled version.
4. Reducer experiment: two nodes appending to `messages` without `add_messages` — what does the second node's write do to the first's? (The reducer's reason for existing.)
5. Draw your capstone's *ideal* graph (nodes/edges/conditions) on paper — include one human-interrupt node. Bring it to file 03/06.

## Pitfalls

- **Unbounded cycles** — every loop-back edge needs an exit condition in state (retry counters, grades)
- **State fields overwritten accidentally** — without reducers, parallel/adjacent nodes clobber each other's writes
- **Conditional function raising** — edge functions must handle missing keys (first invocation has a partial state)
- **God-state** — 30 fields nobody reads; state is an API, design it like one (W10-02's memory discipline)
- **Compiling with stale imports** — nodes are bound at `compile()`; edit-then-forget-restart is a classic notebook bug

## Resources

- [LangGraph docs](https://langchain-ai.github.io/langgraph/) — concepts (graphs, state, nodes/edges) + how-tos
- LangChain blog, *Self-RAG with LangGraph* — the canonical conditional-edges example (source of §4's shape)
- LangGraph [persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/) — preview of file 06
- W11-03 — the implicit-graph patterns this file makes explicit
