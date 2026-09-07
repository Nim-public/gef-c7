# Deep-Dive: Fine-Tuning Fundamentals

Parent overview: [`../03-fine-tuning-fundamentals.md`](../03-fine-tuning-fundamentals.md)

SFT done honestly: data formatting with loss masking, tokenization and
loader audits, the training loop with schedules and best-pick
checkpoints, and overfitting diagnosis with eval-during-training.

## File map

| File | What it covers |
|---|---|
| [`01-sft-data.md`](01-sft-data.md) | Formatting, masking, distribution matching |
| [`02-tokenization-loaders.md`](02-tokenization-loaders.md) | Templates, truncation audits |
| [`03-training-loop.md`](03-training-loop.md) | Args, schedules, checkpoints, best-pick |
| [`04-overfitting-diagnosis.md`](04-overfitting-diagnosis.md) | Eval-during-train discipline |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-sft-data.md` — the data decides the fine-tune.
2. `02-tokenization-loaders.md` — the seams where data gets mangled.
3. `03-training-loop.md` — the run and its knobs.
4. `04-overfitting-diagnosis.md` — the eval-during-train discipline.

## Prerequisites

- [`../01-eval-strategy-ragas/04-dataset-versioning.md`](../01-eval-strategy-ragas/04-dataset-versioning.md)
  — the data governance this inherits.
- [`../02-synthetic-data/04-validation.md`](../02-synthetic-data/04-validation.md)
  — the gates synthetic training data must pass.