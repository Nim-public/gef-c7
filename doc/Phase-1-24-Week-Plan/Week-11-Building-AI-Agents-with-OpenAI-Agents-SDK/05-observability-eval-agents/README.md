# Deep-Dive: Observability & Eval for Agents

Parent overview: [`../05-observability-eval-agents.md`](../05-observability-eval-agents.md)

This subfolder turns the SDK's traces into your harness: the trace/span
model, replay debugging for failed runs, the export merge into your W10
trajectory store, and regression suites with trajectory assertions.

## File map

| File | What it covers |
|---|---|
| [`01-trace-span-model.md`](01-trace-span-model.md) | Generation / tool / handoff / guardrail spans |
| [`02-replay-debugging.md`](02-replay-debugging.md) | Failed-run root-cause workflow |
| [`03-export-to-harness.md`](03-export-to-harness.md) | Merged W10-04 + trace rows |
| [`04-regression-suites.md`](04-regression-suites.md) | Trajectory assertions in CI |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-trace-span-model.md` — the data model for everything below.
2. `02-replay-debugging.md` — root-cause a planted failure.
3. `03-export-to-harness.md` — one store, two capture paths.
4. `04-regression-suites.md` — the baseline gate, trajectory edition.

## Prerequisites

- [`../01-agents-sdk-quickstart/05-tracing.md`](../01-agents-sdk-quickstart/05-tracing.md)
  — the trace model and local export.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/)
  — the harness and scorecards this extends.
