# Deep-Dive: Eval Strategy & Ragas

Parent overview: [`../01-eval-strategy-ragas.md`](../01-eval-strategy-ragas.md)

The eval-strategy week: the four Ragas metrics as *diagnosis* tools,
slice analysis per route and doc type, offline vs online signals, and
the dataset-versioning discipline that keeps eval sets trustworthy.

## File map

| File | What it covers |
|---|---|
| [`01-ragas-revision.md`](01-ragas-revision.md) | Four metrics, diagnosis patterns |
| [`02-slice-analysis.md`](02-slice-analysis.md) | Per route/doc-type tables |
| [`03-offline-vs-online.md`](03-offline-vs-online.md) | Golden sets and live signals |
| [`04-dataset-versioning.md`](04-dataset-versioning.md) | Immutable, changelog, held-out slices |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-ragas-revision.md` — the metrics, as diagnoses.
2. `02-slice-analysis.md` — where the system is weak.
3. `03-offline-vs-online.md` — golden sets vs live signals.
4. `04-dataset-versioning.md` — the set's governance.

## Prerequisites

- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md)
  — the minimal metrics this formalizes.
- [`../../Week-15-Production-Grade-Agent-Reliability-Performance-Optimization/01-reliability-limits-retries-tests/04-test-pyramid.md`](../../Week-15-Production-Grade-Agent-Reliability-Performance-Optimization/01-reliability-limits-retries-tests/04-test-pyramid.md)
  — the pyramid these evals slot into.