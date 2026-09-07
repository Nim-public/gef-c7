# Deep-Dive: Capstone Task — Structured Data Retrieval

Parent overview: [`../05-capstone-task-structured-retrieval.md`](../05-capstone-task-structured-retrieval.md)

The weekly capstone: the extended schema with edge-case data, the
gold-SQL eval, the deployed router, and the safety battery — everything
from files 01–04 integrated and graded.

## File map

| File | What it covers |
|---|---|
| [`01-schema-ingestion.md`](01-schema-ingestion.md) | Extended schema, edge cases, idempotency |
| [`02-text2sql-eval.md`](02-text2sql-eval.md) | Gold-SQL methodology |
| [`03-router-implementation.md`](03-router-implementation.md) | Rules + classifier, logged |
| [`04-safety-battery.md`](04-safety-battery.md) | Write-probe, multi-statement, PII |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-schema-ingestion.md` — the schema and its edge cases.
2. `02-text2sql-eval.md` — the gold-SQL methodology.
3. `03-router-implementation.md` — the deployed router.
4. `04-safety-battery.md` — the tabular safety battery.

## Prerequisites

- Files 01–04 of this week — every component exists.
- [`../01-eval-strategy-ragas/04-dataset-versioning.md`](../01-eval-strategy-ragas/04-dataset-versioning.md)
  — the governance the eval set inherits.