# 04 — Keyword vs Semantic Search (and the Hybrid Bridge)

> Week 4 index: [README.md](README.md)

**Session topics:** *Search Engine Development — building keyword and semantic search capabilities (S1) · Compare keyword versus semantic search in practice (S2)*

---

## What you'll learn

- How keyword search scores documents (TF-IDF/BM25) — the 50-year-old engine still beating embeddings at some tasks
- Where semantic search wins and where it embarrassingly fails
- A side-by-side evaluation harness you'll reuse forever
- Hybrid search: taking the union's strengths (full version lands in Week 5)

## 1. Keyword search: BM25 in one idea

Rank documents by **term frequency × inverse document frequency**, with saturation and length normalization. "Rare terms that appear a lot in this doc, and barely in others, matter most."

```python
from rank_bm25 import BM25Okapi

corpus = [
    "The refund timeline is 5 business days after approval.",
    "Refunds are processed to the original payment method.",
    "Shipping takes 3 to 7 days depending on the region.",
    "To reset your password, use the forgot password link.",
]
tokenized = [c.lower().split() for c in corpus]
bm25 = BM25Okapi(tokenized)

scores = bm25.get_scores("refund".split())
best = sorted(zip(scores, corpus), reverse=True)
```

Strengths you must respect: **exact terms matter** (error codes `E-4021`, product SKUs, names, acronyms); zero training, zero embeddings; trivially explainable ("matched: refund ×3").

Blind spots: vocabulary mismatch ("can't log in" vs "reset password" share zero keywords — the Week 2 embedding demo), no synonyms, no cross-lingual, no meaning.

## 2. Semantic search: embeddings do the understanding

Same query, vector search (file 03): `"can't log in"` → nearest = "reset your password" via cosine in embedding space. Wins on intent, paraphrase, multilingual.

Fails (test these on your corpus):

- **Exact identifiers** — `"SKU-4821"` matches everything "similar" and nothing exact
- **Rare names/codes unseen in training** — no signal in the embedding
- **Fresh jargon** — terms coined after the model's training data
- **Negation & counting** — "not refundable" ranks near "refundable"

## 3. The evaluation harness (build this once, use all program)

```python
import json

eval_set = json.load(open("data/search_eval.jsonl", encoding="utf-8"))
# each: {"query": "...", "relevant_ids": ["doc7::chunk42", ...]}

def evaluate(search_fn, k=5):
    hits = 0
    for case in eval_set:
        results = search_fn(case["query"], k=k)
        got = {r["id"] for r in results}
        hits += bool(got & set(case["relevant_ids"]))
    return hits / len(eval_set)                # hit rate @k

print("bm25    :", evaluate(bm25_search))
print("semantic:", evaluate(semantic_search))
```

20–30 queries with hand-marked relevant chunks. Two minutes per system change, forever. Week 5 adds MRR/precision; the harness stays identical.

### Where each one wins — run this experiment

| Query type | Expected winner |
|---|---|
| "reset password" vs "cannot log into account" | semantic |
| `"E-4021"` (error code in corpus) | keyword |
| "policy for cancelled subscriptions refunds" | tie/keyword (exact terms dominate) |
| Hindi question over English docs | semantic (multilingual embedder) |
| "not eligible for refund" | keyword (negation) |

Your numbers will differ — that's why the harness exists.

## 4. Hybrid: the union, cheaply (full version next week)

Reciprocal Rank Fusion — merge two ranked lists by rank position:

```python
def rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return dict(sorted(fused.items(), key=lambda kv: -kv[1]))

bm25_top10    = [r["id"] for r in bm25_search(q, k=10)]
semantic_top10 = [r["id"] for r in semantic_search(q, k=10)]
fused = list(rrf([bm25_top10, semantic_top10]).items())[:5]
```

Why RRF works: rank-based fusion needs no score calibration (BM25 scores ~0–20, cosine ~0–1 — incomparable directly; ranks aren't). The pattern: keyword catches exact terms, semantic catches paraphrase, the fused top-5 usually contains both systems' best hits.

## 5. Choosing a default for your search engine

| Corpus reality | Default |
|---|---|
| Product codes, SKUs, error codes, names | keyword-heavy hybrid |
| Conversational/FAQ, paraphrase-heavy | semantic-heavy hybrid |
| Multilingual audience | semantic (multilingual model) |
| Tiny corpus (<100 chunks) | keyword alone may honestly suffice — measure |

Ship **hybrid (BM25 + vectors, RRF)** as the baseline unless measurements say otherwise. It's two searches and 15 lines of fusion — cheap insurance against both failure modes.

## Exercises

1. Build the harness with 25 queries over your corpus. Report hit rate for BM25, semantic, and RRF-hybrid. Does hybrid win?
2. Find (or write) 3 queries where BM25 beats embeddings *badly*, and 3 the reverse. Categorize each failure (identifier? paraphrase? negation?).
3. Tune BM25's tokenizer: lower+split vs lower+strip punctuation+stem (nltk PorterStemmer). Effect on hit rate?
4. Swap the embedder (`all-MiniLM-L6-v2` vs `BAAI/bge-small-en-v1.5`) in the harness. Does one win on your data? (Full model bake-off: Week 5 file 02.)
5. Add `rrf(k)` as a parameter — try k=1, 60, 500. Is the ranking sensitive? What does that tell you about score scale assumptions?

## Pitfalls

- **Tokenization mismatch** between index-time and query-time (BM25 is only as consistent as your `split()`)
- **Cosine on unnormalized vectors** in the "semantic" arm — your comparison is invalid, not your conclusion
- **Eval set too easy** — queries copied verbatim from chunks make everything score 100%; write queries the way users talk
- **Comparing raw scores across retrievers** — never; compare ranks/sets
- **Deploying two indexes with different corpus versions** — keep one ingestion pipeline feeding both

## Resources

- BM25 explained: [rank_bm25 docs](https://github.com/dorianbrown/rank_bm25) + Robertson & Zaragoza's BM25 primer
- LanceDB hybrid search docs (`query_type="hybrid"` — native RRF, meets Week 5)
- Weaviate/pinecone.io posts on hybrid search — the clearest RRF explanations
- [BEIR benchmark](https://arxiv.org/abs/2104.08663) — why hybrid wins on real retrieval suites
