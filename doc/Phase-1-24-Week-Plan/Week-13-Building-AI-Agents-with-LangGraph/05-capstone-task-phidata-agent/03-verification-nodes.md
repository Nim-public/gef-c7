# Verification Nodes — Numeric Grounding in the Loop

**What you'll learn:** the verification hooks from W12, rebuilt as
*graph nodes*: a verify node that recomputes claims, a sanity node that
annotates results, and the mismatch edge that flags honestly.

## 1. The verify node

```python
def verify_node(state: AgentState) -> dict:
    claim = extract_number(state["draft_answer"])
    independent = independent_sql(state["sql_used"][-1])
    if independent is None:
        return {"caveats": ["verification returned no rows"]}
    if abs(independent - claim) / max(claim, 1) < 0.01:
        return {"verified": True}
    return {"verified": False,
            "caveats": [f"verification mismatch: claim={claim}, "
                        f"independent={independent}"]}
```

| Field | Meaning |
|---|---|
| `verified: True` | an independent query agreed within 1% |
| `verified: False` | mismatch — the caveat is *mandatory* |
| `caveats` | user-visible honesty (W12 file 04) |

The independent query is the design constraint: it must recompute by a
*different path* (different aggregation, different filter order) or it
is the same bug checking itself.

## 2. Wiring verification into the graph

```python
builder.add_edge("answer", "verify")
builder.add_conditional_edges("verify", route_after_verify,
                              {"ok": END, "flag": END, "recompute": "answer"})
```

The route: verified or flagged-caveat → END; *silent* mismatch →
recompute once, then flag. The W12 mismatch drill's rubric, as edges.

## 3. The sanity node

```python
def sanity_node(state: AgentState) -> dict:
    issues = sanity_checks(state["last_rows"], state["verified_col"])
    return {"caveats": state.get("caveats", []) + issues}
```

The W12 sanity checks (missing data, constant columns, unit drift) run
as a node between SQL and verify — annotations accumulate in `caveats`,
and the display contract (W12 file 04-04) relays them to the user.

## 4. The verification battery (graph edition)

| Case | Expected |
|---|---|
| clean number | verified True, no caveats |
| planted query bug | verified False, caveat in user view |
| independent query 0 rows | caveat, claim unsupported |
| chitchat (no numbers) | verify node skipped (routing) |

The battery re-runs the W12 drills as graph-path assertions — node
sequences from the trace are the evidence, same as every W13 battery.

## Exercises

1. Build verify + sanity nodes; wire the three-way route; run the
   battery's four cases.
2. Independence drill: make `verify_number` use the *same* query; the
   mismatch goes undetected — then restore independence and show the
   detection. The independence property, proven by its absence.
3. Display drill: a flagged mismatch must appear in the user view's
   caveats (the W12 rendering contract, now graph-fed).