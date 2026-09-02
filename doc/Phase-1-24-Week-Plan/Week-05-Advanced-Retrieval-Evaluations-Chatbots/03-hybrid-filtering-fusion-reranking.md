# 03 — Advanced Retrieval: Filtering, Fusion, Reranking

> Week 5 index: [README.md](README.md)

**Session topics:** *Advanced retrieval: Hybrid search and filtering (S1) · Introduction to RAG fusion and retrieval re-ranking (S1) · Integrating Fusion & Re-ranking (practical sketch) (S2)*

---

## What you'll learn

- Metadata filtering: pre-filter vs post-filter and the permission pattern
- RAG fusion: one question becomes many, retrieval becomes coverage
- Cross-encoder reranking: the biggest single quality jump in most pipelines
- A reference architecture stacking all three on Week 4's engine

## 1. Filtering: retrieval with constraints

Real queries carry constraints the embedding can't see: "policy docs only", "updated this year", "docs I'm allowed to see". Metadata filters (LanceDB `where`, file 03) handle it:

```python
hits = (table.search(q_vec)
        .where("(doc_type = 'policy') AND (updated >= '2025-01-01')", prefilter=True)
        .limit(10).to_list())
```

**Prefilter vs postfilter** — prefilter restricts candidates *before* ANN search (correct for permissions: a forbidden doc must never even be a candidate); postfilter trims results *after* (can return nothing when valid matches exist further out). Security-critical filters are always prefilter.

**Auto-filters** — let an LLM turn the question into the filter (cheap, powerful, test heavily):

```python
FILTER_PROMPT = """Extract search filters as JSON from the question.
Schema: {"doc_type": "policy|faq|ticket", "year_min": 2024, "region": "<string|null>"}
Question: {q}
JSON:"""
# {"region": null} -> omit the filter entirely
```

Failure mode to test: over-constraining ("from last year's refund doc" → filters away the answer). Always fall back to unfiltered search when filtered returns < threshold.

## 2. RAG fusion: one question becomes several

Users ask vague questions; chunks answer specific ones. **Fusion** (a.k.a. multi-query retrieval) uses the LLM to expand the question into 3–5 independent search queries, then merges results:

```python
FUSE_PROMPT = """Generate 4 alternative search queries for this question.
Cover different phrasings and sub-questions. One per line.

Question: {q}"""

def fused_search(query, k=5):
    alts = client.chat.completions.create(
        model="gpt-4o-mini", temperature=0.7,
        messages=[{"role": "user", "content": FUSE_PROMPT.format(q=query)}],
    ).choices[0].message.content.splitlines()

    rankings = [bm25_search(q, 10) and [h["id"] for h in bm25_search(q, 10)] for q in [query, *alts]]
    rankings += [[h["id"] for h in vector_search(q, k=10)] for q in [query, *alts]]
    return rrf(rankings)[:k]        # same RRF as Week 4, now over 8–10 lists
```

Wins: covers synonyms the user didn't say ("refund timeline" + "how long until money back" + "payout duration"), catches the multi-part question ("compare A and B" → one query per side). Costs: +1 LLM call (~300–500 ms) and 4× retrieval per question — cheap, since retrieval is the cheap part.

## 3. Reranking: the quality multiplier

**The two-stage insight**: bi-encoder retrieval (embed query & docs *independently*, compare vectors) is fast but coarse; a **cross-encoder** reads query+chunk *together* and scores true relevance — 100× slower per pair, so you can't run it on 1M chunks, but you absolutely can on 20–50 *candidates*:

```
corpus (1M chunks) ─► bi-encoder retrieval (top 20–50) ─► cross-encoder rerank ─► top 5 ─► LLM
                        fast, approximate                      slow, accurate
```

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, candidates: list[dict], top_k=5) -> list[dict]:
    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)                 # one score per (query, chunk) pair
    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)
    return sorted(candidates, key=lambda c: -c["rerank_score"])[:top_k]
```

- Pairs with the fusion output of §2: **fusion widens recall (top-50), reranker sharpens precision (top-5)** — complementary, both cheap
- Alternatives: `BAAI/bge-reranker-base` (strong, multilingual), Cohere Rerank API (managed, no hosting), ColBERT-class late-interaction (the frontier — Week 5+ reading)
- Latency: MiniLM cross-encoder ≈ 5–20 ms/pair CPU → 20 candidates ≈ 200–400 ms. Budget it; it's usually the best ms-per-quality-point you can buy

## 4. Reference architecture (Week 4 engine, upgraded)

```
query ─► [filter extractor: metadata JSON]                    (§1)
      ─► [query expansion: 4 alternates]                      (§2)
      ─► per-query: BM25 top-20 + vector top-20  (prefiltered) (§1)
      ─► RRF fuse ─► top 50
      ─► cross-encoder rerank ─► top 5
      ─► context assembly ─► grounded LLM answer (W4-01 prompt)
```

Each stage is independently ablatable — that's the point of the harness:

| Config | Hit rate @5 | p95 latency |
|---|---|---|
| W4 baseline (hybrid RRF) |  |  |
| + prefilter |  |  |
| + fusion |  |  |
| + reranker |  |  |

Add one stage at a time, measure, keep the winner. Some stages will *not* earn their latency on your corpus — that's a finding, not a failure.

## Exercises

1. Build the reference architecture on your Week 4 engine, stage by stage, with the eval table above. Which stage bought the most hit-rate per added latency?
2. Auto-filter test: 10 questions with implicit constraints ("current refund policy" → year filter). How often is the generated filter right? Log every misfire.
3. Fusion ablation: 0/2/4/8 alternate queries. Where does quality plateau — and what does 8× retrieval cost you?
4. Reranker swap: `ms-marco-MiniLM-L-6-v2` vs `bge-reranker-base` on the same fused top-50. Same winner at top-3?
5. Break the chain deliberately: fusion generates 4 garbage queries (test with an incoherent question). Does RRF absorb the noise or does it pollute the top-5? What guard would you add?

## Pitfalls

- **Post-filtering permissions** — a forbidden doc in the candidate set is a data leak even if the LLM "probably won't use it"; prefilter, always
- **Fusion without dedup** — the same chunk from 3 queries is *signal* (RRF handles it) but naive set-union overcounts
- **Reranking the final k** — reranking 5 candidates to pick 5 is theater; rerank 20–50 to pick 3–5
- **LLM expansion for identifier queries** — "E-4021" expanded into prose can *lose* the exact term; keep the original query in the ranking list (the code above does)
- **Stacking everything "because Week 5"** — every stage is latency+complexity; keep what the harness proves

## Resources

- Raudaschl, *RAG Fusion* post + repo — the original multi-query framing
- Sentence Transformers, [Cross-Encoders docs](https://sbert.net/examples/applications/cross-encoder/README.html) + [retrieve & rerank](https://sbert.net/examples/applications/retrieve_rerank/README.html)
- Cohere [Rerank API](https://docs.cohere.com/docs/rerank-overview) — managed reranking with quality charts
- LanceDB docs — native hybrid + reranking patterns
- Gao et al., *RAG-Fusion* (arXiv 2402.03367)
