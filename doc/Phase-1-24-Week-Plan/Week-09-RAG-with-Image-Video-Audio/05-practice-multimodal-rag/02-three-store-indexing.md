# Three-Store Indexing — Chunks, Fields, Crops

**What you'll learn:** the practice deliverable's stage 2: three stores
(text chunks, structured fields, image crops) in one LanceDB table, each
serving different query classes, with the alignment invariants that keep
them joinable.

## 1. The three stores, one table

| Store | Rows | Vector column | Serves |
|---|---|---|---|
| chunks | text pages/paragraphs | text_vec | P1 retrieval |
| fields | structured facts (name, date, value) | — | filters, exact lookup |
| crops | chart regions | image_vec + text_vec | fine-grained citation |

```python
rows = chunks_rows + fields_rows + crop_rows     # one create_table
```

One table, three row kinds, discriminated by `kind` — filters do the
rest. The alternative (three tables) splits the fusion logic; one table
keeps RRF simple.

## 2. Fields: the structured store that filters love

```python
field_rows = [{
    "kind": "field", "unit_id": f"{uid}::f_{name}",
    "parent_id": uid, "field": name, "value": str(val),
    "text_vec": encode_text([f"{name}: {val}"])[0],
} for uid, fields in extracted_fields.items() for name, val in fields.items()]
```

Fields come from regex/LLM extraction over OCR text (dates, totals, model
names). They serve two purposes: prefilter scopes (`WHERE kind='field' AND
field='date'`) and answer augmentation ("the chart says 12%").

## 3. The invariants that keep stores joinable

| Invariant | Assert | Breaks |
|---|---|---|
| Parent exists | every `parent_id` ∈ chunks/crops parents | orphan citations |
| Row alignment | `text_vec` rows ↔ manifest | wrong-unit hits |
| Kind discipline | fields have no image_vec | column-type drift |

One test, three asserts — the Week-07 V2 check generalized to the full
schema.

## 4. Store sizing — the numbers that justify the design

On a 2k-unit corpus (your scale):

| Store | Rows | Vector bytes | Non-vector bytes | Build time |
|---|---|---|---|---|
| chunks | 2,000 | 2000×384×4 = 3.1 MB | ~2 MB text | ~1 min |
| fields | ~6,000 (3/unit) | 6.1 MB | ~0.5 MB | +30 s |
| crops | ~400 (0.2/unit) | 0.8 MB | ~50 MB images (paths only) | +2 min |

```python
def store_bytes(df) -> dict:
    v = df.text_vec.dropna().shape[0] * 384 * 4
    return {"rows": len(df), "vector_mb": round(v / 1e6, 1)}
```

Three observations that defend the design: (1) vectors are the *small*
part — text and crop files dominate disk, which is why crop rows store
paths, not pixels; (2) fields at 3 rows/unit triple the row count but not
the build pain; (3) total build stays under 5 minutes, so re-ingest after
any settings change is routine rather than feared.

## 5. Store lifecycle — when each store is rebuilt

| Trigger | chunks | fields | crops |
|---|---|---|---|
| text encoder change | rebuild | rebuild | — (uses image_vec? no) |
| image encoder change | — | — | rebuild |
| caption version bump | rebuild (captions inside text) | — | — |
| OCR engine change | rebuild | rebuild | — |
| crop strategy change | — | — | rebuild |

```python
REBUILD_MATRIX = {
    "text_encoder": {"chunks", "fields"},
    "image_encoder": {"crops"},
    "caption_version": {"chunks"},
    "ocr_engine": {"chunks", "fields"},
    "crop_strategy": {"crops"},
}

def affected_stores(change: str) -> set[str]:
    return REBUILD_MATRIX.get(change, set())
```

The matrix prevents both failure modes: rebuilding everything (hours) and
rebuilding nothing (stale vectors). It is settings-version discipline,
made explicit per store.

## Exercises

1. Build the three stores on your corpus; run the invariant test; fix any
   orphan parents (usually a crop whose chart classification failed).
2. Query-class coverage: for each of your 5 routing classes, name which
   store(s) the route hits — any class with no store is a gap; file a
   follow-up, don't improvise.
3. Field utility check: answer 3 structured-fact queries via fields-only
   lookup; then dry-run the rebuild matrix — for a text-encoder change,
   name exactly which stores rebuild and the expected total time from the
   sizing table.

## Pitfalls

- Fields as free-text blobs — schema them (name/value) or filters can't
  use them.
- Crops indexed without their text_vec — image-only crops miss the OCR
  text that routes need.
- Three tables "for cleanliness" — the fusion and contract code duplicates;
  one table, `kind` column.

## Resources

- W9-04 ingestion (the parent/child schema); patterns file (routes→stores).
- Your field-extraction prototypes — the fields store's source.
