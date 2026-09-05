# Three-Way Router Comparison — Rules, Handoffs, Graph

**What you'll learn:** the same ticket router implemented three ways —
W9 regex rules, W11 handoffs, W13 graph — compared on accuracy, latency,
cost, and auditability, with the honest verdict for your capstone.

## 1. The three implementations

| Implementation | Routing mechanism | W-week |
|---|---|---|
| Rules | regex on ticket text → pipeline | W9-05 |
| Handoffs | model calls `transfer_to_X` | W11-02 |
| Graph | conditional edge from classified state | this file |

All three share: the same classification prompt, the same KB/data
nodes, the same escalation policy. The *only* variable is the routing
mechanism — the comparison protocol (W11 file 06-02) applies.

## 2. The comparison table

| Metric | Rules | Handoffs | Graph |
|---|---|---|---|
| route accuracy (25 tickets) | 0.77 | 0.87 | 0.90 |
| p50 latency | 2.0 s | 2.4 s | 2.1 s |
| tokens p50 | 3.1k | 3.6k | 3.3k |
| escalation correctness | 1.00 | 1.00 | 1.00 |
| auditability of the route | code-readable | trace | trace + state |
| change cost (new class) | edit regex | edit description | edit enum + edge |

Fill with your numbers. The expected shape: graph ≈ handoffs on
accuracy, graph slightly cheaper (the classification turn does both
jobs), rules cheapest and weakest on ambiguity.

## 3. What each mechanism is actually for

| Mechanism | Best at | Fails at |
|---|---|---|
| rules | rigid, high-volume, known classes | ambiguity, drift |
| handoffs | conversational transfer, ownership | precision routing |
| graph | stateful multi-step, auditable paths | simple one-liners (overkill) |

The verdict pattern from the W11/W12 comparison tables repeats: the
mechanism is chosen per *system shape*, not per leaderboard. Your
boundary memo (W10 file 04) already said this at the agent level; this
table says it at the router level.

## 4. The auditability row deserves its own paragraph

Rules: the route is `if "invoice" in text` — readable by anyone, but
blind to meaning. Handoffs: the route is a model decision in a trace —
powerful but post-hoc. Graph: the route is *state* — the classification
(reason included) sits in the state before the edge fires, so the route
and its justification are the same artifact. For the capstone's
review-gated flows, that last property is the graph's genuine edge.

## Exercises

1. Implement the handoffs version of the router (one afternoon); run the
   same 25-ticket eval; fill the table's third column.
2. Cost drill: compute tokens/latency per implementation from the merged
   store; the classification-turn sharing is the graph's saving — verify.
3. Verdict drill: write the router decision into the boundary memo
   citing accuracy, cost, and auditability rows.

## Pitfalls

- Comparing with different classification prompts per implementation —
  the prompt is shared; only the routing varies.
- Graph chosen for a 2-class router — overkill; rules were fine and
  cheaper (the honest table says so).
- Auditability claimed without traces — the property needs the merged
  store (W11 file 05-03) to be real.