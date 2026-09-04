# 03.2 — FAISS Indexes

> Subfolder index: [README.md](README.md) · Parent: [../03-embeddings-vector-databases.md](../03-embeddings-vector-databases.md)

---

## What you'll learn

- Flat: exact search, zero tuning, the eval ground truth
- IVF: the clustering approach, the nprobe dial, the recall measurement
- The index-choice decision tree

## 1. Flat — exact, zero tuning

```python
import faiss, numpy as np

d = 384
index = faiss.IndexFlatIP(d)                    # inner product = cosine on normalized
index.add(emb.astype("float32"))                # (N, 384)

q = model.encode(["refund timeline"], normalize_embeddings=True).astype("float32")
scores, ids = index.search(q, k=5)
```

Properties: exact, deterministic, no training, no parameters. The eval ground truth — every ANN index is measured against this. Use up to ~100k vectors.

## 2. IVF — approximate, tuned

```python
nlist = 100                                     # number of clusters
quantizer = faiss.IndexFlatIP(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
index.train(emb.astype("float32"))              # k-means — needs ≥ ~30×nlist vectors
index.add(emb.astype("float32"))
index.nprobe = 10                               # search 10 of 100 cells

scores, ids = index.search(q, k=5)
```

The mechanics: k-means clusters the vectors into `nlist` cells; queries search only the `nprobe` nearest cells. The recall/speed trade:

| nprobe | Recall@5 (vs flat) | Speed |
|---|---|---|
| 1 | ~60% | fastest |
| 10 | ~95% | 10× faster than flat |
| 100 (=nlist) | 100% | = flat (no benefit) |

**Recall is a dial** (`nprobe`), not a property — measure it against flat on your eval set. The training requirement: ≥ ~30×nlist vectors, or the clustering is unstable.

## 3. The recall measurement protocol

```python
def measure_recall(flat_ids, ivf_ids, k=5):
    """Fraction of flat top-k found by IVF."""
    overlap = sum(len(set(f) & set(i)) for f, i in zip(flat_ids, ivf_ids))
    return overlap / (len(flat_ids) * k)

flat_ids = flat_index.search(q, 5)[1]
ivf_ids = ivf_index.search(q, 5)[1]
print(f"recall@5: {measure_recall(flat_ids, ivf_ids):.3f}")
```

The protocol: same queries, same k, both indexes — the overlap is the recall. Run on 100+ queries for stable numbers; report per-query variance, not just the mean.

## 4. The index-choice decision tree

```
N < 100k?           → Flat (exact, no tuning)
100k ≤ N ≤ 10M?     → IVFFlat (tune nprobe)
N > 10M?            → IVFPQ (compressed, file W9-02) or HNSW
Need exact always?  → Flat regardless of N
```

## Exercises

1. Latency scaling: flat search at N = 1k/10k/100k — the curve that justifies indexes.
2. The recall sweep: IVF at nprobe ∈ {1, 5, 10, 50} — recall@5 and latency; the knee table.
3. The training-size test: IVF trained on 1k, 5k, and 30k vectors at nlist=100 — compare recall; find the minimum training size.
4. The metric flip: search with L2 vs IP on the same normalized vectors — verify identical rankings; then on unnormalized — show they differ.
5. Memory audit: `index.ntotal`, `index.is_trained`, and the memory footprint per index type — the capacity planning numbers.

## Pitfalls

- **float64 into FAISS** — cryptic errors; always `.astype("float32")`
- **IVF not trained** — `index.is_trained` is False; search raises or returns garbage
- **nprobe=1 with nlist=100** — 1% recall; the default is too aggressive for quality
- **Metric mismatch** — L2 index with cosine-normalized vectors gives wrong distances (L2 ≠ cosine ranking on unnormalized data)
- **The index forgotten at rebuild** — corpus updated, index stale; rebuild on every ingestion (W4-05)

## Resources

- [FAISS wiki](https://github.com/facebookresearch/faiss/wiki) — *Getting started*, *Running on GPUs*, index choice
- Johnson et al., *Billion-scale similarity search with GPUs* — IVF/PQ internals
- W4-05 (the eval that measures recall)
