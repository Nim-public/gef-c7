# Exercises — Keyword vs Semantic

> Subfolder index: [README.md](README.md) · Parent: [../04-search-keyword-vs-semantic.md](../04-search-keyword-vs-semantic.md)

Labs for this subfolder. Shared fixture: the W4-05 corpus and eval set.

---

## E1 — BM25 mastery (file 01)

1. Score inspection: one query, per-term BM25 contributions — explain the ranking term by term.
2. The tokenizer A/B: `split()` vs regex words vs stemmed — hit-rate comparison; document the tokenizer's impact.
3. The saturation verification: add a term 1×, 5×, 10×, 50× to a document — plot the score; verify the k1 saturation.

**Worked approach:** exercise 1's term-by-term breakdown is BM25's explainability advantage — every ranking is auditable, unlike embedding similarity.

## E2 — Semantic failure probes (file 02)

1. Run all 5 failure probes on your corpus; classify each result pass/fail/partial.
2. The mitigation map: for each failure, name the arm (BM25/filter/decompose) and verify the fix.
3. The confidence-mistaken-for-correctness audit: 10 high-similarity wrong results — what makes them similar? (The embedding's blind spot, categorized.)

**Worked approach:** exercise 2's mitigation verification is the hybrid architecture's justification — each failure class maps to an arm, and the arms compose into the hybrid.

## E3 — The harness build (file 03)

1. Build the 25-query eval set with hand-verified relevant ids.
2. Implement the three metrics; run the baseline; produce the reporting table.
3. The eval-set refresh: add 10 production queries (from W10-04 logs); re-run; does the ranking change? (Distribution shift measured.)

**Worked approach:** exercise 3's distribution shift is the eval-set maintenance lesson — the eval set is a living artifact that tracks the query distribution (W16-01's versioning).

## E4 — The hybrid certification (file 04)

1. RRF by hand + code: two rankings, fused — manual and programmatic results match.
2. The k-sweep: RRF k ∈ {1, 10, 60, 500} — the ranking stability analysis.
3. The three-arm test: add the cross-encoder reranker (W5-03) after RRF — the fused vs reranked comparison.
4. The coverage measurement: for 25 queries, the union coverage (correct doc in ANY arm's top-10) vs per-arm coverage — the hybrid's coverage advantage quantified.

**Worked approach:** exercise 4's union-coverage measurement is the hybrid architecture's core value proposition — the union of two imperfect systems covers more than either alone.

## Self-assessment

- Can you compute BM25 scores by hand for a simple query-document pair?
- Can you name the five semantic-search failure classes and the probe for each?
- Can you implement RRF and explain why ranks beat scores for fusion?
