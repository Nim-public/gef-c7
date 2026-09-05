# Metadata Handling — Manifests, EXIF, Provenance, Permissions

**What you'll learn:** turn loose files into a queryable corpus: one manifest
to rule them, EXIF/IPTC extraction that survives real-world photos, and a
provenance + permissions schema you can defend in a review.

## 1. The manifest is the corpus

Raw bytes answer "what does it look like"; the manifest answers "what is it,
where did it come from, and may I use it." Every later week (alignment,
retrieval, evaluation) joins on the manifest, so its schema is an API —
version it, and never rename columns casually.

```python
import pandas as pd, pyarrow.parquet as pq

SCHEMA_V1 = {
    "unit_id": str,          # stable slug, never recycled
    "modality": str,         # text|image|audio|video
    "rel_path": str,         # repo-relative, POSIX separators
    "sha256": str,           # content hash of raw file
    "source_uri": str,       # URL or scanner path
    "license": str,          # SPDX id or "UNLICENSED"
    "captured_at": str,      # ISO 8601, from EXIF/ID3/container if present
    "settings_json": str,    # processing settings used
    "notes": str,
}

df = pd.read_parquet("data/manifests/corpus-manifest.parquet")
assert set(SCHEMA_V1) <= set(df.columns), "manifest schema drift"
```

## 2. EXIF extraction that survives real photos

```python
from PIL import Image
from PIL.ExifTags import TAGS

def exif_summary(path: str) -> dict:
    img = Image.open(path)
    raw = img.getexif()
    out = {}
    for tag_id, val in raw.items():
        name = TAGS.get(tag_id, f"tag_{tag_id}")
        out[name] = str(val)
    # Orientation (274) decides whether your resize should swap w/h.
    if "Orientation" in out:
        out["needs_transpose"] = out["Orientation"] != "1"
    return out

print(exif_summary("data/raw/images/IMG_4021.jpg"))
# {'Make': 'Apple', 'DateTimeOriginal': '2025:11:03 14:22:41',
#  'Orientation': '6', 'needs_transpose': True}
```

The two EXIF fields that actually bite pipelines: **Orientation** (image is
sideways unless you call `PIL.ImageOps.exif_transpose`) and
**DateTimeOriginal** (your temporal-align clock for photo corpora). Phone
exports frequently strip both — treat their absence as data, not noise.

## 3. Provenance: where every unit came from

```python
from datetime import datetime, timezone

def make_unit(unit_id, modality, rel_path, source_uri, license, **kw) -> dict:
    row = dict(
        unit_id=unit_id, modality=modality, rel_path=rel_path,
        sha256=kw["sha256"], source_uri=source_uri, license=license,
        captured_at=kw.get("captured_at") or "",           # may be unknown
        settings_json=kw.get("settings_json", "{}"),
        notes=kw.get("notes", ""),
        ingested_at=datetime.now(timezone.utc).isoformat(),
    )
    return row
```

Provenance answers review questions before they are asked: "why is this
screenshot in the corpus?" → `source_uri` + `notes`. For scraped or
user-contributed data, record the *access date* too — pages rot, and a
dead link with a date is evidence; a dead link without one is a mystery.

## 4. Permissions: a decision table, encoded

| Source type | Default license posture | Action |
|---|---|---|
| Your own files | yours | ingest, note in `notes` |
| CC-BY / CC-BY-SA | attribution required | keep `source_uri`, add attribution page |
| CC0 / public domain | free | ingest |
| "All rights reserved" web content | restricted | do **not** ingest into the repo; process locally, exclude from published corpus |
| Vendor ToS-limited (e.g., API dumps) | restricted | check ToS; usually exclude |

```python
ALLOWED = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "UNLICENSED"}

def enforce_permissions(df: pd.DataFrame, allow: set[str] = ALLOWED) -> pd.DataFrame:
    blocked = df[~df["license"].isin(allow)]
    if len(blocked):
        blocked.to_parquet("data/manifests/excluded.parquet")
    return df[df["license"].isin(allow)].reset_index(drop=True)
```

Run this *before* building embeddings — excluded units should never have a
vector, or your published index leaks restricted content.

## Exercises

1. Extend `exif_summary` to also read XMP (where PDFs and some cameras store
   licenses). Write the merge rule when EXIF and XMP disagree.
2. Build a manifest for 10 mixed files in `data/raw/` (any modality): hash,
   guess modality from extension, apply the permissions table, and write the
   excluded rows to a report.
3. A teammate renames `captured_at` → `date`. List three downstream files
   that break and the schema-versioning move that would have prevented it.

## Pitfalls

- Backslashes in `rel_path` — Windows-only paths poison POSIX consumers; always `Path.as_posix()`.
- Trusting EXIF timestamps as UTC — they are local time with no offset; record the offset you assume.
- "License: unknown" rows left in the corpus — unknown means excluded until proven otherwise.

## Resources

- EXIF tag reference (CIPA DC-008); PIL ExifTags documentation.
- SPDX license identifier list for the `license` column.
