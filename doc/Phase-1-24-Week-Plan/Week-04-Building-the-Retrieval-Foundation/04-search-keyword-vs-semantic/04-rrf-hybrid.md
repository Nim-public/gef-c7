# 04.4 — RRF Hybrid

> Subfolder index: [README.md](README.md) · Parent: [../04-search-keyword-vs-semantic.md](../04-search-keyword-vs-semantic.md)

---

## What you'll learn

- RRF: the rank-based fusion formula, derived and implemented
- The k parameter: what it controls and how to tune it
- The hybrid architecture: two arms, one ranking
- Score calibration: why ranks, not scores

## 1. The formula

```
RRF(d) = Σ_systems  1 / (k + rank_system(d))
```

For each document d, sum `1/(k + rank)` across all retrieval systems. A document ranked 1st by both systems scores `2/(k+1)`; a document ranked 1st by one and absent from the other scores `1/(k+1)`.

| Parameter | Effect |
|---|---|
| `k` | dampens the influence of top ranks; k=60 is the standard |
| number of systems | more systems = more coverage, more noise |

The k intuition: k=60 means rank-1 contributes `1/61 ≈ 0.016` while rank-10 contributes `1/70 ≈ 0.014` — the difference is small, so being ranked 1st vs 10th matters less than being *present*. Higher k flattens further; lower k makes top ranks dominate.

## 2. The implementation

```python
def rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return dict(sorted(fused.items(), key=lambda kv: -kv[1]))

bm25_top = [doc["id"] for doc in bm25_search(query, k=10)]
sem_top  = [doc["id"] for doc in semantic_search(query, k=10)]
fused = list(rrf([bm25_top, sem_top]).items())[:5]
```

The hybrid: BM25 catches exact identifiers and keyword matches; semantic catches paraphrases and intent; RRF merges without score calibration (the reason ranks, not scores — BM25 scores ~0–20, cosine ~0–1, incomparable directly).

## 3. Why ranks, not scores

| System | Score range | Score meaning |
|---|---|---|
| BM25 | 0–20+ | term-frequency based |
| Cosine | 0–1 | angular similarity |
| Cross-encoder | −10 to 10 | learned relevance |

Score-based fusion (weighted sum) requires calibrating scores to a common scale — fragile and model-dependent. Rank-based fusion only needs the *order* within each system — robust across scoring schemes.

## 4. The hybrid architecture (two arms, one ranking)

```
query ─┬─► BM25 index ────► top-10 by BM25 score ──┐
       │                                           ├──► RRF ──► top-5 ──► LLM
       └─► vector index ─► top-10 by cosine ───────┘
```

Each arm covers the other's blind spots: identifiers (BM25) and paraphrases (semantic). The fused ranking is more robust than either alone — the measurement (file 03's harness) proves it on your corpus.

## Exercises

1. RRF by hand: two rankings of 5 documents with 3 overlapping — compute the fused scores manually; verify against the code.
2. The k-sweep: k ∈ {1, 10, 60, 500} — how does the fused ranking change? At what k does the top-rank dominance appear?
3. The coverage measurement: for 25 queries, how many have the correct doc in the BM25 top-10, the semantic top-10, and the fused top-5? The union coverage is the hybrid's value.
4. The three-arm hybrid: add a third arm (cross-encoder reranker scores) to the RRF — does the three-way fusion beat the two-way?
5. The k-vs-depth trade: with k=10 per arm, sweep the RRF k parameter — find where top-rank dominance starts distorting the fusion.

## Pitfalls

- **Score-based fusion without calibration** — summing BM25 and cosine scores mixes incompatible scales; ranks are scale-free
- **Duplicated documents across arms** — the same doc from both systems gets double-counted; RRF handles this naturally (the score adds), but verify
- **Empty arm results** — one system returning nothing shouldn't break the fusion; handle empty rankings
- **Rank ties** — two docs at the same rank get the same RRF contribution; break ties deterministically (by id)
- **The fusion evaluated on the training queries** — the k parameter tuned on eval queries overfits; validate on held-out queries

## Resources

- Cormack et al., *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods* — the RRF paper
- W4-04 parent (the comparison framework), W5-03 (the reranking stage after fusion) — composed here
- LanceDB [`query_type="hybrid"`](https://lancedb.github.io/lancedb/) — the native hybrid (W9-02)
