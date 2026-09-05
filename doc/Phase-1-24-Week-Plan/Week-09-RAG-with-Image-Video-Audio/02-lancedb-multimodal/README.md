# Deep-Dive: LanceDB for Multimodal AI

Parent overview: [`../02-lancedb-multimodal.md`](../02-lancedb-multimodal.md)

This subfolder takes the toy matrix store from the cataloger and makes it
production-shaped: multi-vector tables, IVF-PQ compression with honest
recall math, the recall/speed sweep methodology, and native hybrid search.

## File map

| File | What it covers |
|---|---|
| [`01-multi-vector-tables.md`](01-multi-vector-tables.md) | Text+image columns, per-column search |
| [`02-ivf-pq.md`](02-ivf-pq.md) | Product quantization mechanics and knobs |
| [`03-recall-speed-sweeps.md`](03-recall-speed-sweeps.md) | nprobe/refine sweeps against flat ground truth |
| [`04-hybrid-search.md`](04-hybrid-search.md) | FTS + vector, RRF, filters |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-multi-vector-tables.md` — the schema decision first.
2. `02-ivf-pq.md` — what compression costs and buys.
3. `03-recall-speed-sweeps.md` — measure before you trust.
4. `04-hybrid-search.md` — the retrieval upgrade your RAG wants.

## Prerequisites

- [`../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/02-representation-levels.md`](../../Week-07-Multimodal-AI-Building-the-Foundation/01-multimodal-ai-landscape/02-representation-levels.md)
  — the matrix+manifest invariant this database replaces.
- Week 04 (retrieval) — the metrics reused in the sweeps.
