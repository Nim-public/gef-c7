# Exercises — Multimodal Landscape Deep-Dive

Expanded set with worked approaches. Do them in order; each builds on the
last. Target corpus: whatever exists under `data/raw/` in your repo.

## 1. Modality cost audit (from 01-modality-comparison)

**Task:** enumerate your corpus by modality; compute raw size, estimated
token/patch counts, and CPU encode minutes using §1's table.

**Worked approach:**

```python
from pathlib import Path
from collections import defaultdict
import pandas as pd

COST = {  # (bytes/unit, tokens/unit, cpu_ms/unit) — from the deep-dive table
    "image": (150_000, 197, 80),
    "audio": (1_000_000, 3_000, 120),
    "video": (60_000_000, 1_500, 2_500),
}
EXT = {".jpg": "image", ".png": "image", ".wav": "audio", ".mp4": "video", ".mov": "video"}

rows = []
for p in Path("data/raw").rglob("*"):
    if p.suffix.lower() in EXT:
        m = EXT[p.suffix.lower()]
        b, t, ms = COST[m]
        rows.append({"modality": m, "units": 1, "bytes": p.stat().st_size,
                     "tokens": t, "cpu_ms": ms})
df = pd.DataFrame(rows).groupby("modality").agg(
    units=("units", "sum"), raw_gb=("bytes", lambda s: s.sum()/1e9),
    total_tokens=("tokens", "sum"), cpu_min=("cpu_ms", lambda s: s.sum()/60_000))
print(df)
```

**Pass criterion:** every file in `data/raw/` appears exactly once; no
extension maps to two modalities.

## 2. Level-placement drill (from 02-representation-levels)

**Task:** for each artifact below, say which level (raw/processed/embedding)
it belongs in and whether deleting it loses information: (a) `IMG.jpg`
rotated per EXIF, (b) its 224×224 JPEG, (c) its CLIP vector, (d) the
`settings_json` string, (e) a FAISS index built on (c).

**Worked approach:** (a) raw — it is a *view*, the original bytes are truth;
(b) processed — deletable, regenerable from (a)+settings; (c) embedding —
deletable, regenerable but costs encode time; (d) *metadata* — keep with the
unit, it is the regeneration recipe; (e) derived index — deletable, but
record the matrix hash it was built from or you cannot tell if it is stale.

## 3. Manifest bootstrap (from 03-metadata-handling)

**Task:** write `scripts/build_manifest.py` that walks `data/raw/`, extracts
EXIF for images, and writes the v1 manifest parquet with permissions applied.

**Worked approach:** reuse `exif_summary` and `make_unit` from file 03; the
only new logic is the walk (skip dotfiles), the hash (read in 1 MB chunks),
and the license default (`UNLICENSED` for your own files). Write an
exclusions parquet and print both counts. Then *delete* the parquet and
regenerate — determinism check: `sha256` of both runs must match.

## 4. Gap measurement (from 04-the-modality-gap)

**Task:** with your Week-04 text embeddings and any ≥20 CLIP image vectors,
produce the two-centroid table and one sentence interpreting it.

**Worked approach:** encode 20 processed images with
`CLIPModel.get_image_features`; reuse `centroid_cos`. Interpretation pattern:
"cross-modal centroid cosine is X while within-text is Y, so absolute
thresholds must be per-modality; ranking remains valid."

## 5. Capstone inventory (from 04-the-modality-gap)

**Task:** fill the 7-field inventory table for your corpus and commit it to
your capstone README under "Modality inventory".

**Worked approach:** derive counts from exercise 1's output; choose units
with the Week-06 lesson (smallest unit that still carries meaning); set
`sidecar` honestly — empty OCR/ASR plans are the #1 gap risk. Each empty
sidecar cell must name the week that fills it (Week 08 for ASR).

## Pitfalls recap

- Grouping by suffix without lowercasing — `.JPG` files silently vanish.
- Audit double-counts when a directory is a symlink into `data/raw`.
- Inventory units chosen per *file* for video — retrieval granularity is the sampled clip, not the container.

## 6. Capstone: the one-page corpus report

**Task:** combine exercises 1, 3, and 5 into `reports/corpus-report.md` —
modality cost table, manifest coverage (units with/without EXIF timestamps),
and the inventory table with every empty `sidecar` cell assigned a filling
week. Regenerate it with one command (`py scripts/build_manifest.py --report`)
so it never drifts from the data.

**Worked approach:** the script already computes everything; this exercise
is *assembly*: render the three tables from the same parquet the manifest
build wrote, assert no unit is missing `sha256` or `license`, and add a
footer line with the generation timestamp and manifest schema version.
Commit the report generator, not the report itself — the report is derived.

**Pass criterion:** a teammate can regenerate the identical report from a
fresh clone with only `py scripts/build_manifest.py --report`; both copies
hash to the same value.
