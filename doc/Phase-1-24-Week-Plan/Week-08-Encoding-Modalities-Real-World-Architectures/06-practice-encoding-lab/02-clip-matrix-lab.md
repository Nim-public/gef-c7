# CLIP Matrix Lab — Contrastive Matrix and Retrieval Metrics on Your Pairs

**What you'll learn:** build the full N×N CLIP similarity matrix on your
image-caption pairs, read its block structure, and produce the Week-07
retrieval metrics — the lab that closes the loop between Week 07's eval
harness and Week 08's model.

## 1. The matrix

```python
import numpy as np, torch, torch.nn.functional as F
from PIL import Image
from pathlib import Path
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

@torch.no_grad()
def clip_matrix(image_paths: list[str], captions: list[str]) -> np.ndarray:
    ii = proc(images=[Image.open(p).convert("RGB") for p in image_paths],
              return_tensors="pt", padding=True)
    ti = proc(text=captions, return_tensors="pt", padding=True, truncation=True)
    ie = F.normalize(model.get_image_features(**ii), dim=-1)
    te = F.normalize(model.get_text_features(**ti), dim=-1)
    return (ie @ te.T).numpy()                    # (N_img, N_txt)

pairs = load_pairs("data/manifests/mini-benchmark.parquet")   # your held-out pairs
S = clip_matrix([p.image_path for p in pairs], [p.caption for p in pairs])
```

## 2. Reading the matrix: three diagnostics

| Diagnostic | Code intuition | What it tells you |
|---|---|---|
| Diagonal dominance | `mean(S[i,i] − max offdiag row i)` | retrieval headroom per pair |
| Row vs col spread | std of rows vs cols | modality gap (Week-07 file) in your data |
| Duplicate block | near-identical rows | duplicate captions polluting the eval |

```python
def diagnostics(S: np.ndarray) -> dict:
    n = len(S)
    off_max = S - np.eye(n) * S.max()
    return {
        "diag_margin": float((np.diag(S) - off_max.max(axis=1)).mean()),
        "row_std": float(S.std(axis=1).mean()),
        "col_std": float(S.std(axis=0).mean()),
        "near_dup_rows": int((np.abs(S - S[0]).sum(axis=1) < 0.01).sum() - 1),
    }
```

## 3. Retrieval metrics both directions

The Week-07 metric implementations apply unchanged — `ranks_for_queries` on
`S` with `gt = arange(n)` (pair i is image i's caption):

```python
from eval_metrics import ranks_for_queries, recall_at_k, median_rank

r_t2i = ranks_for_queries(te, ie, np.arange(n))     # captions find images
r_i2t = ranks_for_queries(ie, te, np.arange(n))     # images find captions
report = {"t2i_R@1": (r_t2i <= 1).mean(), "i2t_R@1": (r_i2t <= 1).mean(),
          "t2i_MedR": int(np.median(r_t2i)), "i2t_MedR": int(np.median(r_i2t))}
```

Report at pool = full n (your mini-benchmark is 200–500 — the pool *is* the
corpus here; the fixed-pool protocol matters only when comparing to external
numbers).

## 4. From matrix to index: the capstone seam

This matrix *is* your multimodal index in miniature: `te` is the query
encoder, `ie` the index vectors. Everything Week-09+ builds (FAISS, fusion,
rerank) operates on these two matrices. Save them with the manifest-hash
discipline:

```python
np.save("data/embeddings/clip-b32/lab-matrix-img.npy", ie)
np.save("data/embeddings/clip-b32/lab-matrix-txt.npy", te)
```

## Exercises

1. Run the diagnostics on your pairs; if `near_dup_rows` > 0, dedupe and
   re-run — duplicates in eval pairs are a Week-07 manifest bug surfacing.
2. Compute the 4-metric report both directions; compare with the benchmark
   expectations (t2i usually beats i2t at equal N) and explain any inversion.
3. Prompt-side ablation: recompute the matrix with captions vs
   template-wrapped captions ("a photo of …"); report the Δdiag-margin —
   the zero-shot lesson (file 04) measured on your own data.

## Pitfalls

- Normalizing *after* the matrix multiply — normalize embeddings first, or the cosine is wrong in both directions.
- Eval pairs whose captions came from the *same* source doc as indexed units — leakage; the held-out rule from Week 07 applies.
- Reporting R@K without the pair count n — with n=20 vs n=500, R@5 means different things; state n in every table header.

## Resources

- Your Week-07 metrics: [`../../Week-07-Multimodal-AI-Building-the-Foundation/05-evaluation-metrics-benchmarks/`](../../Week-07-Multimodal-AI-Building-the-Foundation/05-evaluation-metrics-benchmarks/).
- CLIP model card — expected similarity ranges for sanity-checking the matrix.
