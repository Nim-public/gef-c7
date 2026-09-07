# Interrupts — interrupt_before, Approval Design, Resumes

**What you'll learn:** the HITL gate, graph-native: `interrupt_before`
pauses before a node, the resume contract, and the approval design that
makes human review a *state transition* instead of a hack.

## 1. The mechanics

```python
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["send_email", "ingest_units"],   # the gated nodes
)

config = {"configurable": {"thread_id": "task-3"}}
graph.invoke(inputs, config)                  # runs until the gate
snap = graph.get_state(config)
assert snap.next == ("send_email",)           # paused exactly there

# human approves:
graph.invoke(None, config)                    # resume, no new input

# human rejects:
graph.update_state(config, {"approved": False})
graph.invoke(None, config)                    # continues with the edit
```

The W10 HITL gate (`needs_gate` → `gate_payload` → `human_decide`)
becomes three primitives: the interrupt list (which nodes gate), the
state update (the decision), and the resume (continuation). Same policy
table, structural enforcement.

## 2. Approval design (what the human sees and does)

| Decision | State effect | Resume call |
|---|---|---|
| approve | nothing (state as proposed) | `invoke(None, config)` |
| edit | `update_state` with corrections | `invoke(None, config)` |
| reject | `update_state` with a rejection marker + reason | route elsewhere |

```python
def apply_approval(decision) -> dict:
    if decision.kind == "approve":
        return {}
    if decision.kind == "edit":
        return {"proposed_response": decision.edited}
    return {"rejected": True, "reject_reason": decision.reason}
```

The three-decision model from W10 file 04 carries over exactly —
approve/edit/reject — with the edit *as a state update* rather than a
side-channel. The reject reason lands in the trajectory store, feeding
the W10 reject-reason mining loop.

## 3. Where interrupts belong (the gate policy, graph edition)

| Node | Gate? | Rationale |
|---|---|---|
| retrieval/search | no | read-only, cheap |
| answer generation | sampled | spot-check policy |
| send_email / ingest / delete | always | blast radius (W10 triage table) |
| spend over threshold | always | cost consent |

The W10 `GATE_POLICY` maps 1:1 to the interrupt list — read-only nodes
run free; the blast-radius nodes gate. The policy stays a committed
artifact; the interrupt list is its graph projection.

## 4. Resumes and the state contract

The resume (`invoke(None, config)`) continues from the *interrupted
node* with the state as updated. Rules:

1. **Update before resume** — the decision must be in state when the
   gated node runs.
2. **`None` means continue** — passing new inputs starts a *new* run
   (a different thing entirely).
3. **One gate, one decision** — re-interrupting on the same node without
   state change is a policy bug, not a feature.

## 5. The interrupt inventory (the gate policy, rendered)

| Gated node | Decision model | Resume action | Battery case |
|---|---|---|---|
| `send_email` | approve/edit/reject | 3-branch | send blocked without approval |
| `ingest_units` | approve/edit | 2-branch | ingestion needs human sign-off |
| `answer` (sampled) | spot-check | sampled by run_id | the W12 sampled gate |
| search/retrieve | never | — | read-only, zero gates |

The inventory is the W10 `GATE_POLICY` rendered as the interrupt list —
and the battery asserts the *invariant*: no gated node executes without
a state change. The last row is as important as the first: zero-gate
read-only paths prove the policy is not blanket paranoia.

## Exercises

1. Wire `interrupt_before` on the two gated nodes; run the three
   decisions (approve/edit/reject) through the resume contract; verify
   no advance without a decision (the invariant test).
2. Inventory drill: render §5 from your `GATE_POLICY`; every gated node
   has a battery case; every read-only node has a zero-gate test.
3. Resume-mistake drill: resume with new inputs (the classic error);
   observe the new-run behavior; add the guard (assert pending interrupt
   before resume).