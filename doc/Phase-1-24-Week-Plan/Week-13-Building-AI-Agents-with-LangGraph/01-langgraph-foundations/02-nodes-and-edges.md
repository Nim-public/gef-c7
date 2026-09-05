# Nodes and Edges — Normal and Conditional Wiring

**What you'll learn:** the graph as wiring: nodes as functions, normal
edges as fixed paths, conditional edges as the routing layer — your W9
router and W10 loop, expressed as edges.

## 1. The minimal graph

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(GraphState)
builder.add_node("retrieve", retrieve)
builder.add_node("answer", answer)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)

graph = builder.compile()
result = graph.invoke({"query": "Which chart shows Q3 margin?"})
```

Four objects: `START`, nodes, edges, `END`. The W9 hot path
(route→retrieve→generate) as three edges — deterministic, auditable,
exactly the pipeline your boundary memo prescribed.

## 2. Conditional edges — the router as a function

```python
def route(state: GraphState) -> str:
    if state["query_class"] == "charts":
        return "chart_node"
    if state["query_class"] == "exact":
        return "fts_node"
    return "answer"

builder.add_conditional_edges("classify", route,
                              {"chart_node": "chart_node",
                               "fts_node": "fts_node",
                               "answer": "answer"})
```

| W9/W10 construct | LangGraph construct |
|---|---|
| regex router (W9-05) | conditional edge function |
| agent loop | cycle: agent → tools → agent (file 03) |
| HITL gate | interrupt (file 06) |
| two-pass encoding | two nodes + edge |

The routing function is *your code* — deterministic, testable, the
regex router's natural home. Where the model should choose, the node
returns the choice in state and the edge reads it — control flow in
state, exactly W10's transfer, now inspectable.

## 3. Fan-out with Send (map-reduce)

```python
from langgraph.types import Send

def fan_out(state: GraphState):
    return [Send("process_unit", {"unit_id": u})
            for u in state["retrieved"]]

builder.add_conditional_edges("retrieve", fan_out, ["process_unit"])
```

`Send` fans one state into n parallel node invocations — batch unit
processing, per-crop OCR, anything embarrassingly parallel. The reducer
(`operator.add`) collects the results — the map-reduce pair your
Week-07 batch encode could have used.

## 4. Wiring discipline (the graph review checklist)

```text
[ ] every node returns partial state (never the whole dict)
[ ] every conditional edge's mapping covers all return values
[ ] cycles have a counter field and an exit edge (file 03)
[ ] START/END explicit; no orphan nodes
[ ] the diagram in the README matches builder code (one source: code)
```

## 5. The graph review checklist, applied to your W9 path

```text
[ ] START → classify → route → nodes → END   (no orphan nodes)
[ ] classify returns partial state           (never the whole dict)
[ ] route's mapping dict covers every class  (exhaustiveness)
[ ] node names match the README diagram      (review them together)
[ ] every edge has an owner (why does this edge exist?)
```

The checklist is the graph review's rubric — the same four gates as the
W10 pipeline review (contract, quarantine, determinism, settings) but
addressing *wiring* instead of transforms. The last item is the one that
rots: diagrams drift from code unless they are reviewed together, so
generate the diagram from the builder or read them side by side.

## Exercises

1. Wire the W9 hot path as a graph; run 5 queries; verify identical
   outcomes and node sequences vs the W9 function chain.
2. Conditional drill: implement `route`; table-test it (10 inputs →
   expected nodes) — the router, now a pure function with a truth table.
3. Send drill: fan out 12 units through `process_unit`; verify the
   reducer's order and the parallel speedup.

## Pitfalls

- Nodes returning full state — the reducers then double-apply; return
  partials.
- Unmapped conditional returns — runtime errors that a table-test would
  have caught at write time.
- Graph code drifting from the README diagram — generate or review
  together; drift is how dead edges survive.