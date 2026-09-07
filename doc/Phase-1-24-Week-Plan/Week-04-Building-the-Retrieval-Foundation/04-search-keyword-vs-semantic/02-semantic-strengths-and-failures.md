# 04.2 — Semantic Strengths & Failures

> Subfolder index: [README.md](README.md) · Parent: [../04-search-keyword-vs-semantic.md](../04-search-keyword-vs-semantic.md)

---

## What you'll learn

- The semantic search strengths, demonstrated on real pairs
- The failure catalog: the queries where embeddings confidently fail
- The probe design: systematic testing of each failure class

## 1. The strengths (where embeddings shine)

| Strength | Example |
|---|---|
| **vocabulary bridging** | "can't log in" → "reset your password" |
| **paraphrase matching** | "cancel subscription" → "terminate plan" |
| **cross-lingual** | Hindi query → English document (multilingual models) |
| **intent matching** | "my computer is slow" → "performance optimization guide" |
| **conceptual** | "data safety" → "encryption at rest and in transit" |

The vocabulary-bridging strength is the single biggest argument for semantic search: keyword search finds zero results for paraphrases; embeddings find the right document.

## 2. The failure catalog (each probed)

| Failure | Query | Expected result | Actual |
|---|---|---|---|
| **Counting** | "products under $50" | filtered set | similar products, no filter |
| **Negation** | "not refundable" | the non-refundable policy | the refundable policy |
| **Identifiers** | "E-4021" | the exact error doc | similar errors, not the exact one |
| **Comparison** | "compare plan A and B" | both docs | one doc |
| **Temporal** | "changes since last month" | recent changes | all mentions |

Each failure is a *retrieval design* problem, not a model bug — the mitigation is either a different search arm (SQL, BM25) or a hybrid (the RRF pattern).

## 3. The probe design

```python
PROBES = {
    "counting":   "How many products are under $50?",
    "negation":   "Which items are NOT refundable?",
    "identifier": "Find the doc for error code E-4021",
    "comparison": "Compare plan A and plan B pricing",
    "temporal":   "What changed in the policy last month?",
}

for name, query in PROBES.items():
    results = semantic_search(query, k=5)
    print(f"{name:12} -> {[r['id'] for r in results]}")
    # hand-judge: is the right document in the top-5?
```

The probe results classify your corpus's semantic-search readiness — each failure names the mitigation (filter, hybrid arm, or metadata enrichment).

## 4. The mitigation map

| Failure | Mitigation |
|---|---|
| identifiers | BM25 arm in the hybrid (exact match) |
| counting/filtering | SQL arm or metadata prefilter |
| negation | BM25 (the term "not" is a signal) or NLI |
| comparison | decomposition (W14-04) — two queries, one synthesis |
| temporal | date-filtered retrieval or SQL |

The mitigations compose into the hybrid architecture (file 04 of the parent) — each failure class is served by the arm that handles it.

## Exercises

1. The probe suite: run all 5 failure probes on your corpus; classify each result as pass/fail/partial.
2. The mitigation map: for each failure found, name the arm that fixes it; verify the fix works.
3. The threshold interaction: does the semantic threshold (W4-03's calibration) interact with the failure classes? (Low-score failures are already caught; the failures are the confident-wrong ones.)
4. The paraphrase set: 10 paraphrases of the same question — how consistent are the top-5 results? (Consistency is a quality signal independent of accuracy.)
5. The mitigation-integration test: after adding the BM25 arm, re-run the failing probes — which now pass?

## Pitfalls

- **Semantic search as the only arm** — the failure catalog exists because one arm can't cover all query types
- **Probes without expected results** — a probe without a hand-labeled expected answer tests nothing
- **The confidence-mistaken-for-correctness trap** — a 0.9 similarity to the wrong document is still wrong
- **Corpus-specific failures assumed universal** — your failures are your corpus's; the probe suite is corpus-specific
- **Fixing one failure, breaking another** — the BM25 arm that fixes identifiers may hurt paraphrase matching; measure the trade

## Resources

- W4-04 parent (the comparison framework), W4-03 (the embedding infrastructure) — composed here
- E10-01 (benchmark literacy) — the failure-classification discipline at research scale
- W5-03 (the hybrid architecture that resolves these failures)
