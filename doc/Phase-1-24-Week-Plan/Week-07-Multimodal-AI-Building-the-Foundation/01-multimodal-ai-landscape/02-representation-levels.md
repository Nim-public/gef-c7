# Representation Levels — Raw / Processed / Embeddings Storage Strategy

**What you'll learn:** a single, defensible on-disk layout for all four
modalities, what each level costs, and which level your pipeline should cache.

## 1. The three levels

| Level | What it is | Size (1 h corpus) | Regeneration cost | Keep? |
|---|---|---|---|---|
| **Raw** | Original bytes, untouched | ~2–6 GB | n/a (irreplaceable) | always, immutable |
| **Processed** | Normalized arrays: 224×224 JPEGs, 16 kHz WAVs, sampled frames | ~0.5–1.5 GB | minutes, deterministic | until stable |
| **Embeddings** | Fixed vectors + metadata | ~20–80 MB | minutes + model version | always, versioned |

The deciding question per level: *can I regenerate it exactly, and how long
does that take?* Raw is the source of truth; processed is a cache keyed by
(settings + library version); embeddings are a cache keyed by (model version
+ processor version + input hash). Everything in `data/processed/` and
`data/embeddings/` must be **deletable without data loss**.

## 2. A layout that survives the capstone

```text
data/
  raw/
    images/            # original files, sha256 in manifest
    audio/
    video/
  processed/
    images-224/        # <stem>.jpg   (CLIP preproc)
    audio-16k/         # <stem>.wav   (mono PCM16)
    video-keyframes/   # <stem>/f0001.jpg ...
  embeddings/
    clip-vit-b32/      # .npy per unit + index.json (model, hash, mapping)
    minilm-l6/
  manifests/
    corpus-manifest.parquet
```

```python
from pathlib import Path
import hashlib, json

def unit_key(rel_path: str, settings: dict) -> str:
    """Cache key = content + processing settings, not just filename."""
    h = hashlib.sha256(f"{rel_path}|{json.dumps(settings, sort_keys=True)}".encode())
    return h.hexdigest()[:16]

key = unit_key("raw/images/figure3.png",
               {"size": 224, "mean": [0.485, 0.456, 0.406]})
# processed path: data/processed/images-224/<key>.jpg
# embeddings path: data/embeddings/clip-vit-b32/<key>.npy
```

## 3. Embedding storage: parquet vs npy + sidecar

```python
import numpy as np, pandas as pd

# Option A: one .npy per unit — simple, memory-mappable, no schema churn.
vecs = np.load("data/embeddings/clip-vit-b32/ab12cd34.npz")["emb"]  # (197+1, 512)

# Option B: one matrix for the whole corpus + row mapping (what FAISS wants).
matrix = np.load("data/embeddings/clip-vit-b32/matrix.npy")          # (N, 512)
meta  = pd.read_parquet("data/manifests/corpus-manifest.parquet")
assert len(meta) == matrix.shape[0]  # row i of matrix == row i of manifest
```

For the capstone, use **Option B**: a single `(N, 512)` float32 matrix plus a
parquet manifest whose row order *is* the matrix row order. That invariant
(`len(meta) == matrix.shape[0]`, and `meta.iloc[i]` describes `matrix[i]`) is
the single most useful assertion in a multimodal repo — write it as a test.

## 4. When processed beats raw at read time

| Situation | Read from | Why |
|---|---|---|
| Re-encoding with new settings | raw | processed was built under old settings |
| Training/eval loops (many epochs) | processed | skip decode+normalize every step |
| Indexing into FAISS | embeddings | decoded pixels never enter RAM |
| Answering "what exactly was in the original?" | raw | only immutable source |

Processed files are a *performance* artifact; embeddings are a *semantic*
artifact. Confusing the two leads to the classic bug: re-encoding embeddings
because "the images changed" when only normalization settings changed — the
content hash in `unit_key` catches this for free.

## Exercises

1. Your disk budget is 5 GB for a corpus of 300 images (2 MB each), 100 audio
   clips (5 min each), and 20 videos (30 min each @ 4 Mbps). Fill the three
   levels with numbers and decide what processed artifacts you can afford.
2. Write `rebuild_processed(manifest, settings)` pseudocode that regenerates
   the processed level from raw for changed settings only (hint: compare
   stored `settings_json` per unit).
3. Prove the row-alignment invariant: load `matrix.npy` and the manifest,
   assert shape agreement, then spot-check three rows by re-encoding from
   processed files and comparing cosine similarity > 0.999.

## Pitfalls

- Storing embeddings as float64 — doubles size for zero accuracy gain; use float32 (float16 for FAISS-IVF experiments).
- Cache keys without settings — silent staleness when normalization changes.
- Reordering the manifest after building the matrix — mislabeled vectors forever.

## Resources

- NumPy memory mapping (`np.load(..., mmap_mode="r")`) for matrices larger than RAM.
- Apache Parquet for manifests; `pyarrow` docs on nested metadata columns.
