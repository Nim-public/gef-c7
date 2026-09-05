# Deep-Dive: Synthetic Data

Parent overview: [`../02-synthetic-data.md`](../02-synthetic-data.md)

Synthetic data at scale: seed expansion (paraphrases and variations),
persona grids for coverage, adversarial red-team generation, and the
validation battery (labels, diversity, leakage, distribution) that keeps
synthetic data trustworthy.

## File map

| File | What it covers |
|---|---|
| [`01-seed-expansion.md`](01-seed-expansion.md) | Paraphrase/variation generation |
| [`02-persona-grids.md`](02-persona-grids.md) | Coverage cells and weights |
| [`03-adversarial-generation.md`](03-adversarial-generation.md) | Red-team data at scale |
| [`04-validation.md`](04-validation.md) | Labels, diversity, leakage, distribution |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-seed-expansion.md` — multiply the seeds without multiplying noise.
2. `02-persona-grids.md` — coverage by design, not by accident.
3. `03-adversarial-generation.md` — red-team data at scale.
4. `04-validation.md` — the battery that gates every synthetic batch.

## Prerequisites

- [`../01-eval-strategy-ragas/04-dataset-versioning.md`](../01-eval-strategy-ragas/04-dataset-versioning.md)
  — the version model synthetic data joins.
- [`../../Week-13-Building-AI-Agents-with-LangGraph/06-checkpointing-human-in-loop/`](../../Week-13-Building-AI-Agents-with-LangGraph/06-checkpointing-human-in-loop/)
  — the HITL sampling for synthetic QA.