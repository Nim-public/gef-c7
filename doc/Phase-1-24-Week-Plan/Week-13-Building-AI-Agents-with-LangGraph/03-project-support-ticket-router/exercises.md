# Exercises — Support Ticket Router

Expanded set with worked approaches. The deliverable: the classification
node with gated escalation, both resolution nodes wired from your
existing stacks, and the three-way comparison table.

## 1. Classification node (from 01-classification-node)

**Task:** build the typed classification (category/urgency/reason/
confidence); run 10 tickets; hand-check 5 reasons; sweep the confidence
gate and pick the knee.

**Worked approach:** the reason-quality hand-check is the eval's teeth —
"technical because technical" is a guess dressed as a reason. The
threshold sweep finds *your* knee; record it with the accuracy curve.

**Pass criterion:** 5/5 reasons legible; the gate threshold chosen from
the accuracy curve, recorded.

## 2. Escalation first (from 02-escalation-edges)

**Task:** wire the three-way route with escalation first; run the four
escalation-battery cases; assert edges from traces; then the
order-swap drill.

**Worked approach:** the order-swap drill proves the ordering *is* the
property — a confidently-resolved escalation ticket is the failure the
order prevents. Restore and re-green.

**Pass criterion:** 4/4 battery edges correct; the swapped-order case
documented as the reason for the ordering.

## 3. Resolution nodes (from 03-kb-data-nodes)

**Task:** wire kb_node (with 0-hit escalation) and data_node (with the
W12 validator); run the integration battery (4 paths); assert node
sequences.

**Worked approach:** the guard-parity check (validator hints verbatim)
is the reuse proof — the W12 contracts survive as node-internal code.

**Pass criterion:** 4/4 path assertions; validator hints verbatim; the
0-hit escalation message honest.

## 4. Three-way comparison (from 04-router-comparison)

**Task:** run the 25-ticket eval through all three implementations;
fill the comparison table; write the router decision with cited rows.

**Worked approach:** the protocol header (same prompts, same corpus,
same eval set) is what makes three columns comparable — one variable
(the routing mechanism) changes per column.

**Pass criterion:** the table committed; the verdict cites accuracy,
cost, and auditability rows.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Typed classification + legible reasons | node + hand-check | 3 |
| Escalation ordering proven by order-swap | drill | 4 |
| Resolution nodes with guard parity | integration battery | 4 |
| Three-way comparison table + verdict | comparison report | 4 |
| Confidence threshold from measured knee | sweep table | 2 |

**Pass bar:** 14/18 to proceed to file 04 (the codegen loop). The
comparison (4-pointer) closes the three-week routing arc — W9 rules, W11
handoffs, W13 graph, one table.

## Pitfalls recap

- Reasons that restate categories — the hand-check rejects them; the
  judge samples enforce it.
- Escalation after confidence — the order swap drill is the proof this
  matters.
- Node-local reimplementations of guards — import the W12 validators;
  one contract, many callers.