# Deep-Dive: Tracing, Guardrails & LangSmith

Parent overview: [`../02-tracing-guardrails-langsmith.md`](../02-tracing-guardrails-langsmith.md)

The hosted observability layer: LangSmith setup and projects, hosted
dataset/evaluation runs, platform guardrails (moderation/PII), and trace
hygiene — PII scrubbing, retention, sampling.

## File map

| File | What it covers |
|---|---|
| [`01-langsmith-setup.md`](01-langsmith-setup.md) | Automatic tracing, projects |
| [`02-datasets-evaluations.md`](02-datasets-evaluations.md) | Hosted regression runs |
| [`03-platform-guardrails.md`](03-platform-guardrails.md) | Moderation/PII layering |
| [`04-trace-hygiene.md`](04-trace-hygiene.md) | PII scrubbing, retention, sampling |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-langsmith-setup.md` — the tracing switch and projects.
2. `02-datasets-evaluations.md` — hosted eval runs alongside your harness.
3. `03-platform-guardrails.md` — the moderation/PII layer.
4. `04-trace-hygiene.md` — what leaves your machine, and when.

## Prerequisites

- [`../01-reliability-limits-retries-tests/`](../01-reliability-limits-retries-tests/)
  — the budget and pyramid this observability serves.
- [`../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/05-tracing.md`](../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/05-tracing.md)
  — the trace model and hygiene rules.