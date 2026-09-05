# KB & Data Nodes — W9/W6 Capstone Integration

**What you'll learn:** the resolution side of the router: a knowledge
node (your W9 hybrid stack) and a data node (your W6/W12 SQL tools),
wired as graph nodes with their guards intact.

## 1. The knowledge node

```python
def kb_node(state: RouterState) -> dict:
    hits = hybrid_retrieve(state["ticket"], k=5)
    if not hits:
        return {"resolution": "No knowledge found — escalate to human.",
                "escalated": True}
    ctx = "\n".join(f"[{h.unit_id}] {h.text[:300]}" for h in hits)
    answer = llm_answer(state["ticket"], ctx)
    return {"resolution": answer,
            "citations": [h.unit_id for h in hits]}
```

The 0-hit branch *escalates* — the W10 refusal path as a graph edge.
The knowledge node inherits every W9 guard: citations required, gaps
stated, and the insufficiency battery applies unchanged.

## 2. The data node (guarded SQL, graph edition)

```python
def data_node(state: RouterState) -> dict:
    sql = llm_compose_sql(state["ticket"], schema=SCHEMA_DDL)
    if blocked := validate_sql(sql, ALLOWED_TABLES):
        return {"resolution": blocked, "citations": []}   # instructive refusal
    rows = run_sql(sql)
    return {"resolution": summarize_rows(rows, sql),
            "sql_used": [sql]}
```

The W12-02 validator runs inside the node — same guardrails, same
instructive refusals, now addressable as a graph node the router can
choose (or not).

## 3. Node wiring with the dual-pipeline routing

```python
builder.add_conditional_edges(
    "classify", route, {
        "escalate": "escalate_node",
        "human_review": "human_node",
        "kb": "kb_node",
        "data": "data_node",
    })
```

| Classification | Node | Guards inherited |
|---|---|---|
| how-to / conceptual | kb_node | citations, 0-hit escalation |
| account/numeric | data_node | SQL validator, row limits |
| urgency 5 | escalate | (before both) |
| low confidence | human | — |

The W9 pattern-selection table has become graph topology — the route
*is* an edge, and the guards ride with their nodes.

## 4. The integration battery

| Case | Path | Assert |
|---|---|---|
| "how do I export?" | kb | citation present |
| "what's my account balance?" | data | `sql_used` present, no write |
| "system is down entirely" | escalate | edge from trace |
| "how do I export?" (0 hits variant) | kb → escalate | 0-hit branch fires |

The battery runs the *paths*, not just endpoints — each case asserts the
node sequence from the trace, which is the graph's whole advantage.

## 5. The resolution-node test matrix

| Node | Drill | Assert |
|---|---|---|
| kb (hit) | known-answer query | citation present |
| kb (0-hit) | empty the KB for one query | escalation message |
| data (valid) | numeric question | `sql_used`, no writes |
| data (blocked) | write attempt | instructive refusal, verbatim |

The matrix runs after any node change — it is the integration battery
from §4, formalized as the node's contract test. The kb/data parity
rows re-run the W12 validators verbatim: same hints, same refusals,
different transport.

## 6. The router graph review (the wiring sign-off)

```text
[ ] classify → route → {escalate, human, kb, data}  (complete mapping)
[ ] kb 0-hit edge → escalate                         (no silent empty answers)
[ ] data node validator = W12 validator (verbatim)
[ ] escalation precedes both resolution branches
[ ] node names match the architecture diagram
```

The sign-off is the graph review checklist (file 01-02) applied to the
router — five rows, each asserting a property from this file. It is the
last gate before the router serves tickets.

## Exercises

1. Wire both nodes; run the four integration cases; assert node
   sequences from the trace.
2. Guard-parity drill: the data node's refusals must match the W12 SQL
   battery verbatim — same validator, same hints.
3. 0-hit drill: empty the KB for one query; the kb node escalates with
   the honest message — the W10 refusal path, graph edition.
4. Matrix drill: run the §5 matrix; every drill's assertion green; the
   matrix itself committed next to the node code.
5. Sign-off drill: run the §6 checklist against the final wiring; every
   row cites the test that proved it.

## Pitfalls

- KB node without the 0-hit escalation — "No knowledge found" as a user
  answer is the silent failure; escalate instead.
- Data node bypassing the validator — same rule as W12: the tool (node)
  enforces; the graph is just wiring.
- Guards reimplemented per node — import the W12 validators; one
  contract, two callers.