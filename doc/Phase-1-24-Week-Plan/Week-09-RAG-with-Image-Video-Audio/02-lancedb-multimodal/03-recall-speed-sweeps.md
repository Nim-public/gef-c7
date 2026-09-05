# Recall and Speed Sweeps — Against Flat Ground Truth

**What you'll learn:** the measurement methodology that turns index knobs
from folklore into numbers: build flat ground truth once, sweep `nprobe`/
`refine_factor`, and report recall@K with latency — the table your decision
memo cites.

## 1. Ground truth first, always

```python
import numpy as np, time, pandas as pd, lancedb

db = lancedb.connect("data/lancedb")
table = db["units"]
vecs = np.stack(table.to_pandas()["text_vec"].to_numpy())     # (N, 384)
queries = vecs[np.random.default_rng(0).choice(len(vecs), 50, replace=False)]

def flat_topk(Q: np.ndarray, X: np.ndarray, k: int) -> np.ndarray:
    Qn = Q / np.linalg.norm(Q, axis=1, keepdims=True)
    Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
    return np.argsort(-(Qn @ Xn.T), axis=1)[:, :k]

GT = flat_topk(queries, vecs, 10)                             # exact answers
```

GT is *cheap* at your scale (50×N×384 multiply) — build it once, reuse for
every sweep; it is also your regression baseline when the corpus changes.

## 2. The sweep, one table per report

```python
def ann_topk(q, table, k=10, nprobe=16, refine=1):
    s = table.search(q, vector_column_name="text_vec").limit(k).nprobe(nprobe)
    if refine > 1:
        s = s.refine_factor(refine)
    return [r["unit_id"] for r in s.to_list()]

rows = []
for nprobe in [1, 4, 16, 64]:
    for refine in [1, 5]:
        t0 = time.perf_counter()
        hits = [set(ann_topk(q, table, nprobe=nprobe, refine=refine)) for q in queries]
        dt = (time.perf_counter() - t0) / len(queries) * 1000
        recall = np.mean([len(h & set(g)) / 10 for h, g in zip(hits, GT)])
        rows.append({"nprobe": nprobe, "refine": refine,
                     "recall@10": round(float(recall), 3), "ms/q": round(dt, 2)})
print(pd.DataFrame(rows))
```

## 3. Reading the sweep table

| nprobe | refine | R@10 | ms/q | Read |
|---|---|---|---|---|
| 1 | 1 | 0.42 | 0.4 | unusable |
| 4 | 1 | 0.78 | 0.9 | cheap-and-decent |
| 16 | 1 | 0.94 | 2.1 | default pick |
| 16 | 5 | 0.99 | 3.4 | refine pays for itself |
| 64 | 5 | 0.99 | 7.8 | near-flat; why bother |

The decision rule: pick the cheapest cell with R@10 ≥ flat − 0.02; here
`nprobe=16, refine=5`. The *shape* matters more than any cell: if recall
rises steeply with nprobe at fixed latency budget, IVF is healthy; a flat
curve means your partitions are wrong for the data.

## 4. Regression discipline

Sweeps only mean something against a *fixed* query set and corpus version:

```text
reports/sweeps/2026-09-05-corpus-v3.md   ← commit the table + query seed
```

When the corpus changes, GT regenerates and the old table is historical —
never compare recall numbers across corpus versions (the Week-07
eval-harness rule, same trap).

## Exercises

1. Run the full sweep on your units table; produce the 5-row table with
   your own numbers; mark the chosen cell.
2. GT-vs-ANN drill: for 5 queries where ANN@nprobe=1 missed, inspect the
   true top-1's cell vs the query's cell — quantify "true neighbor in
   another cell" vs "PQ distortion" as failure causes.
3. Latency tail: re-run the chosen cell 5× and report p50/p95 — a single
   mean hides the OS-cache warm-up that your demo will hit once.

## Pitfalls

- Recall computed against a *different* k than the reported one — fix k=10 everywhere or the table lies.
- Sweeping with random *new* queries each run — queries are part of the fixture; seed them.
- Reporting ms/q from a cold process — warm up with 20 throwaway queries first.

## Resources

- Your Week-04/07 eval harness — same discipline, new engine.
- LanceDB docs on `nprobe`/`refine_factor` defaults and limits.
