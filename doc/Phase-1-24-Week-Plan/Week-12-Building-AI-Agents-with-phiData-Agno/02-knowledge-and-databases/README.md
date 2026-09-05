# Deep-Dive: Knowledge & Databases

Parent overview: [`../02-knowledge-and-databases.md`](../02-knowledge-and-databases.md)

Agno's `Knowledge` wraps exactly the stack you built in Weeks 04–09:
LanceDB, hybrid search, rerankers. This subfolder wires your corpus in,
covers ingestion by source, grounding rules that survive agentic RAG, and
the dual-pipeline design (knowledge vs SQL) your capstone needs.

## File map

| File | What it covers |
|---|---|
| [`01-knowledge-lancedb.md`](01-knowledge-lancedb.md) | `Knowledge` + LanceDB + hybrid + rerankers |
| [`02-ingestion-by-source.md`](02-ingestion-by-source.md) | PDF / CSV / JSON / RDBMS paths |
| [`03-grounding-rules.md`](03-grounding-rules.md) | Instructions + insufficiency battery |
| [`04-dual-pipeline.md`](04-dual-pipeline.md) | Knowledge vs SQL tool selection |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-knowledge-lancedb.md` — your W09 index, wrapped.
2. `02-ingestion-by-source.md` — getting your corpus in cleanly.
3. `03-grounding-rules.md` — the constitution, knowledge edition.
4. `04-dual-pipeline.md` — two tools, one routing decision.

## Prerequisites

- [`../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/`](../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/)
  — the store and sweeps this wraps.
- [`../01-agno-introduction/01-agent-structure.md`](../01-agno-introduction/01-agent-structure.md)
  — the Agent fields.
