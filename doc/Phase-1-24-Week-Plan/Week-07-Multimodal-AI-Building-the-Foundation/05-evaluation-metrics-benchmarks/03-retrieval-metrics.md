# Retrieval Metrics — R@1/5/10, MedR, Both Directions

**What you'll learn:** the metrics that decide whether your multimodal RAG
works: Recall@K and Median Rank, computed in both query directions, with the
pool-size subtlety that makes your numbers comparable (or not).

## 1. The setup: two directions, always

Cross-modal retrieval has two query directions and they are *not* equivalent:

- **text→image**: query = caption; corpus = images. (RAG default.)
- **image→text**: query = image; corpus = captions. (Mirror eval.)

Report both; a model can be good one way and mediocre the other (training
objective asymmetries, caption length effects).

```python
import numpy as np

def ranks_for_queries(Q: np.ndarray, C: np.ndarray,
                      gt: np.ndarray) -> np.ndarray:
    """Q: (Nq, D) queries; C: (Nc, D) candidates; gt: (Nq,) index of the
    relevant candidate per query. Returns rank (1-based) of gt per query."""
    Q = Q / np.linalg.norm(Q, axis=1, keepdims=True)
    C = C / np.linalg.norm(C, axis=1, keepdims=True)
    sims = Q @ C.T                       # (Nq, Nc)
    order = np.argsort(-sims, axis=1)
    pos = np.arange(len(Q))[:, None]     # candidate axis
    rank_of_gt = (order == gt[:, None]).argmax(axis=1) + 1
    return rank_of_gt
```

## 2. The metric implementations

```python
def recall_at_k(ranks: np.ndarray, k: int) -> float:
    return float((ranks <= k).mean())

def median_rank(ranks: np.ndarray) -> float:
    return float(np.median(ranks))

def report(ranks_t2i: np.ndarray, ranks_i2t: np.ndarray) -> dict:
    return {
        "t2i": {f"R@{k}": round(recall_at_k(ranks_t2i, k), 3) for k in (1, 5, 10)}
               | {"MedR": median_rank(ranks_t2i)},
        "i2t": {f"R@{k}": round(recall_at_k(ranks_i2t, k), 3) for k in (1, 5, 10)}
               | {"MedR": median_rank(ranks_i2t)},
    }
```

| Metric | Question it answers | Bad value looks like |
|---|---|---|
| R@1 | "is the top hit right?" | demo shows wrong image first |
| R@5 | "is it in the first page?" | user scrolls, finds it, loses trust |
| R@10 | "is it findable at all?" | corpus useless for the task |
| MedR | typical rank (robust to outliers) | tail cases: mean rank hides them |

## 3. Pool size: the comparability trap

R@1 on a 50-image pool and R@1 on a 5,000-image pool are different metrics
wearing the same name. The paper-standard protocol on COCO is **5,000-image
pools**; smaller pools inflate every number.

```python
def fixed_pool_eval(Q: np.ndarray, C: np.ndarray, gt: np.ndarray,
                    pool: int = 1000, seed: int = 42) -> np.ndarray:
    """Standard protocol: keep gt, fill the rest with a fixed random pool."""
    rng = np.random.default_rng(seed)
    n_c = C.shape[0]
    assert n_c := n_c  # pool <= corpus size
    ranks = []
    for i in range(len(Q)):
        others = [j for j in range(n_c) if j != gt[i]]
        distractors = rng.choice(others, size=pool - 1, replace=False)
        cand_idx = np.concatenate([[gt[i]], distractors])
        r = ranks_for_queries(Q[i:i+1], C[cand_idx], gt=np.array([0]))
        ranks.append(r[0])
    return np.array(ranks)
```

Fixed seed + fixed pool = reproducible, comparable numbers. Change either and
your eval set is a *different* eval set — record `(pool, seed, corpus_hash)`
in the report header next to the numbers.

## 4. Beyond exact-match: multiple relevant candidates

A caption has 5 references (COCO); a moment in a video has a ±2 s span. Two
upgrades, in order of honesty:

```python
def ranks_multi_gt(Q: np.ndarray, C: np.ndarray, gt_sets: list[set]) -> np.ndarray:
    """Rank of the BEST relevant candidate per query."""
    Q = Q / np.linalg.norm(Q, axis=1, keepdims=True)
    C = C / np.linalg.norm(C, axis=1, keepdims=True)
    order = np.argsort(-(Q @ C.T), axis=1)
    out = np.empty(len(Q), dtype=int)
    for i, o in enumerate(order):
        hits = np.flatnonzero(np.isin(o, list(gt[i])))
        out[i] = (hits[0] + 1) if len(hits) else len(o)
    return out
```

- **Multi-GT R@K** — any of the 5 captions counts (standard for COCO).
- **Span GT** (your video alignment) — a hit is any frame within the
  temporal window from the alignment parquet; without it, R@K on video is
  a coin flip measured wrong.

## 5. The capstone report format

```text
# Retrieval eval — corpus v3 — pool=1000 seed=42 — 2026-09-05

| direction | R@1 | R@5 | R@10 | MedR |
|---|---|---|---|---|
| text→image | 0.42 | 0.71 | 0.83 | 3 |
| image→text | 0.38 | 0.66 | 0.79 | 4 |

Change since last run: re-encoded with settings v3 (+0.05 R@1).
```

One table, both directions, pool/seed header, and a delta line. Anything
less and next week's number is not comparable to this week's.

## Exercises

1. Sanity-check `ranks_for_queries` with a synthetic set where gt is always
   the top match → R@1 must be 1.0; then add one distractor closer than gt
   for half the queries and predict R@1 = 0.5 before running.
2. Pool-size sensitivity: R@1 at pool ∈ {50, 200, 1000, 5000} on your
   mini-benchmark; plot and write the comparability caveat into your report
   template.
3. Implement span-GT eval for video: using alignment parquet windows, compute
   R@5 where a hit is any sampled frame within ±2 s of the ground-truth moment.

## Pitfalls

- Ties in similarity broken by `argsort` order — shuffle candidate order (fixed seed) or ties systematically favor low indices.
- Reporting mean rank — a few catastrophic queries (rank 4,000) dominate the mean; MedR + R@K instead.
- Evaluating on the indexing corpus — 200 test pairs must be *held out* from the indexed corpus or every number is inflated.

## Resources

- COCO evaluation protocol (Karpathy & Fei-Fei 2015 splits, 1k/5k pools).
- Your alignment parquet for span ground truth:
  [`../04-data-alignment-synchronization/`](../04-data-alignment-synchronization/).
