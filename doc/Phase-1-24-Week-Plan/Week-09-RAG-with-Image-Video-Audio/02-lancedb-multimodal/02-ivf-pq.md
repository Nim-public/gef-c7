# IVF-PQ — Product Quantization Mechanics and Knobs

**What you'll learn:** how IVF-PQ compresses vectors and trades recall for
speed, computed on a small example where every number is checkable, plus
the two build-time knobs (`num_partitions`, `num_sub_vectors`) and two
query-time knobs (`nprobe`, `refine_factor`).

## 1. PQ by hand on 8-dim vectors

```python
import numpy as np

# 4 sub-vectors of 2 dims each (m=4, d_sub=2); codebook of 256 centroids/sub-space
rng = np.random.default_rng(0)
X = rng.standard_normal((1000, 8)).astype(np.float32)

m, ksub = 4, 256
d_sub = X.shape[1] // m
codes = np.zeros((len(X), m), dtype=np.uint8)
codebooks = []
for j in range(m):
    sub = X[:, j*d_sub:(j+1)*d_sub]
    # 1-D k-means x2 for brevity; real PQ uses k-means per sub-space
    cent = sub[np.random.default_rng(j).choice(len(sub), ksub, replace=False)]
    dists = ((sub[:, None, :] - cent[None, :, :]) ** 2).sum(-1)
    codes[:, j] = dist.argmin(axis=1)
    codebooks.append(cent)

# storage: 1000 × 4 bytes (uint8 codes) + 4 × 256 × 2 floats (codebooks)
print(f"raw: {X.nbytes/1024:.0f} KB  vs  PQ: {codes.nbytes/1024:.0f} KB "
      f"+ {sum(c.nbytes for c in codebooks)/1024:.0f} KB")
```

Storage math: 8 floats (32 B) → 4 codes (4 B) = **8× compression**, plus a
fixed codebook cost. Memory, not FLOPs, is why PQ exists: FAISS-class
indexes live in RAM.

## 2. IVF: coarse quantizer first

```python
nlist = 16                                    # coarse cells
cent = X[np.random.default_rng(1).choice(len(X), nlist, replace=False)]
cell = ((X[:, None, :] - cent[None, :, :]) ** 2).sum(-1).argmin(axis=1)
```

Search visits only `nprobe` of the `nlist` cells → compute drops ~`nlist/nprobe`-fold;
recall depends on the query's true neighbors sitting in the visited cells.

## 3. The four knobs, honestly

| Knob | Stage | ↑ effect | Cost |
|---|---|---|---|
| `num_partitions` (nlist) | build | finer cells | slower build, more files |
| `num_sub_vectors` (m) | build | finer PQ, better recall | bigger codes (m bytes/vec) |
| `nprobe` | query | higher recall | linear query cost |
| `refine_factor` | query | rerank top candidates with true vectors | fetch cost |

```python
table.create_index(metric="cosine", vector_column_name="text_vec",
                   index_type="IVF_PQ",
                   num_partitions=64, num_sub_vectors=48)   # 384-d → 48 sub × 8-d
res = (table.search(q, vector_column_name="text_vec")
            .nprobe(16).refine_factor(5).limit(10).to_list())
```

Rule: `num_sub_vectors` = dim/8 for 384/512-d vectors; `nprobe` starts at
nlist/4; `refine_factor` 5–10 recovers most PQ error cheaply.

## 4. When *not* to compress

| Corpus size | Recommendation |
|---|---|
| < 100k × 512-d | flat (no index) — brute force is ~ms |
| 100k–1M | IVF, skip PQ or small m |
| > 1M or RAM-bound | IVF-PQ, sweep recall (file 03) |

Your capstone (~1k–10k units) is firmly in "flat" territory — build the
IVF-PQ *skills* here, use the flat path in the demo, and say so in the
decision memo. Compression is a scale tool, not a rite of passage.

## Exercises

1. Verify the 8× compression claim with the §1 code; then compute it for
   512-d, m=64 (and name the codebook cost).
2. Recall-by-hand: pick one query; find its true top-1 in flat; then search
   with nprobe=1 of 16 cells — when does it miss? (Answer: when the top-1
   lies in another cell — the IVF failure mode, observed not assumed.)
3. Refine ablation: flat vs IVF-PQ nprobe=16, refine ∈ {1, 5, 10}; report
   R@1 and latency for all three.

## Pitfalls

- `num_sub_vectors` not dividing the dim — build error; 384/8=48 ✓, 512/8=64 ✓.
- Sweeping nprobe on *trained* embeddings without fixed queries — recall numbers need a fixed query set and fixed ground truth.
- Reading "IVF-PQ is faster" as unconditional — at your scale flat wins; measure at your n.

## Resources

- LanceDB IVF-PQ docs (index params, nprobe/refine_factor).
- Jégou et al. 2011 (PQ), Johnson et al. 2019 (IVF) — the mechanics' originals.
