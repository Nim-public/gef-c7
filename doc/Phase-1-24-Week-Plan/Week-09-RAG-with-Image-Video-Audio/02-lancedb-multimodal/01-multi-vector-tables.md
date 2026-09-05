# Multi-Vector Tables — Text + Image Columns, Per-Column Search

**What you'll learn:** one LanceDB table holding *both* modalities' vectors
as separate columns, searched per-column — the schema that replaces your
two-matrix invariant with a single queryable store.

## 1. The table, created once

```python
import lancedb, pandas as pd

db = lancedb.connect("data/lancedb")

rows = [{
    "unit_id": r.unit_id,
    "caption": r.caption,
    "path": r.rel_path,
    "modality": r.modality,
    "text_vec": text_vecs[i],          # 384-d, MiniLM
    "image_vec": image_vecs[i],        # 512-d, CLIP (None for text-only rows)
} for i, r in manifest.iterrows()]

table = db.create_table("units", data=pd.DataFrame(rows), mode="overwrite")
```

Two vector columns in one table: LanceDB indexes each independently. The
query declares the column:

```python
res = (table.search(q_text_vec, vector_column_name="text_vec")
            .limit(5).to_list())
res_img = (table.search(q_img_vec, vector_column_name="image_vec")
                .limit(5).to_list())
```

## 2. Why one table beats two matrices

| Concern | Two matrices + manifest | One LanceDB table |
|---|---|---|
| Row alignment invariant | manual assert everywhere | table-level, by construction |
| Metadata filters | pandas pre-filter | SQL `WHERE` in the query plan |
| Mixed modality rows | pad matrices | sparse columns, `None` allowed |
| Persistence | npy + parquet pair | one artifact |

The invariant does not disappear — it *moves down* into the engine. You
still assert it once after ingest (`table.to_pandas()` shape checks), but
query-time joins become impossible to desynchronize.

## 3. Ingest with the manifest as source of truth

```python
def ingest(manifest_path: str, table_name: str = "units"):
    df = pd.read_parquet(manifest_path)
    text_vecs = encode_text(df.caption.fillna("").tolist())
    image_vecs = [clip_image_embed(p) if m == "image" else None
                  for p, m in zip(df.rel_path, df.modality)]
    db.create_table(table_name, data=pd.DataFrame({
        "unit_id": df.unit_id, "caption": df.caption, "path": df.rel_path,
        "modality": df.modality, "text_vec": text_vecs.tolist(),
        "image_vec": [None if v is None else v.tolist() for v in image_vecs],
    }), mode="overwrite")
```

Ingest reads *only* the manifest (single source of truth) and fails loudly
on row-count mismatch — the Week-07 discipline, ported.

## 4. Per-column search with filters

```python
# text search scoped to image-modality rows with captions:
res = (table.search(q_vec, vector_column_name="text_vec")
            .where("modality = 'image' AND caption IS NOT NULL", prefilter=True)
            .limit(10).to_list())
```

`prefilter=True` applies the WHERE before vector search (correct for
restrictive filters); `postfilter` is faster for loose filters but can
return fewer than `limit` rows. Choose per query — the flag is a semantics
decision, not a tuning knob.

## 5. Schema evolution — the change you will actually make

Inevitable change: adding a third vector column (e.g., `audio_vec` in
Week 10). LanceDB tables are versioned artifacts:

```python
# add a column: rewrite via staging (no in-place ALTER for vector columns)
old = table.to_pandas()
old["audio_vec"] = None                      # backfill later, per unit
db["units_v2"].add(old)
# validate v2, then swap names; keep v1 until the swap is verified
```

| Change | Mechanism |
|---|---|
| add nullable column | staging table + swap (above) |
| change vector dim | new table + full re-encode (version bump) |
| add metadata field | staging + backfill from manifest |

The version-in-filename discipline from the alignment pipeline applies:
`units-v3` in the table name beats a mysterious silent schema.

## Exercises

1. Migrate the cataloger's matrix+SQLite to one LanceDB table; verify the
   search results match the old path on 10 queries (cosine ranks identical).
2. Filter drill: same vector query with `prefilter` vs `postfilter` on a
   filter matching 10% of rows — compare returned row counts and explain.
3. Schema probe: `table.schema` after ingest with one `None` image_vec —
   confirm the column stays fixed-size-list float32, not object.

## Pitfalls

- Storing vectors as Python lists of lists in a *column mixed with None* —
  check the inferred schema; explicit `pyarrow` schema avoids object dtype.
- `mode="overwrite"` in shared environments — it drops the table; use
  `mode="create"` + `add()` for incremental ingest.
- Assuming `None` vectors are skipped by search — they are, but `.where`
  must handle them (`IS NOT NULL`) or rows vanish silently.

## Resources

- LanceDB Python docs: `create_table`, `search`, vector columns.
- PyArrow fixed-size-list types for explicit schemas.
