# Deep-Dive: Measuring Agents & Patterns

Parent overview: [`../04-measuring-agents-patterns.md`](../04-measuring-agents-patterns.md)

This subfolder builds the harness that files 01–03 promised: trajectory
instrumentation from the registry's audit log, the three-dimension metric
set, HITL gate design with measured rates, and a calibrated LLM-as-judge
for trajectories.

## File map

| File | What it covers |
|---|---|
| [`01-trajectory-instrumentation.md`](01-trajectory-instrumentation.md) | Logs, tokens, steps per run — the schema |
| [`02-three-dimension-metrics.md`](02-three-dimension-metrics.md) | Success / efficiency / process |
| [`03-hitl-gates.md`](03-hitl-gates.md) | Approval design and measured rates |
| [`04-llm-as-judge.md`](04-llm-as-judge.md) | Trajectory scoring and calibration |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-trajectory-instrumentation.md` — you cannot measure what you did not log.
2. `02-three-dimension-metrics.md` — three numbers, one table per eval run.
3. `03-hitl-gates.md` — the human in the loop, quantified.
4. `04-llm-as-judge.md` — the judge, calibrated before trusted.

## Prerequisites

- [`../01-agents-foundations/02-hand-rolled-react.md`](../01-agents-foundations/02-hand-rolled-react.md)
  — the trace the harness consumes.
- [`../02-tools-and-memory/02-tool-registry.md`](../02-tools-and-memory/02-tool-registry.md)
  — the audit log feeding it.
- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md)
  — the table discipline extended to trajectories.
