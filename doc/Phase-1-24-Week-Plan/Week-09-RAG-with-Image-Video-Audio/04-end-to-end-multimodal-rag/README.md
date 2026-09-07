# Deep-Dive: End-to-End Multimodal RAG Build

Parent overview: [`../04-end-to-end-multimodal-rag.md`](../04-end-to-end-multimodal-rag.md)

The parent sketched ingestion → hybrid retrieval → grounded generation.
This subfolder builds each stage as a measurable component: an ingestion
script that emits captions and region crops into LanceDB, a fusion-based
retriever with filters, a VLM generation stage with citation enforcement,
and the per-stage cost/latency ledger the whole system reports.

## File map

| File | What it covers |
|---|---|
| [`01-ingestion.md`](01-ingestion.md) | Captions + embeddings + region crops → tables |
| [`02-hybrid-retrieval.md`](02-hybrid-retrieval.md) | Cross-space fusion with filters |
| [`03-grounded-generation.md`](03-grounded-generation.md) | VLM answers with enforced citations |
| [`04-cost-latency-ledger.md`](04-cost-latency-ledger.md) | Per-stage measurement, p50/p95 |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-ingestion.md` — nothing works until ingest is idempotent.
2. `02-hybrid-retrieval.md` — the retrieval your router dispatches to.
3. `03-grounded-generation.md` — the answer layer, cited or nothing.
4. `04-cost-latency-ledger.md` — the numbers that keep it honest.

## Prerequisites

- This week's files 01–03 (apps, store, patterns) — all components exist.
- [`../../Week-07-Multimodal-AI-Building-the-Foundation/04-data-alignment-synchronization/`](../../Week-07-Multimodal-AI-Building-the-Foundation/04-data-alignment-synchronization/)
  — the validation gates ingest must pass.
