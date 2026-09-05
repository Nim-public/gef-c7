# Deep-Dive: Practice — Multimodal Dataset Explorer & Alignment Audit

Parent deliverable spec: [`../06-practice-multimodal-explorer.md`](../06-practice-multimodal-explorer.md)

The parent defines Parts A/B/C and the rubric. This subfolder is the *build
guide*: file-by-file implementation of the explorer, the alignment audit, the
metrics mini-run, and the capstone integration — each with acceptance
criteria so you know when each part is done.

## File map

| File | What it covers |
|---|---|
| [`01-explorer-build.md`](01-explorer-build.md) | Dataset stats module + Gradio viewer, acceptance criteria |
| [`02-alignment-audit.md`](02-alignment-audit.md) | Audit report generation wired to the validation catalog |
| [`03-metrics-demo.md`](03-metrics-demo.md) | BLEU + CLIPScore on real pairs as a runnable demo |
| [`04-capstone-inventory.md`](04-capstone-inventory.md) | Modality inventory → scope → README integration |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Build order (each part depends on the previous)

1. `01-explorer-build.md` — you need to *see* the corpus before auditing it.
2. `02-alignment-audit.md` — the audit formalizes what the explorer shows.
3. `03-metrics-demo.md` — numbers on the pairs you just eyeballed.
4. `04-capstone-inventory.md` — write the conclusions into the capstone.

## Prerequisites

- [`../01-multimodal-ai-landscape/`](../01-multimodal-ai-landscape/) — manifest.
- [`../04-data-alignment-synchronization/`](../04-data-alignment-synchronization/) — checks V1–V8.
- [`../05-evaluation-metrics-benchmarks/`](../05-evaluation-metrics-benchmarks/) — BLEU + CLIPScore implementations.
