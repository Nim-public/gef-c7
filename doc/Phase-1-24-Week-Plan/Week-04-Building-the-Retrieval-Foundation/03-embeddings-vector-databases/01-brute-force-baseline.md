# 03.1 — Brute-Force Baseline

> Subfolder index: [README.md](README.md) · Parent: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md)

---

## What you'll learn

- The NumPy baseline that defines correctness for every index
- The memory and latency limits that motivate indexes
- The baseline as the eval's ground truth

## 1. The implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
corpus = ["chunk text one", "chunk text two", "..."]       # from W4-02
emb = model.encode(corpus, normalize_embeddings=True)       # (N, 384)

def brute_search(query: str, k: int = 5) -> list[tuple[int, float]]:
    q = model.encode([query], normalize_embeddings=True)[0]
    sims = emb @ q                                          # cosine = dot on normalized
    top = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in top]
```

Three properties: **exact** (every vector compared), **deterministic** (same input → same ranking), **simple** (no tuning). The baseline that all indexes are measured against.

## 2. The limits, measured

| N vectors | Memory (384-d, fp32) | Search time (1 query) |
|---|---|---|
| 1k | 1.5 MB | ~0.1 ms |
| 10k | 15 MB | ~1 ms |
| 100k | 150 MB | ~10 ms |
| 1M | 1.5 GB | ~100 ms |

The crossover: below ~100k vectors, brute force is fast enough — an index adds complexity without benefit. Above 1M, the 100 ms search breaches any interactive SLA. The FAISS index (file 02) trades a little recall for a big speedup.

## 3. The baseline as ground truth

The W4-05 eval set (25 queries) run through brute force produces the **exact** top-k for every query. This is the reference that:

- validates IVF recall (file 02's sweep)
- validates LanceDB's ANN (file 03)
- defines the "correct" answer for the eval set
- catches embedding drift (any change in embeddings shifts the ground truth)

## Exercises

1. Latency scaling: brute-force search at N = 1k/10k/100k — measure per-query time; plot the curve.
2. The determinism check: same query, 10 runs — identical results (they must be — no randomness in the math).
3. The normalization proof: unnormalized vectors with dot-product vs L2 — show the rankings differ; then normalize and show they match.
4. Memory measurement: `emb.nbytes` at N = 1k/10k/100k — verify the formula `N × 384 × 4 bytes`.
5. The drift canary: change one corpus embedding slightly; measure the top-k shift — the sensitivity baseline for detecting index drift.

## Pitfalls

- **Forgetting `normalize_embeddings=True`** — dot ≠ cosine; the rankings silently differ (W4-03's rule)
- **int64 vs float32** — NumPy defaults to float64; FAISS wants float32; the conversion must be explicit
- **argsort stability** — `np.argsort` is not stable by default; use `kind="stable"` for reproducible ties
- **The baseline forgotten** — without it, IVF recall claims are unverified
- **In-memory only** — process restart reloads everything; persist or accept the reload cost

## Resources

- W4-02 (the chunks), W4-05 (the eval set) — the inputs
- NumPy [sorting](https://numpy.org/doc/stable/reference/generated/numpy.argsort.html) — stability and performance
- W4-03 parent (the indexes that build on this baseline)
