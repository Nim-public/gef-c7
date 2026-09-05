# Deep-Dive: Capstone Task — The Agno Data Agent

Parent overview: [`../05-capstone-task-phidata-agent.md`](../05-capstone-task-phidata-agent.md)

The capstone task: assemble the Agno agent (toolkits + knowledge), run
15 data-intensive cases, ground every number with verification nodes,
and compare against the W11 SDK implementation.

## File map

| File | What it covers |
|---|---|
| [`01-agno-assembly.md`](01-agno-assembly.md) | Toolkits + knowledge in one agent |
| [`02-eval-cases.md`](02-eval-cases.md) | 15 data-intensive cases with gold answers |
| [`03-verification-nodes.md`](03-verification-nodes.md) | Numeric grounding in the loop |
| [`04-comparison-vs-w11.md`](04-comparison-vs-w11.md) | Same-case tables |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-agno-assembly.md` — the W12 components in one agent.
2. `02-eval-cases.md` — 15 cases, gold answers, before running.
3. `03-verification-nodes.md` — numbers verified, not trusted.
4. `04-comparison-vs-w11.md` — the final framework evidence.

## Prerequisites

- [`../03-custom-tools-toolkits/`](../03-custom-tools-toolkits/) and
  [`../04-analytics-agent-financial/`](../04-analytics-agent-financial/)
  (W12 branch) — the toolkits and defenses.
- The LangGraph foundations (this week) — the verification nodes.