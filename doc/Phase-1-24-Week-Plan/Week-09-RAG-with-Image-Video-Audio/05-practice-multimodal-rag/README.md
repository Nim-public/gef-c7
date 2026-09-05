# Deep-Dive: Practice — Multimodal RAG over Your Data

Parent deliverable spec: [`../05-practice-multimodal-rag.md`](../05-practice-multimodal-rag.md)

The parent defines the deliverable, requirements, agent-tool contract, and
rubric. This subfolder is the build guide: corpus preparation, the
three-store index, the router with a safety battery (including the
cross-server injection case), and the eval tables that grade the system.

## File map

| File | What it covers |
|---|---|
| [`01-corpus-prep.md`](01-corpus-prep.md) | Manifests → captions → crops, with gates |
| [`02-three-store-indexing.md`](02-three-store-indexing.md) | Chunks, fields, crops — the three stores |
| [`03-router-safety.md`](03-router-safety.md) | Router battery incl. cross-server injection |
| [`04-eval-tables.md`](04-eval-tables.md) | Retrieval + Ragas + latency tables |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Build order

1. `01-corpus-prep.md` — corpus first, gates included.
2. `02-three-store-indexing.md` — the schema that serves all routes.
3. `03-router-safety.md` — the battery that keeps the demo honest.
4. `04-eval-tables.md` — the three tables the rubric grades.

## Prerequisites

- This week's files 01–04 — every component exists; this wires them.
- [`../../Week-07-Multimodal-AI-Building-the-Foundation/06-practice-multimodal-explorer/`](../../Week-07-Multimodal-AI-Building-the-Foundation/06-practice-multimodal-explorer/)
  — the audit ritual reused here.
