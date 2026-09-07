# 03.3 — LanceDB in Production

> Subfolder index: [README.md](README.md) · Parent: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md)

---

## What you'll learn

- LanceDB tables: schema, persistence, updates
- Metadata filtering: prefilter vs postfilter, the security pattern
- The persistence model: what survives restarts
- The update lifecycle: add, update, delete without corrupting the index

## 1. Tables with schema

```python
import lancedb
import pandas as pd

db = lancedb.connect("data/lancedb")

table = db.create_table("capstone_chunks", data=pd.DataFrame({
    "id": chunk_ids, "text": chunk_texts, "source": sources,
    "doc_type": doc_types, "permissions": permissions,
    "vector": emb_list,
}), mode="overwrite")
```

The table is a folder on disk — persistent, restartable, shareable. The schema is inferred from the DataFrame; explicit schemas prevent inference surprises.

## 2. Metadata filtering — prefilter for security

```python
# prefilter: restricted rows never enter the candidate set
hits = (table.search(q_vec)
        .where("permissions = 'all-staff'", prefilter=True)
        .limit(5).to_list())

# postfilter: trims results AFTER search — can return nothing when matches exist
hits_post = (table.search(q_vec)
             .where("doc_type = 'policy'")
             .limit(5).to_list())          # may be empty even if matches exist
```

**The security rule**: permission filters are always prefilter — a restricted document in the candidate set is a data leak even if the final answer doesn't use it. The E7-01 threat model requires this.

## 3. The update lifecycle

```python
# add new chunks
table.add(new_chunks_df)

# delete by predicate (source-level re-ingestion)
table.delete("source_fp = '3f2a'")

# update = delete + add (no in-place update)
old = table.search().where("id = 'old-id'").to_list()
table.delete("id = 'old-id'")
table.add(updated_chunk)
```

The delete-then-add pattern for updates keeps the index consistent — no stale vectors for changed content. The W4-05 incremental rule: only changed sources re-ingest.

## 4. Persistence and restarts

The table lives on disk under `data/lancedb/` — process restarts reload it without re-embedding. But:

- the **index** (if created) may need rebuilding after bulk adds
- the **schema** is fixed at creation — new columns need `table.add_columns()`
- concurrent writers need care (single-writer per table, or use the transaction API)

The persistence model makes LanceDB suitable for the capstone's local development AND small-team production — the step between in-memory FAISS and a managed service (W6-02's coexistence map).

## Exercises

1. Persistence test: create a table, close the process, reopen — verify all data intact and searchable.
2. The update lifecycle: add, update (delete+add), delete a chunk — verify the index reflects each operation immediately.
3. Schema evolution: add a `language` column to an existing table — does the index need rebuilding?
4. Concurrency probe: two processes writing to the same table — observe the behavior; design the write protocol.
5. The migration drill: copy a table between LanceDB databases (dev → staging); verify all rows and the index transfer.

## Pitfalls

- **`mode="overwrite"` in production** — wipes the table on every deploy; use `mode="append"` or explicit deletes
- **Index not rebuilt after bulk add** — new vectors are searchable but unoptimized; rebuild after large ingests
- **Schema inference surprises** — a None in a column changes the inferred type; pin the schema
- **Large tables without indexes** — full scans on every query; create the ANN index after initial load
- **Concurrent writes without protocol** — last-writer-wins or corruption; serialize writes or use optimistic locking

## Resources

- [LanceDB docs](https://lancedb.github.io/lancedb/) — tables, indexes, updates, filters
- W4-01/02 (the contracts LanceDB implements), W5-03 (the filtering consumer) — composed here
- [Lance format](https://lance.org/) — the columnar storage spec
