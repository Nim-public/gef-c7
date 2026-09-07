# Ingestion — Captions, Embeddings, Region Crops to LanceDB

**What you'll learn:** the offline half of the system: one idempotent
ingest that produces captions, two vector columns, and *region crops* for
chart-heavy units — with the validation gate at the end.

## 1. The script, stage by stage

```python
# scripts/ingest_multimodal.py
import pandas as pd, lancedb, numpy as np
from pathlib import Path

def ingest(manifest_path: str, out_dir: str = "data/lancedb") -> None:
    df = pd.read_parquet(manifest_path)
    rows = []
    for r in df.itertuples():
        caption = blip_caption(r.rel_path) if r.modality == "image" else ""
        ocr = ocr_text(r.rel_path) if r.sidecar_status == "pending" else r.notes
        text = f"{ocr}\n{caption}".strip()
        row = {
            "unit_id": r.unit_id,
            "modality": r.modality,
            "text": text,
            "caption_version": CAPTION_VERSION,
            "text_vec": encode_text([text])[0],
            "image_vec": clip_image_embed(r.rel_path) if r.modality in
                         ("image", "video") else None,
            "crops": region_crops(r.rel_path) if has_chart(r) else [],
        }
        rows.append(row)
    db = lancedb.connect(out_dir)
    db.create_table("units", data=pd.DataFrame(rows), mode="overwrite")
```

Region crops (`region_crops`) split chart-heavy images into detected
regions (via OCR bounding boxes or simple quadrants) — each crop becomes
its own unit row with an `unit_id:parent_id` relation, so retrieval can
answer "which part of the chart" at citation granularity.

## 2. Idempotency and versioning

| Mechanism | Implementation | Protects |
|---|---|---|
| Content hash ids | manifest sha256 | duplicate rows |
| `caption_version` | bump on captioner change | silent drift |
| settings hash | `unit_key(rel_path, settings)` | stale embeddings |
| validation gate | run `validate()` post-ingest | everything above |

The gate from Week 07 runs *inside* ingest: a corpus that fails validation
never reaches the table.

## 3. Crop units in the schema

```python
# parent: unit_id="u123" (the full image)
# child:  unit_id="u123::r2", parent_id="u123", region=[x, y, w, h]
```

Two retrieval modes fall out: coarse (parents only) for context windows,
fine (crops included) for citations. Filter with `WHERE parent_id IS NULL`
for the coarse pass.

## 4. The staging swap — how production ingest actually runs

`mode="overwrite"` on a live table is a demo-day outage waiting to happen.
The staging pattern:

```text
1. ingest → units_staging (full rebuild, any schema)
2. validate staging (W7 gate) + row-count check vs manifest
3. smoke queries: 5 golden queries, compare top-3 vs live table
4. swap: units → units_backup; units_staging → units
5. keep backup one cycle; delete only after next successful ingest
```

```python
def promote(db, golden: list[str]):
    assert live_top3_matches(db, "units_staging", golden), "smoke failed"
    db.table_names()  # sanity: staging exists
    # rename dance via your client's table ops; backups beat in-place edits
```

The smoke step is what catches the silent schema drift that validation's
shape checks miss (e.g., vectors now float64 — passes counts, breaks
cosine precision).

## Exercises

1. Add crop units for 5 chart images (quadrant splitting is fine); verify
   parent/child rows and that coarse-mode retrieval excludes children.
2. Idempotency proof: run ingest twice; assert table row count and vector
   hashes identical.
3. Gate drill: corrupt one hash post-ingest; run the validation gate; it
   must fail *before* the table is served. Then run the staging swap with
   the golden-query smoke test and confirm zero user-visible change.

## Pitfalls

- Crops without provenance (`parent_id`) — orphan citations that cannot be
  verified against the source unit.
- Re-encoding the whole corpus to change one captioner — caption_version
  enables targeted re-ingest; use it.
- `mode="overwrite"` on the live table — stage to `units_staging`,
  validate, then swap.

## Resources

- Week-07 manifest/align/validate files; Week-08 CLIP + BLIP components.
- LanceDB multi-vector file (this week) — the target schema.
