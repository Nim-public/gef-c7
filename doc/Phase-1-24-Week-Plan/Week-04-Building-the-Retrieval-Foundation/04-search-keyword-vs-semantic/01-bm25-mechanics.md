# 04.1 — BM25 Mechanics

> Subfolder index: [README.md](README.md) · Parent: [../04-search-keyword-vs-semantic.md](../04-search-keyword-vs-semantic.md)

---

## What you'll learn

- BM25's scoring formula: TF-IDF with saturation and length normalization
- The rank_bm25 implementation with tokenization control
- The strengths that keep BM25 in every production stack

## 1. The scoring formula

```
BM25(q, d) = Σ_idf(qi) · tf(qi,d) · (k1 + 1) / (tf(qi,d) + k1 · (1 - b + b · |d|/avgdl))
```

| Component | Effect |
|---|---|
| IDF | rare terms score higher |
| TF saturation (k1) | diminishing returns for repeated terms |
| Length normalization (b) | long documents don't dominate |

The three components answer three retrieval problems: rare terms matter more (IDF), repetition has limits (saturation), and document length is normalized (fairness). No embeddings needed — pure text statistics.

## 2. Implementation

```python
from rank_bm25 import BM25Okapi

corpus = [
    "The refund window is 5 business days after approval.",
    "Refunds are processed to the original payment method.",
    "Shipping takes 3 to 7 days depending on the region.",
]
tokenized = [c.lower().split() for c in corpus]
bm25 = BM25Okapi(tokenized)

scores = bm25.get_scores("refund".split())
for s, doc in sorted(zip(scores, corpus), reverse=True):
    if s > 0: print(f"{s:.3f} {doc}")
```

The tokenization IS the system: `lower().split()` is the minimum; real systems use stemming, stop-word removal, and n-grams. **The tokenizer choice is a retrieval-quality decision.**

## 3. The strengths (why BM25 survives)

| Strength | Example |
|---|---|
| exact identifiers | `"SKU-4821"`, `"E-4021"`, `"RFC 793"` — exact match beats semantic similarity |
| rare technical terms | "Kubernetes ingress controller" — the terms ARE the signal |
| negation | "not refundable" — the term "refundable" matches; the "not" is lost by embeddings |
| zero setup | no model, no embeddings, no GPU |
| explainability | "matched: refund ×3, days ×1" — auditable rankings |

## 4. The weaknesses (the embedding motivation)

| Weakness | Example |
|---|---|
| vocabulary mismatch | "can't log in" vs "reset password" — zero shared terms |
| no synonyms | "cancel" ≠ "terminate" |
| no cross-lingual | Hindi query ≠ English doc |
| no meaning | "bank" matches both river and finance uses |

These are the failures semantic search fixes — and why the hybrid (file 04 of this subfolder... the RRF pattern) combines both.

## Exercises

1. Tokenizer A/B: `lower().split()` vs `lower()+regex words+PorterStemmer` — hit-rate comparison on your eval set.
2. The identifier test: search for `"E-4021"` and `"SKU-4821"` — BM25 vs embeddings (W4-03); verify BM25 wins on exact identifiers.
3. Score inspection: for one query, print each term's BM25 contribution — explain the ranking (the explainability advantage).
4. The saturation check: add the same term 10× to a document — does the score keep growing? (k1 saturates it — verify.)
5. Stop-word experiment: with and without stop-word removal — which queries improve, which degrade?

## Pitfalls

- **Inconsistent tokenization between index and query** — the same text tokenized differently produces different scores
- **Empty token lists** — a query that tokenizes to nothing returns zero scores; handle explicitly
- **Case sensitivity in identifiers** — "SKU-4821" vs "sku-4821"; decide and enforce
- **BM25 on very short documents** — length normalization favors them; verify with your data
- **Term-frequency gaming** — a document repeating a term 50× doesn't score 50× higher (saturation), but gaming is real

## Resources

- [rank_bm25](https://github.com/dorianbrown/rank_bm25) — the implementation used here
- Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* — the formula's derivation
- W4-04 parent (the comparison framework), W2-03 (the embedding contrast) — composed here
