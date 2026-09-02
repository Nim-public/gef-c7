# 02 — Semantic Caching & Context Compression

> E9 index: [README.md](README.md)

**Core topics:** *Semantic response caching and context compression — the memory techniques that cut cost/latency.*

---

## What you'll learn

- Semantic caching: exact vs embedding-level cache hits, thresholds, invalidation
- The correctness trap: when a cached answer is *similar but wrong*
- Context compression at agent scale (W18-03's techniques, memory edition)
- The cost/quality measurement for both

## 1. Exact vs semantic caching

| Layer | Mechanism | From your work |
|---|---|---|
| **Exact** | identical prompt (hash) → identical answer | W15-04's prompt caching; CI caches (W14-04) |
| **Semantic** | similar question → cached answer | new this file — the risk tier |

Exact caching is free safety. Semantic caching trades correctness risk for cost: the hit is decided by embedding similarity (W2-03), which cannot distinguish "refund timeline" from "refund fraud investigation timeline".

## 2. Semantic cache design

```python
import numpy as np

class SemanticCache:
    def __init__(self, thresh=0.92, ttl_days=7):
        self.rows = []                       # {q_emb, answer, model, created, meta}
        self.thresh, self.ttl = thresh, ttl_days

    def lookup(self, question_emb, filters: dict) -> dict | None:
        for row in self.rows:
            if not self._matches_filters(row, filters): continue
            if self._expired(row): continue
            if float(question_emb @ row["q_emb"]) >= self.thresh:
                return row
        return None

    def store(self, question_emb, answer, model, meta):
        self.rows.append({"q_emb": question_emb, "answer": answer,
                          "model": model, "created": now(), "meta": meta})
```

Design rules that keep the cache honest:

- **High threshold (≥0.92)** — similarity lies (W2-03); a 0.85 match on "refund *policy*" vs "refund *status*" is a wrong answer served instantly
- **Cache key = model + prompt version + filters** — W16-01's versioning: a cached answer from the old prompt version is stale (W4-03's drift rule, caching edition)
- **TTL** — corpus updates (W4-05) and policy changes invalidate answers; the cache must expire them
- **Per-feature caches** — analytics answers (numbers!) must never be cached like prose answers (W12-04's grounding rules); time-bucket numeric answers by data freshness
- **Tenant isolation** — user A's cached answer must not serve user B if permissions differ (W5-03's prefilter extends to the cache)

## 3. Measuring the trade

| Metric | Definition |
|---|---|
| hit rate | served-from-cache ÷ total |
| cost saved | hits × per-call cost (E8-03 ledger) |
| **wrong-hit rate** | sampled cache hits judged incorrect ÷ sampled hits |
| latency win | p50/p95 with vs without cache |

```python
def audit_cache(cache, sample_n=50, judge=llm_judge):
    sample = random.sample(cache.rows, min(sample_n, len(cache.rows)))
    wrong = [r for r in sample if not judge(r["question"], r["answer"])]
    return {"sampled": len(sample), "wrong_hits": len(wrong),
            "wrong_rate": len(wrong) / len(sample)}
```

The wrong-hit rate is the metric that decides the threshold: raise `thresh` until `wrong-hit ≈ 0` while hit rate stays meaningful — the W15-04 router sweep, caching edition.

## 4. Context compression (W18-03 at agent scale)

Memory pages and long agent runs need compression before they fit budgets:

| Technique | When |
|---|---|
| extractive (keep top sentences) | facts/numbers must survive exactly (W18-03 §4a) |
| abstractive summarization | narrative memory, topic transitions (W2-03 rules) |
| LLMLingua token compression | structure-heavy content (W18-03 §4c) |
| hierarchical re-summarization | old memories compress recursively (E9-01's archival tier) |

Agent-loop compression (W10-05's `fit_context`) generalizes: old *observations* compress extractively (facts survive), old *conversations* compress abstractively, core memory never compresses (it's the constitution + live facts).

## Exercises

1. Build `SemanticCache` with the audit function; run 200 real-ish queries (W16-02 grid) through it. Report hit rate, wrong-hit rate, and the threshold that satisfies both.
2. Staleness drill: update a document in your corpus (W4-05); verify the cached answer for the related question is stale — then implement the invalidation (by source/dependency).
3. Cache-key audit: same question, different user permissions (W5-03) — verify tenant isolation in the cache. What's the fix if broken? (Filters in the key, or per-tenant caches.)
4. Compression A/B: agent run with raw history vs compressed history (extractive/abstractive) over 30 turns — answer quality and context tokens. Which compression for which content?
5. Cost model: cache hit-rate × E8-03's per-call cost — the monthly saving curve as a function of threshold. Where's your operating point?

## Pitfalls

- **Caching personalized answers** — a cached answer computed with user A's permissions/data served to user B is a data leak (W5-03's prefilter, cache edition)
- **Cache before grounding** — a cached RAG answer survives corpus changes that invalidated it; TTL + invalidation by source
- **Compression losing constraints** — abstractive summaries drop citation ids and numbers; keep verbatim critical spans (W18-03 §4a)
- **Threshold set once** — query distribution drifts (new product, new language); re-audit monthly (W16-02's distribution rule)
- **Semantic cache as a security surface** — poisoning the cache = poisoning every future similar query (E7's LLM04/08); write-path authentication required

## Resources

- GPTCache [docs](https://github.com/zilliztech/GPTCache) — semantic-cache reference architecture
- W18-03 (compression), W15-04 (exact caching), W10-02/05 (memory/budget) — composed here
- LangChain [caching](https://python.langchain.com/docs/how_to/llm_caching/) — exact + optional semantic layers
- [Letta docs](https://docs.letta.com/) — where caching meets memory (E9-01)
