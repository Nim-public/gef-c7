# Supervisor Topology — Routing Workers

**What you'll learn:** the supervisor pattern: one router node, several
worker nodes, conditional edges back to the supervisor — the W11
handoff topology, graph-native, with the routing state made visible.

## 1. The topology

```python
builder = StateGraph(TeamState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", researcher_node)
builder.add_node("analyst", analyst_node)
builder.add_node("writer", writer_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_to_worker,
                              {"researcher": "researcher",
                               "analyst": "analyst",
                               "writer": "writer",
                               "done": END})
for w in ("researcher", "analyst", "writer"):
    builder.add_edge(w, "supervisor")       # workers report back
```

The supervisor decides; workers execute and return; the supervisor
decides again. The cycle is bounded exactly like file 01's repair loop
(`turns < max`) — same bound, more workers.

## 2. The supervisor node

```python
def supervisor_node(state: TeamState) -> dict:
    if state["turns"] == 0:
        return {"next": "researcher", "turns": 1}
    if state["research_done"] and not state["analysis_done"]:
        return {"next": "analyst", "turns": state["turns"] + 1}
    if state["analysis_done"] and not state["report"]:
        return {"next": "writer", "turns": state["turns"] + 1}
    return {"next": "done", "turns": state["turns"] + 1}
```

| Supervisor style | Mechanism | Trade |
|---|---|---|
| rule-based (above) | deterministic, testable | needs you to know the plan |
| LLM supervisor | model reads state, picks worker | flexible, costlier, less predictable |

Start rule-based (your W9 router's descendant); promote to LLM-driven
only where the plan is genuinely unknown — the boundary rule, per
*decision* now.

## 3. Worker state discipline

Each worker returns partial state; the supervisor reads only the fields
it needs:

| Worker | Returns | Supervisor reads |
|---|---|---|
| researcher | `research_notes`, `sources` | `research_done` flag |
| analyst | `analysis`, `numbers` | `analysis_done` |
| writer | `report` | `report` |

The W11 state-passing rules apply: context carries infrastructure, typed
outputs cross boundaries, summaries compress. The graph state is the
shared blackboard — reducers decide what accumulates.

## 4. Supervisor vs handoffs vs chains (the topology menu)

| Need | Pattern | W-week |
|---|---|---|
| fixed order | chain / sequential crew | W11/W12 |
| dynamic order, one speaker | handoffs | W11 |
| dynamic order, shared state | supervisor graph | this file |
| parallel fan-out | `Send` map-reduce | W13 file 01 |

Same menu, fourth entry. The supervisor's distinctive feature is the
*shared blackboard* — workers see accumulated state, not just their
inputs.

## Exercises

1. Build the supervisor topology; run a research→analyze→write task;
   verify the turn sequence from the trace.
2. Rule-vs-LLM drill: swap the rule supervisor for an LLM supervisor on
   5 tasks; compare plan quality, tokens, and determinism.
3. Bounded drill: set the turn cap at 6; force a task that needs 8;
   verify honest degradation — the bound holds under pressure.

## Pitfalls

- LLM supervisors on known pipelines — the rule version is cheaper and
  testable; promote per decision, not per vibe.
- Workers that read each other's raw outputs — the blackboard is typed;
  cross-reading is the coupling anti-pattern.
- Supervisor loops without the turn cap — the W10 spiral, team edition;
  the bound is structural.