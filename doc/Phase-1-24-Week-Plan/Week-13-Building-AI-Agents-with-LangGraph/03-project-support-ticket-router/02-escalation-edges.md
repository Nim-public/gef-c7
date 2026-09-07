# Escalation Edges — Urgency Gating First

**What you'll learn:** edge ordering as safety ordering: the escalation
edge fires *before* resolution is attempted, so dangerous tickets never
touch the auto-responder.

## 1. The edge order

```python
def route(state: RouterState) -> str:
    if state["classification"]["urgency"] >= 5:
        return "escalate"            # FIRST — before any resolution
    if state["classification"]["confidence"] < 0.7:
        return "human_review"
    return "resolve"

builder.add_conditional_edges("classify", route, {
    "escalate": "escalate_node",
    "human_review": "human_node",
    "resolve": "kb_node",
})
```

| Order | Guarantee |
|---|---|
| urgency → confidence → resolve | blockers never auto-answered |
| confidence → urgency → resolve | a confident "resolved" could ship to a blocked customer — wrong |

The escalation edge must precede the confidence gate *and* the resolve
node: the ordering is the policy. W10 file 04's triage table encoded
this as data; here it is literally the edge order in code.

## 2. The escalation node

```python
def escalate(state: RouterState) -> dict:
    ticket = state["ticket"]
    c = state["classification"]
    return {"escalated": True,
            "resolution": (
                f"ESCALATED (urgency {c['urgency']}). "
                f"Reason: {c['reason']}. Ticket: {ticket[:200]}")}
```

The escalation node does the minimum: mark, summarize, stop. No
knowledge search, no draft answer — a blocked customer gets a human,
not a hallucinated refund policy.

## 3. The escalation battery

| Case | Expected |
|---|---|
| "cannot log in at all" | escalate, urgency 5 |
| "the export button is slow" | resolve, urgency ≤2 |
| "deleted my account by accident" | escalate (data loss) |
| "how do I reset my password?" | resolve, urgency 2 |

The battery's escalation cases are the *opposite* of the resolution
cases — the discriminator is blockage, not punctuation. Each case asserts
the edge taken (from the trace), not just the answer.

## 4. Escalation in the capstone (the mapping)

| Capstone flow | Escalation edge |
|---|---|
| ticket router | human handoff |
| analytics agent | "insufficient data" → analyst |
| corpus QA | "not in corpus" → librarian |

Every grounded agent needs an escalation edge — the honest-failure
route from the W10 trajectories (`refused` outcomes) made structural.
The edge is where your refusal battery's cases *land*.

## Exercises

1. Wire the three-way route with escalation first; table-test `route`
   with 10 state fixtures (all three branches).
2. Battery drill: run the four escalation cases; assert the edge taken
   from the trace; the punctuation-inflation case must NOT escalate.
3. Order drill: deliberately swap the edge order (confidence first);
   construct a ticket that then mis-ships; restore — the ordering is
   the safety property, proven by its violation.

## 6. The escalation SLA (the human side of the edge)

| Metric | Definition | Target |
|---|---|---|
| escalation rate | escalated / total | 5–15% |
| escalation latency | classify → human notified | <60 s |
| resolution SLA | escalated → human answered | per severity |
| bounce rate | escalated → re-auto-routed | 0 (a decision is final) |

The SLA table makes the escalation edge a *measured* commitment: the
rate proves the gate is calibrated, the latency proves the human is
actually notified, and the bounce rule prevents hot-potato routing (an
escalation that the human rejects goes to *review*, never back to auto).

## Exercises (continued)

4. Record drill: escalate one ticket; verify the record contains all
   five fields and lands in the audit trail.
5. SLA drill: measure classification→notification latency on 10 staged
   escalations; the table's targets get your numbers.

## Pitfalls

- Escalation gated behind confidence — a confidently-wrong urgent ticket
  is the worst failure; urgency first, always.
- Escalation nodes that *also* auto-respond — the edge exists to stop;
  the node marks and hands off.
- Battery cases that only check the answer text — assert the *edge*
  from the trace; the path is the safety property.