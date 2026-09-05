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

## Exercises

1. Build the three stores on your corpus; run the invariant test; fix any
   orphan parents (usually a crop whose chart classification failed).
2. Query-class coverage: for each of your 5 routing classes, name which
   store(s) the route hits — any class with no store is a gap; file a
   follow-up, don't improvise.
3. Field utility check: answer 3 queries that need a structured fact
   ("what date", "which model version") via fields-only lookup — the store
   earns its keep or gets deleted.

## Pitfalls

- Fields as free-text blobs — schema them (name/value) or filters can't use
  them.
- Crops indexed without their text_vec — image-only crops miss the OCR text
  that routes need.
- Three tables "for cleanliness" — the fusion and contract code duplicates;
  one table, `kind` column.

## Resources

- W9-04 ingestion (the parent/child schema); patterns file (routes→stores).
- Your field-extraction prototypes — the fields store's source.
