# Ingestion by Source — PDF, CSV, JSON, RDBMS Paths

**What you'll learn:** getting your *actual* corpus into `Knowledge`
cleanly: per-source ingestion paths, idempotency, and the manifest
discipline that keeps Agno's ingestion from forking your data model.

## 1. The source matrix

| Source | Ingest call | Unit produced | Preprocess first? |
|---|---|---|---|
| PDF (url/file) | `knowledge.insert(url=...)` | page chunks | OCR sidecar first (W7) |
| CSV | `insert` with reader config | row/row-group chunks | typed columns → fields store |
| JSON | `insert` | per-record chunks | flatten nesting first |
| RDBMS | SQL toolkit or ETL to parquet | query results | your W6 pipeline owns this |

```python
# your corpus, your order:
for unit in manifest.itertuples():
    knowledge.insert(
        path=unit.rel_path if unit.modality != "text" else None,
        text_content=unit.text,          # the sidecar-merged text (W9)
        metadata={"unit_id": unit.unit_id, "modality": unit.modality},
    )
```

The manifest-driven insert is the discipline: Agno ingests *content*;
your manifest owns *identity*. Units keep their W7 `unit_id`s so
citations line up across every prior week's artifacts.

## 2. Idempotent ingestion (the W9-04 rule, restated)

| Mechanism | Implementation |
|---|---|
| content-hash dedup | hash before insert; skip known ids |
| versioned tables | `units-v3` naming (W9-04) |
| staged insert | staging table → validate → swap |
| re-ingest policy | only changed units (settings hash) |

```python
def insert_if_new(knowledge, unit) -> bool:
    if unit.sha256 in INGESTED:                  # loaded from the manifest
        return False
    knowledge.insert(text_content=unit.text,
                     metadata={"unit_id": unit.unit_id})
    INGESTED.add(unit.sha256)
    return True
```

Re-running ingestion adds nothing new — the same property the LanceDB
migration proved. Agno's convenience does not exempt you from the
ingestion gate: validate before serving, always.

## 3. CSV and RDBMS: structured data is a different pipeline

Structured sources do not belong in vector knowledge wholesale — the
W6 lesson (RAG for tabular data) still governs:

| Source | In vector knowledge | As SQL/tool |
|---|---|---|
| CSV (small, descriptive) | yes (row summaries) | — |
| RDBMS (transactional) | schema + sample rows only | **the tool** (text-to-SQL) |
| Charts data | OCR text as knowledge | numeric verification via SQL |

The dual-pipeline design (file 04) is precisely this split: knowledge
for prose, SQL for numbers. Ingesting a transactional table into vectors
produces confidently-wrong aggregates — the numeric-hallucination class
file 04's defenses target.

## 4. The ingestion validation gate

```text
after ingest:
  1. row count == manifest units (minus excluded)
  2. spot-check 5 units: text matches source, metadata round-trips
  3. golden-query parity (file 01's loop) passes
  4. exclusion list honored (permissions, W7-03)
```

Same gate, new surface. The gate runs after *any* ingestion change —
new source, new embedder, new chunker.

## Exercises

1. Ingest your manifest into `Knowledge` with metadata round-tripping;
   verify 5 units' `unit_id`s survive a search → citation round-trip.
2. Source-matrix drill: ingest one CSV *both* ways (vector + fields
   store); answer a structured question via each; document which fails
   and why (the dual-pipeline motivation, empirical).
3. Idempotency proof: run ingestion twice; verify unit counts and query
   results unchanged.

## Pitfalls

- `insert` on every run without dedup — duplicate vectors poison hybrid
  scores; the hash set is the fix.
- Metadata dropped at insert — citations die without `unit_id`; pass it
  explicitly.
- Vectorizing numeric tables "for completeness" — that is how
  hallucinated sums happen; route numbers through SQL (file 04).

## Resources

- Agno knowledge docs: insert, readers, metadata (context7:
  `/agno-agi/docs`).
- [`../../Week-06-RAG-for-Tabular-Data/`](../../Week-06-RAG-for-Tabular-Data/)
  — the tabular lesson this file extends.