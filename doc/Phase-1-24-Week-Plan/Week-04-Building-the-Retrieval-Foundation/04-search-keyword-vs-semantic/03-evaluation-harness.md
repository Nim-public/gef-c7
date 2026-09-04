# 04.3 — The Evaluation Harness

> Subfolder index: [README.md](README.md) · Parent: [../04-search-keyword-vs-semantic.md](../04-search-keyword-vs-semantic.md)

---

## What you'll learn

- The harness: eval set format, metrics, runner — reusable across all retrieval changes
- Hit rate, MRR, and precision@k — the three metrics and when each matters
- The harness as the adoption gate for every future change

## 1. The eval set format

```json
{"query": "How do I reset my password?", "relevant_ids": ["handbook::chunk:12", "faq::chunk:03"]}
{"query": "E-4021 error meaning", "relevant_ids": ["errors::chunk:07"]}
{"query": "What changed in the refund policy?", "relevant_ids": ["policy::chunk:02", "policy::chunk:05"]}
```

Each case: a query + the hand-labeled relevant chunk ids. The labels come from: reading the corpus and marking what SHOULD be retrieved (not what WAS retrieved — that's circular). 25–50 cases for stable signals; 100+ for fine-grained comparisons.

## 2. The metrics

```python
def hit_rate_at_k(results, relevant, k):
    """Did a relevant chunk appear in top-k?"""
    return bool(set(results[:k]) & set(relevant))

def mrr(results, relevant, max_k=10):
    """Mean Reciprocal Rank — 1/rank of the first relevant result."""
    for rank, r in enumerate(results[:max_k], 1):
        if r in relevant: return 1.0 / rank
    return 0.0

def precision_at_k(results, relevant, k):
    """Fraction of top-k that are relevant."""
    return len(set(results[:k]) & set(relevant)) / k
```

| Metric | Question | Sensitive to |
|---|---|---|
| Hit rate @k | is the answer findable? | chunking, embedding quality |
| MRR | how high does the right answer rank? | reranking quality |
| Precision @k | how much noise in the top-k? | k selection, threshold |

Hit rate is the screening metric (does it work at all?); MRR is the tuning metric (is the ranking good?); precision@k is the serving metric (is the pasted context clean?). Report all three; optimize the one that matches your failure.

## 3. The harness runner

```python
def run_harness(search_fn, eval_set, k=5) -> dict:
    hit_rates, mrrs, precisions = [], [], []
    for case in eval_set:
        results = search_fn(case["query"], k=k)
        ids = [r["id"] for r in results]
        rel = set(case["relevant_ids"])
        hit_rates.append(hit_rate_at_k(ids, rel, k))
        mrrs.append(mrr(ids, rel))
        precisions.append(precision_at_k(ids, rel, k))
    return {"hit_rate": mean(hit_rates), "mrr": mean(mrrs),
            "precision@k": mean(precisions), "n": len(eval_set)}
```

The harness takes any `search_fn(query, k) -> list[dict]` — your W4 engine, W5's upgrade, LlamaIndex, or any future system. The interface is the stability point.

## 4. The harness as the adoption gate

Every retrieval change (chunking, embedding, routing, new index type) runs through the harness:

| Change | Harness result | Decision |
|---|---|---|
| new embedder | hit_rate 0.72 → 0.78 | adopt |
| new chunker | hit_rate 0.72 → 0.68 | reject |
| new reranker | MRR 0.58 → 0.71 | adopt |
| larger k | precision ↓, hit_rate ↑ | tune with cost model |

The harness converts retrieval engineering from opinion to measurement — the discipline that makes the capstone's retrieval claims auditable.

## Exercises

1. Build the harness (§3) with your 25-query eval set; verify the baseline numbers match your W4-05 results.
2. The metric comparison: for 10 queries, compute all three metrics; identify cases where hit_rate and MRR disagree — the ranking-quality cases.
3. The eval-set growth: add 10 real user questions (from your logs, W10-04); re-run — does the pass rate change? (Distribution shift in the eval set.)
4. The A/B framework: implement `compare(system_a, system_b, eval_set)` that reports per-metric deltas with a sign test — the statistical significance check.
5. The eval-set audit: for each query, check the relevant_ids are actually relevant (hand-verify 5); fix the labels — does the pass rate change?

## Pitfalls

- **Eval set = retrieval training set** — the harness tests what it was built on; hold out queries (W16-02's leakage check)
- **Relevant labels not verified** — wrong labels make the harness measure noise; hand-verify a sample
- **Single-k reporting** — report @1, @5, @10; the k-selection depends on the shape of the curve, not one point
- **No baseline** — every number needs a comparison; the W4 baseline is the reference
- **The harness drifts from production** — production queries ≠ eval queries; refresh the eval set quarterly from real traffic

## Resources

- W4-05 (the task that consumes this harness), W5-03 (the reranking that MRR measures), W16-01 (the versioning)
- [BEIR benchmark](https://arxiv.org/abs/2104.08663) — the retrieval evaluation methodology at scale
- W10-04 (the trajectory metrics) — the harness's runtime counterpart
