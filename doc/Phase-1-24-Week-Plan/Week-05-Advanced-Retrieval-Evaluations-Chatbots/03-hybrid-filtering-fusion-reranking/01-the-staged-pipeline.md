# 03.1 — The Staged Pipeline Implementation

> Subfolder index: [README.md](README.md) · Parent topic: [../03-hybrid-filtering-fusion-reranking.md](../03-hybrid-filtering-fusion-reranking.md)

The full pipeline as runnable code — each stage a function, each stage measured:

```python
def advanced_search(query: str, k: int = 5) -> dict:
    # Stage 1: filter extraction (LLM)
    filters = extract_filters(query)                    # {"doc_type": "policy", ...}

    # Stage 2: query expansion (fusion)
    sub_queries = [query] + decompose(query, n=3)

    # Stage 3: parallel retrieval per sub-query
    all_rankings = []
    for sq in sub_queries:
        bm25_hits = bm25_search(sq, k=10, filters=filters)
        vec_hits = vector_search(sq, k=10, filters=filters)
        all_rankings.append([h["id"] for h in bm25_hits])
        all_rankings.append([h["id"] for h in vec_hits])

    # Stage 4: RRF fusion
    fused = rrf(all_rankings)[:20]                      # top-20 candidates

    # Stage 5: cross-encoder rerank
    candidates = fetch_full(fused)
    reranked = rerank(query, candidates, top_k=k)

    # Stage 6: threshold check
    if not reranked or reranked[0]["rerank_score"] < THRESHOLD:
        return {"hits": [], "caveat": "No strong matches."}
    return {"hits": reranked, "filters": filters, "sub_queries": sub_queries}
```

The ablation table measures each stage's contribution:

| Config | Hit@5 | p95 ms |
|---|---|---|
| W4 baseline (hybrid RRF) | | |
| + prefilter | | |
| + fusion (3 sub-queries) | | |
| + reranker | | |

Each row = the pipeline minus one stage. The attribution tells you which stage earns its latency.

## Exercises

1. Implement `advanced_search` with all 6 stages; measure per-stage latency and the end-to-end p95.
2. The ablation: remove each stage; measure the hit-rate drop; rank stages by contribution.
3. The escalation integration: connect the rerank score threshold to the W5-04 confidence hook — measure the escalation rate on benign traffic.

## Pitfalls

- **Stages tested in isolation** — the composition may introduce new failure modes (filter too strict → fusion has nothing to fuse)
- **The reranker re-scoring already-scored results** — if the bi-encoder already ranked well, the reranker adds latency without gain; measure before adopting
- **Fusion without dedup** — the same chunk from multiple sub-queries double-counts; RRF handles this, naive union doesn't

## Resources

- W5-03 parent, W4-04 (RRF), W4-05 (the harness) — composed here
- LangGraph (W13) — the graph-native version of this pipeline
