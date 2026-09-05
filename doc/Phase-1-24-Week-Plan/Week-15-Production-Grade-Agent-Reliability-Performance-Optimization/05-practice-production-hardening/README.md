# Deep-Dive: Practice — Production Hardening

Parent deliverable spec: [`../05-practice-production-hardening.md`](../05-practice-production-hardening.md)

The capstone-week practice: measure the W14-06 baseline, deploy the
reliability layer live, attribute every optimization, and produce the
before/after table — the production week's evidence.

## File map

| File | What it covers |
|---|---|
| [`01-baseline.md`](01-baseline.md) | W14-06 numbers, re-measured |
| [`02-reliability-layer.md`](02-reliability-layer.md) | Budgets/retries/handlers live |
| [`03-optimization-ledger.md`](03-optimization-ledger.md) | Attributed improvements |
| [`04-before-after.md`](04-before-after.md) | p95, $/task, quality — the table |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Build order

1. `01-baseline.md` — the numbers before touching anything.
2. `02-reliability-layer.md` — budgets, retries, handlers deployed.
3. `03-optimization-ledger.md` — every improvement attributed.
4. `04-before-after.md` — the table the rubric grades.

## Prerequisites

- [`../01-reliability-limits-retries-tests/`](../01-reliability-limits-retries-tests/)
  — the layer being deployed.
- [`../02-tracing-guardrails-langsmith/`](../02-tracing-guardrails-langsmith/)
  and [`../03-inference-optimization/`](../03-inference-optimization/) and
  [`../04-prompt-caching-and-routing/`](../04-prompt-caching-and-routing/)
  — the optimizations being attributed.