# Deep-Dive: Evaluation Metrics & Benchmarks

Parent overview: [`../05-evaluation-metrics-benchmarks.md`](../05-evaluation-metrics-benchmarks.md)

The overview computed BLEU and CLIPScore once. Here we make evaluation a
discipline: every major caption metric implemented from first principles with
edge cases named, retrieval metrics in *both* directions, and the benchmark
landscape mapped onto your capstone's evaluation loop.

## File map

| File | What it covers |
|---|---|
| [`01-bleu-by-hand.md`](01-bleu-by-hand.md) | n-gram precision, clipping, brevity penalty — from scratch |
| [`02-clipscore.md`](02-clipscore.md) | Semantic caption evaluation with CLIP, full implementation |
| [`03-retrieval-metrics.md`](03-retrieval-metrics.md) | R@1/5/10, MedR, image→text *and* text→image |
| [`04-benchmark-tour.md`](04-benchmark-tour.md) | COCO/VQA/AudioCaps/MSR-VTT mapped to your eval set |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-bleu-by-hand.md` — know what the number *is* before trusting it.
2. `02-clipscore.md` — the semantic complement BLEU lacks.
3. `03-retrieval-metrics.md` — the metrics your RAG demo actually reports.
4. `04-benchmark-tour.md` — where each metric is the *official* one.

## Prerequisites

- Week 04 (retrieval pipeline) — file 03 extends its metrics.
- [`../02-modality-processing-pipelines/`](../02-modality-processing-pipelines/)
  — encoder parity, so your metric inputs are trustworthy.
