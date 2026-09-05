# Deep-Dive: The Multimodal AI Landscape

Parent overview: [`../01-multimodal-ai-landscape.md`](../01-multimodal-ai-landscape.md)

This subfolder goes beyond the overview: exact modality-by-modality tradeoff
tables, a concrete storage strategy for raw/processed/embedding artifacts, a
metadata playbook you can run on your own corpus, and the "modality gap"
framed as a buildable inventory rather than an abstract warning.

## File map

| File | What it covers |
|---|---|
| [`01-modality-comparison.md`](01-modality-comparison.md) | Representation, cost, tasks, model families — per modality, with numbers |
| [`02-representation-levels.md`](02-representation-levels.md) | Raw vs processed vs embeddings: what to keep on disk and why |
| [`03-metadata-handling.md`](03-metadata-handling.md) | Manifests, EXIF, provenance, permissions — a runnable playbook |
| [`04-the-modality-gap.md`](04-the-modality-gap.md) | Why alignment is hard, and the capstone modality inventory |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-modality-comparison.md` — calibrate what each modality actually costs.
2. `02-representation-levels.md` — decide your on-disk layout once.
3. `03-metadata-handling.md` — build the manifest your later weeks assume.
4. `04-the-modality-gap.md` — connect everything to the GEF C7 capstone.

## Prerequisites

- Week 01 (text tokens, embeddings) and Week 04 (retrieval foundations).
- A Python env with `datasets`, `pillow`, `pandas` available.
