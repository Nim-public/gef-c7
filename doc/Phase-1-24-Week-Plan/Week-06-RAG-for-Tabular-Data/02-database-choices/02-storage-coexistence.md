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

## 6. The coexistence drill record (the map's proof)

```text
SQLite:  orders=312, order_items=704, products=15
LanceDB: vectors=214 (units), unit_ids resolvable to manifest
files:   data/raw = 214 source files
cross-check: manifest count == LanceDB count == raw file count ✓
orphan probe: manifest row deleted → flag raised ✓
```

The drill record is the map's proof — the counts across stores, the
cross-check, and the orphan probe. The polyglot storage map is only
trustworthy when its sync rules are demonstrably enforced.

## Exercises

1. Draw your capstone's storage map with the linking keys; verify each
   key resolves (a unit_id lookup, a SQL query, a file path).
2. Consistency drill: ingest 5 new units; check the counts across
   stores agree (SQLite rows, LanceDB vectors, manifest rows).
3. Drift drill: delete a manifest row but leave the LanceDB vector; the
   consistency check must flag the orphan — the sync rule proven.
4. Pin drill: write the note; the consistency command recorded.
5. Record drill: fill §6 from your stores; the counts committed.

## 7. The store-choice per data type (the map's routing annex)

| Data type | Store | Why |
|---|---|---|
| transactional facts | SQLite | constraints, joins, aggregates |
| prose/chunks | LanceDB | embedding search |
| media binaries | file system | too large for any DB |
| free text in tables | SQLite + serialized copy in LanceDB | the hybrid bridge (file 04) |
| derived aggregates | computed, not stored | freshness by construction |

The annex extends the map per *data type* — the capstone's every data
shape has a home, and the last row is the W12 lesson (derived aggregates
are computed fresh, never cached into staleness).