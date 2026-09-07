# Cycles and Bounds — Retry Counters, Exit Conditions

**What you'll learn:** the agent loop as a *bounded cycle*: the agent →
tools edge pair, the counter field, the exit conditions — every W10
budget rule, expressed as graph structure.

## 1. The ReAct cycle

```python
class AgentState(TypedDict):
    query: str
    attempts: int
    retrieved: Annotated[list[str], operator.add]
    answer: str

def agent_node(state: AgentState) -> dict:
    # model decides: more tools, or answer
    return {"attempts": state["attempts"] + 1, ...}

def tools_node(state: AgentState) -> dict: ...

def should_continue(state: AgentState) -> str:
    if state["answer"]:
        return "end"
    if state["attempts"] >= 6:
        return "force_answer"          # the budget stop, as an edge
    return "tools"

builder.add_conditional_edges("agent_node", should_continue,
                              {"tools": "tools_node", "end": END,
                               "force_answer": "force_answer"})
builder.add_edge("tools_node", "agent_node")     # the cycle
```

The loop is *visible*: the `tools_node → agent_node` edge is the cycle;
`attempts` is the bound; `should_continue` is the exit condition. Your
W10 `max_steps` became three inspectable artifacts.

## 2. Bounds: every cycle needs a counter

| Cycle pattern | Bound | Exit edge |
|---|---|---|
| agent↔tools | `attempts < max_steps` | force_answer |
| self-repair (write→test→debug) | `attempts < 4` | report_failures |
| refinement (W11 chaining) | `confidence ≥ 0.8` | accept |
| retrieval retry | `retry_count < 2` | fallback answer |

```python
def bounded_add(left: list, right: list, cap: int = 20) -> list:
    return (left + right)[:cap]
```

The bounded reducer caps *state growth*; the counter caps *iterations*.
Both are the fitter's discipline as graph structure — and both are what
file 06's checkpointing will replay.

## 3. Exit conditions as first-class nodes

```python
def force_answer(state: AgentState) -> dict:
    return {"answer": "I could not complete this within the step budget.",
            "degraded": True}
```

The force-answer node is the degradation ladder's rung, graph-shaped:
a *node*, not a string in the loop. The W10 `degraded` flag becomes a
state field the harness already reads — the regression gate tracks it.

## 4. Cycle debugging (the trace discipline, graph edition)

| Symptom | Graph reading | Fix locus |
|---|---|---|
| attempts hits bound | the tool results aren't leading anywhere | descriptions or task design |
| attempts low, answer empty | exit condition too eager | should_continue logic |
| retrieved grows unboundedly | missing cap reducer | bounded_add |

The W10 detectors (loop rate) run over the graph's `attempts` histogram
— the harness survives, the graph is just a new capture surface.

## 5. The bound table (every cycle in your system, one page)

| Graph | Cycle | Bound | Exit node | Flag |
|---|---|---|---|---|
| ReAct agent | agent↔tools | 6 | force_answer | `degraded` |
| repair loop | write↔test | 4 | report_failures | `degraded` |
| refinement | answer↔critique | 2 | accept current | `confidence<0.8` |
| choice re-prompt | apply↔generate | 2 | open thread | `unresolved` |

The bound table is the cycle inventory from the anti-patterns file
(W11-03), graph edition — one row per loop, each with its exit and its
honesty flag. The harness reads the table: any cycle without a row is
an unbounded loop waiting to happen.

## Exercises

1. Build the ReAct cycle with the three-way exit; run the eval set;
   verify the attempts distribution matches W10's.
2. Bound drill: set `max_steps=2` on task 8; the force-answer edge must
   fire with `degraded=True`; the session stays clean.
3. Cap drill: unbounded-retrieval stress; `bounded_add` caps at 20; the
   trim node drops the oldest — the fitter, as a reducer.
4. Table drill: fill the §5 table for *your* graphs; any cycle missing a
   row gets bounded this session.

## Pitfalls

- Cycles without counter fields — `max_turns` style bounds are graph
  config; the counter in state is the auditable one.
- Exit conditions reading stale fields — reducers decide what
  `should_continue` sees; know your merge order.
- Force-answer nodes that don't flag `degraded` — the harness treats
  unflagged failures as successes; the flag is the contract.