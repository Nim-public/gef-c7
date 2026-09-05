# Deep-Dive: Reliability — Limits, Retries, Tests

Parent overview: [`../01-reliability-limits-retries-tests.md`](../01-reliability-limits-retries-tests.md)

Production hardening, part 1: the RunBudget (turns/tokens/time/spend),
tenacity retry policies, exception→message contracts, and the test
pyramid from stubbed units to soak tests.

API verified against context7 id `/jd/tenacity`.

## File map

| File | What it covers |
|---|---|
| [`01-run-budget.md`](01-run-budget.md) | Turns/tokens/time/spend aborts |
| [`02-retry-policies.md`](02-retry-policies.md) | Tenacity backoff, budgets, circuit breakers |
| [`03-user-contracts.md`](03-user-contracts.md) | Exception→message handler maps |
| [`04-test-pyramid.md`](04-test-pyramid.md) | Stubbed unit → contract → integration → soak |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-run-budget.md` — the abort rails.
2. `02-retry-policies.md` — tenacity with policies.
3. `03-user-contracts.md` — failures users can read.
4. `04-test-pyramid.md` — the four tiers, budgeted.

## Prerequisites

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/`](../../Week-10-Introduction-to-Agentic-AI-MCP/01-agents-foundations/)
  — the episode budget this hardens.
- [`../04-prompt-caching-and-routing/`](../04-prompt-caching-and-routing/)
  — the cost side of the budget.