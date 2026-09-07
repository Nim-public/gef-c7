# Deep-Dive: Project — Support Ticket Router

Parent overview: [`../03-project-support-ticket-router.md`](../03-project-support-ticket-router.md)

The ticket router is the classification graph: a structured-output
classification node, urgency-gated escalation edges, knowledge and data
nodes wired from your capstone stacks, and the three-way router
comparison (rules / handoffs / graph).

## File map

| File | What it covers |
|---|---|
| [`01-classification-node.md`](01-classification-node.md) | Structured outputs, reasoning |
| [`02-escalation-edges.md`](02-escalation-edges.md) | Urgency gating first |
| [`03-kb-data-nodes.md`](03-kb-data-nodes.md) | W9/W6 capstone integration |
| [`04-router-comparison.md`](04-router-comparison.md) | Rules vs handoffs vs graph |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-classification-node.md` — classify with structure and reasons.
2. `02-escalation-edges.md` — gate the dangerous path first.
3. `03-kb-data-nodes.md` — wire your existing stacks in.
4. `04-router-comparison.md` — three implementations, one eval set.

## Prerequisites

- [`../01-langgraph-foundations/`](../01-langgraph-foundations/) — state,
  conditional edges.
- [`../02-knowledge-and-databases/04-dual-pipeline.md`](../02-knowledge-and-databases/04-dual-pipeline.md)
  (W12) — the knowledge/SQL nodes.
