# Exercises — Fusion & Reranking

> Subfolder index: [README.md](README.md) · Parent topic: [../03-hybrid-filtering-fusion-reranking.md](../03-hybrid-filtering-fusion-reranking.md)

Labs for this subfolder. The staged pipeline (file 01) is the fixture for all exercises.

---

## E1 — The staged build (file 01)

1. Implement the 6-stage pipeline; run the W4-05 harness at each stage; produce the ablation table.
2. The attribution: which stage contributes the most hit-rate improvement per added millisecond?
3. The auto-filter accuracy: 20 questions with implicit constraints; measure the filter-extraction accuracy; fix the top failure.

**Worked approach:** exercise 2's ablation table is the pipeline's justification — each stage earns its latency or gets removed.

## E2 — The reranker deep dive (file 01)

1. Cross-encoder comparison: `ms-marco-MiniLM-L-6-v2` vs `BAAI/bge-reranker-base` on the same fused top-20 — which reranks better on your domain?
2. The depth study: rerank from top-10 vs top-30 vs top-50 — the recall/precision/latency trade; find the optimal candidate depth.
3. The calibration: plot rerank score vs actual relevance on 50 scored pairs — is the score monotonic with quality?

**Worked approach:** exercise 2's depth study determines the fusion output size — too few candidates and the reranker can't find the answer; too many and latency suffers.

## E3 — The fusion stress test (file 01)

1. Query expansion quality: for 10 questions, hand-judge the 3 sub-queries — are they actually useful? What fraction are redundant or misleading?
2. The noisy-expansion test: feed deliberately bad sub-queries — does RRF absorb the noise or does the ranking degrade?
3. The end-to-end p95: measure the full pipeline 20×; identify the bottleneck stage; optimize it and re-measure.

**Worked approach:** exercise 2's noise test reveals RRF's robustness limit — the point where bad sub-queries overwhelm the signal from good ones.

## Self-assessment

- Can you draw your pipeline's architecture from memory, naming each stage and its measured contribution?
- Can you explain why prefilter is a security control and postfilter is not?
- Can you set the reranker candidate depth and the escalation threshold from data rather than defaults?
