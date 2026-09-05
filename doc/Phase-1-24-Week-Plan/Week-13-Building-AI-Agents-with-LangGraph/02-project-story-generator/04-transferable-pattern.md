# The Transferable Pattern — Interactive Flows Generally

**What you'll learn:** the story generator's skeleton — generate, WAIT,
apply, repeat — as the template for every human-in-the-loop flow:
approval workflows, guided data entry, triage-with-confirmation.

## 1. The pattern, abstracted

| Story element | Generalized | Other instances |
|---|---|---|
| `generate_chapter` | propose next artifact | draft report, ticket triage |
| `options` | the choice set | approve/edit/escalate |
| `apply_choice` | state update by the choice | commit edit, route ticket |
| world JSON | the durable domain object | project state, customer record |
| interrupt + resume | the pause | every HITL gate (W10 file 04) |

The pattern is: **propose → pause → apply**, with a durable world the
pauses protect. Every W10 HITL gate was this pattern without the
framework support; LangGraph's interrupts make it structural.

## 2. Instance: guided ticket triage

```python
class TicketState(TypedDict):
    ticket: str
    classification: str
    proposed_response: str
    approved: bool

# generate: classify + propose response
# WAIT: human approves (interrupt_before=["apply_response"])
# apply: send response, update ticket record
```

The triage flow is the story flow with different nouns: the model
proposes, the human confirms, the state records. Same graph shape, same
checkpointer, same resume contract — which is why you learned it on a
story (fun) before applying it to work (accountable).

## 3. The pattern's invariants (any instance must hold)

| Invariant | Test |
|---|---|
| state survives process death | crash drill (file 02-02) |
| human choices are recorded (audit) | trajectory row per choice |
| out-of-distribution choices degrade gracefully | fallback ladder |
| the graph never advances past a WAIT without human state | interrupt test |

```python
def test_no_advance_without_choice():
    snap = graph.get_state(CONFIG)
    assert snap.next == ("apply",)          # still paused
    assert snap.values["chosen"] == ""      # nothing chosen yet
```

The invariant test is one assert: *between generate and apply, the graph
waits*. The state machine's honesty, mechanically verified.

## 4. The capstone mapping (your flows)

| Capstone need | Pattern instance |
|---|---|
| answer approval before delivery | propose → WAIT → apply |
| corpus ingestion confirmation | propose units → WAIT → ingest |
| analytics query review | propose SQL → WAIT → run |

Each is one graph, one checkpointer, one UI loop — the story generator's
skeleton with domain nouns. Week 14+ builds the real ones.

## Exercises

1. Abstract the story graph into a reusable `interactive_flow` builder
   (generate_fn, apply_fn, options_fn); rebuild the story with it as the
   smoke test.
2. Invariant drill: write the §3 tests for your builder; run them on the
   story and on one work flow.
3. Mapping drill: list three capstone flows that fit the pattern; pick
   one for Week 14; justify with the boundary memo.

## Pitfalls

- Patterns copied per-project instead of built once — the builder is the
  deliverable; instances are configuration.
- Audit trails skipped in work flows — the story can lose its log; the
  ticket cannot.
- Invariant tests written only for the happy path — the ood-choice
  fallback is the pattern's actual value.