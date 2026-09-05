# Deep-Dive: Data Alignment & Synchronization

Parent overview: [`../04-data-alignment-synchronization.md`](../04-data-alignment-synchronization.md)

The overview called alignment "the quiet prerequisite." This subfolder makes
it loud and mechanical: one clock for all modalities, integrity checks that
run in CI rather than in your head, an explicit policy table for missing
data, and an alignment pipeline that produces reports instead of folklore.

## File map

| File | What it covers |
|---|---|
| [`01-temporal-alignment.md`](01-temporal-alignment.md) | Subtitles ↔ frames ↔ audio on one clock: offset math and drift |
| [`02-cross-modal-validation.md`](02-cross-modal-validation.md) | Automated integrity checks with a validation report format |
| [`03-missing-data-policies.md`](03-missing-data-policies.md) | Drop / impute / flag decision tables per modality and field |
| [`04-alignment-pipeline.md`](04-alignment-pipeline.md) | The full pipeline: manifest joins, versioning, report artifacts |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-temporal-alignment.md` — get one video's clocks to agree.
2. `02-cross-modal-validation.md` — turn agreement into assertions.
3. `03-missing-data-policies.md` — decide *before* the data goes missing.
4. `04-alignment-pipeline.md` — wire it into the capstone ingest.

## Prerequisites

- [`../01-multimodal-ai-landscape/03-metadata-handling.md`](../01-multimodal-ai-landscape/03-metadata-handling.md)
  — the manifest schema this pipeline joins on.
- [`../02-modality-processing-pipelines/03-video-pipeline.md`](../02-modality-processing-pipelines/03-video-pipeline.md)
  — sampling records with timestamps.
