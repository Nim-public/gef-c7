# Cross-Store Joins — Ids Linking Chunks and Rows

**What you'll learn:** the hybrid answer's provenance: a retrieved row
chunk joined back to the live warehouse row by id — the cross-store
join that makes the vector hit and the SQL fact the same fact.

## 1. The join

```python
def hydrate_row(chunk: dict, conn) -> dict:
    """LanceDB hit → the live warehouse row."""
    table = chunk["source_table"]
    key = chunk["row_key"]
    row = conn.execute(f"SELECT * FROM {table} WHERE rowid = ?",
                       (key,)).fetchone()
    return {"chunk_text": chunk["text"], "live_row": row,
            "stale": chunk_text_differs(chunk, row)}
```

| Field | Purpose |
|---|---|
| `chunk_text` | what the embedder saw at ingest |
| `live_row` | the current warehouse values |
| `stale` | whether they still agree |

The staleness check is the point: the chunk was serialized at ingest;
the warehouse row may have changed. The answer cites the *live* row and
flags the discrepancy — the citation audit's cross-store edition.

## 2. The staleness policy

| Staleness | Behavior |
|---|---|
| fresh (matches) | answer from the live row |
| drifted (values changed) | answer from live + note the drift |
| row deleted | "this record no longer exists" |

```python
def staleness(chunk_text: str, live_row: dict) -> bool:
    re_serialized = serialize_row(live_row, columns_of(chunk_text))
    return serialize_norm(re_serialized) != serialize_norm(chunk_text)
```

The staleness test re-serializes the live row with the same serializer
and compares — normalization makes whitespace/formatting differences
irrelevant while catching value changes.

## 3. The join in the answer (the provenance line)

```text
Answer: The product "Waterproof Widget" (SKU-007) has 42 units sold.

provenance:
- vector hit: tbl-products-r0007 (score 0.82)
- live row: products.product_id=7 ✓ fresh
```

| Element | Purpose |
|---|---|
| the vector hit | how the row was found |
| the live row | the authoritative values |
| fresh/drifted | the staleness status |
| the ids | the audit trail's join keys |

The provenance line is the answer's receipt — it shows the retrieval
path AND the live verification in one glance.

## 6. The cross-store pin note (the join's manifest)

```markdown
# Cross-store join (W06)
- hydrate: LanceDB hit → live warehouse row by row_key
- staleness: re-serialize the live row, compare (normalized)
- paths: fresh (answer live), drifted (live + note), deleted (honest)
- provenance line: vector hit + live row + status + ids
```

The pin note is the join's manifest — the hydration, the staleness
policy, and the provenance line. The staleness flag is what makes the
cross-store join honest rather than decorative.

## Exercises

1. Implement `hydrate_row`; retrieve 10 row chunks; verify every live
   row matches its chunk (fresh corpus).
2. Staleness drill: update a warehouse row's price after ingest; re-run
   the hydration; the `stale` flag must fire and the answer uses the
   live value.
3. Deletion drill: delete a row post-ingest; the hydration reports
   "no longer exists" — the honest-deletion path.
4. Pin drill: write the note; the staleness drill command recorded.