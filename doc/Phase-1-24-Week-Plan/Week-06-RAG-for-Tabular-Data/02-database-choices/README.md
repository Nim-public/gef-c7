# Deep-Dive: Database Choices

Parent overview: [`../02-database-choices.md`](../02-database-choices.md)

The storage decisions deepened: SQLite vs MySQL vs Postgres with live
dialect probes, the polyglot storage map (relational + vector + files),
the read-only wall proven structurally, and the dev/staging/prod
environment ladder.

## File map

| File | What it covers |
|---|---|
| [`01-sqlite-mysql-postgres.md`](01-sqlite-mysql-postgres.md) | Decision heuristics, dialect diffs |
| [`02-storage-coexistence.md`](02-storage-coexistence.md) | Relational + vector + graph map |
| [`03-read-only-safety.md`](03-read-only-safety.md) | Users, modes, allow-lists |
| [`04-environment-ladder.md`](04-environment-ladder.md) | Dev/staging/prod data policies |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-sqlite-mysql-postgres.md` — pick the engine with evidence.
2. `02-storage-coexistence.md` — map the polyglot stores.
3. `03-read-only-safety.md` — the structural wall.
4. `04-environment-ladder.md` — organize the environments.

## Prerequisites

- [`../01-rdbms-sql-fundamentals/`](../01-rdbms-sql-fundamentals/) — the
  warehouse schema and corpus.
- [`../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/`](../../Week-09-RAG-with-Image-Video-Audio/02-lancedb-multimodal/)
  — the vector store in the coexistence map.