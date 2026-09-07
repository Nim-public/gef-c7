# Deep-Dive: RAG over Structured Data — Text2SQL & the Pipeline

Parent overview: [`../03-rag-over-structured-data.md`](../03-rag-over-structured-data.md)

The Text2SQL pipeline, deepened: the schema prompt generated from the
database catalog, the four-layer validation stack, the bounded repair
loop with error→hint mappings, and the grounded answer format with SQL
audit lines.

## File map

| File | What it covers |
|---|---|
| [`01-schema-prompts.md`](01-schema-prompts.md) | Generated-from-DB, dialect rules, dates |
| [`02-validation-layers.md`](02-validation-layers.md) | Allow-lists, read-only, row caps |
| [`03-repair-loops.md`](03-repair-loops.md) | Error feedback retries |
| [`04-result-formatting.md`](04-result-formatting.md) | Grounded answers with SQL audit lines |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-schema-prompts.md` — generate the prompt from the catalog.
2. `02-validation-layers.md` — four layers, defense in depth.
3. `03-repair-loops.md` — errors as observations.
4. `04-result-formatting.md` — answers with provenance.

## Prerequisites

- [`../01-rdbms-sql-fundamentals/`](../01-rdbms-sql-fundamentals/) — the
  schema, corpus, and query ladder.
- [`../02-database-choices/03-read-only-safety.md`](../02-database-choices/03-read-only-safety.md)
  — the structural wall under the validation stack.