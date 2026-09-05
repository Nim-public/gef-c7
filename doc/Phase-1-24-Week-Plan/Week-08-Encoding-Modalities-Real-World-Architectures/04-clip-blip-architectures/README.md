# Deep-Dive: CLIP & BLIP Architectures

Parent overview: [`../04-clip-blip-architectures.md`](../04-clip-blip-architectures.md)

The two production workhorses, taken apart: CLIP's contrastive loss computed
on a matrix you can hand-check, zero-shot classification with honest logit
reading, BLIP's three objectives and what each buys, and the decision guide
that picks the right model per capstone job.

## File map

| File | What it covers |
|---|---|
| [`01-clip-loss.md`](01-clip-loss.md) | The N×N contrastive matrix by hand and in code |
| [`02-zero-shot-classification.md`](02-zero-shot-classification.md) | Prompt ensembles, logit reading, calibration traps |
| [`03-blip-objectives.md`](03-blip-objectives.md) | ITC / ITM / LM — three heads, three capabilities |
| [`04-decision-guide.md`](04-decision-guide.md) | CLIP vs BLIP vs full VLM per job, with costs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-clip-loss.md` — the loss that made everything possible.
2. `02-zero-shot-classification.md` — the skill your RAG demo uses daily.
3. `03-blip-objectives.md` — what generation-ready alignment adds.
4. `04-decision-guide.md` — pick per job, not per hype.

## Prerequisites

- [`../01-encoding-text-images/03-vit-patch-tokens.md`](../01-encoding-text-images/03-vit-patch-tokens.md)
  — the image tower.
- [`../03-modality-fusion/02-intermediate-fusion.md`](../03-modality-fusion/02-intermediate-fusion.md)
  — cross-attention (BLIP's ITM/LM use it).
