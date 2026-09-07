# Deep-Dive: CSV/JSON Retrieval & the Hybrid Bridge

Parent overview: [`../04-csv-json-hybrid-retrieval.md`](../04-csv-json-hybrid-retrieval.md)

The hybrid retrieval week, deepened: the data-shape decision tree, row
serialization with metadata round-trips, the three-rung router, and the
cross-store join that makes vector hits and warehouse rows the same
fact.

## File map

| File | What it covers |
|---|---|
| [`01-decision-tree.md`](01-decision-tree.md) | SQL vs paste vs hybrid per shape |
| [`02-row-serialization.md`](02-row-serialization.md) | Row-major text, summary chunks |
| [`03-router-design.md`](03-router-design.md) | Rules → zero-shot → agent |
| [`04-cross-store-joins.md`](04-cross-store-joins.md) | Ids linking chunks and rows |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-decision-tree.md` — route by data shape, measurably.
2. `02-row-serialization.md` — rows as retrievable sentences.
3. `03-router-design.md` — the three-rung ladder.
4. `04-cross-store-joins.md` — the provenance join.

## Prerequisites

- [`../01-rdbms-sql-fundamentals/05-pandas-sql-bridge.md`](../01-rdbms-sql-fundamentals/05-pandas-sql-bridge.md)
  — the bridge this router routes across.
- [`../03-rag-over-structured-data/`](../03-rag-over-structured-data/)
  — the Text2SQL route.