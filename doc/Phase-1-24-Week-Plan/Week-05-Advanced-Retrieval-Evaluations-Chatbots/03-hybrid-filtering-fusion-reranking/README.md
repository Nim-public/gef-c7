# 03 — Fusion & Reranking: Deep Dive

> Parent topic: [../03-hybrid-filtering-fusion-reranking.md](../03-hybrid-filtering-fusion-reranking.md) · Week 5 index: [../../README.md](../../README.md)

The reference architecture stacking filtering, fusion, and reranking — each stage independently testable via the W4-05 harness.

**Key content from the parent topic:**

- **Metadata filtering**: prefilter for security (restricted content never enters candidates), postfilter for soft preferences
- **RAG fusion**: LLM decomposes the question into 3–5 sub-queries; RRF merges the rankings — coverage without score calibration
- **Cross-encoder reranking**: the two-stage pattern — bi-encoder retrieves top-50, cross-encoder reranks to top-5. The biggest single quality jump in most pipelines
- **The staged architecture**: filter → fusion → rerank, each stage measured with the W4-05 harness

The auto-filter pattern (LLM extracts metadata filters from the question) and the confidence-threshold escalation (low rerank score → human review) connect to W5-04's guardrail sandwich and W15-04's router.

For the full implementation, ablation tables, and the bypass catalog, see the parent file and the W5-03 exercises.
