# Storage Coexistence — Relational + Vector + Graph Map

**What you'll learn:** the capstone's polyglot storage map: which store
owns which data, how they reference each other, and the sync rules that
keep the map from rotting.

## 1. The map

| Store | Owns | Referenced by | Example |
|---|---|---|---|
| SQLite (warehouse) | tabular facts: orders, products | the SQL tool | `order_items` rows |
| LanceDB (vector) | text chunks + embeddings | the RAG retriever | manual pages, transcripts |
| DuckDB (analytics, optional) | analytical views over exports | chart tools | monthly aggregates |
| file system | raw media, checkpoints | ingest pipelines | PDFs, WAVs |

The boundary rule from W12 file 02-04: prose and citations live in the
vector store; exact numbers live in the relational store; the two link
by `unit_id` and by *content* (the SQL answer's query text).

## 2. The linking keys (how stores reference each other)

| Link | From → To | Key |
|---|---|---|
| answer → corpus unit | agent answer → LanceDB | `unit_id` |
| answer → warehouse fact | agent answer → SQLite | the SQL text |
| chunk → source file | LanceDB → file system | `source_path` metadata |
| order → customer | within SQLite | FKs |

No store duplicates another's data — the linking keys are the join
seams. The dual-pipeline agent (W12 file 04-04) composes answers from
both stores, each claim citing its store's artifact.

## 3. The sync rules (keeping the map honest)

| Rule | Mechanism |
|---|---|
| one writer per store | ingestion scripts own writes; agents read |
| schema versions stamped | SQLite DDL version, LanceDB table version |
| deletes are logical | `is_active=0` flags, not DELETEs |
| cross-store consistency checked | the validation battery's V-gates |

The sync rules are the W9 alignment discipline applied across stores:
one writer per store, logical deletes, and consistency checks that
compare counts and hashes across the map.

## 5. The coexistence pin note (the map's record)

```markdown
# Storage map (W06)
- SQLite: warehouse.db — orders, products, customers, order_items
- LanceDB: data/lancedb/units — text chunks + embeddings (hybrid)
- files: data/raw + data/sandbox — sources and artifacts
- linking: unit_id (chunks→manifest), SQL text (answers→facts)
- sync: one writer per store; logical deletes; V-gates check counts
```

The pin note is the map's record — each store, its data, its links, and
the sync rules. The dual-pipeline agent (W12-04) cites this page.

## Exercises

1. Draw your capstone's storage map with the linking keys; verify each
   key resolves (a unit_id lookup, a SQL query, a file path).
2. Consistency drill: ingest 5 new units; check the counts across
   stores agree (SQLite rows, LanceDB vectors, manifest rows).
3. Drift drill: delete a manifest row but leave the LanceDB vector; the
   consistency check must flag the orphan — the sync rule proven.
4. Pin drill: write the note; the consistency command recorded.