# Exercises — NLP Tasks

> Subfolder index: [README.md](README.md) · Parent: [../03-nlp-tasks.md](../03-nlp-tasks.md)

Shared fixture: a 20-document capstone-adjacent corpus (W1-04's builder output) plus a 40-question labeled QA set — reused across all labs so the comparisons stay valid.

---

## E1 — Summarization quality lab (file 01)

1. Control sweep: 9 summaries (3 lengths × 3 beam widths) of the same article — blind-rank them with a fixed rubric (coverage, fluency, no-invention).
2. Faithfulness audit: `check_faithfulness` on all 9; correlate the issue counts with your blind ranking.
3. Map-reduce vs truncation on a 20k-token document: what does each lose? (Check the conclusion specifically.)

**Worked approach:** the correlation exercise (issue count vs rank) teaches the metric-choice lesson: BLEU-style overlap vs faithfulness checks measure different failures.

## E2 — QA pipeline build (file 02)

1. Extractive QA over your corpus: 20 questions, top-3 spans each; hand-verify — build the score-threshold calibration from wrong-passage runs.
2. Generative QA on the same 20 with the grounding contract; faithfulness spot-check (W5-05).
3. The retrieval sandwich: connect both QA models to your W4 retriever — closed-book vs open-book on 10 questions, table the difference.

**Worked approach:** exercise 3's table is the RAG motivation demonstrated with your own data — the same demonstration W4-01 asked for, now measured.

## E3 — Translation pipeline (file 03)

1. Direction audit: 5 language pairs, both directions, back-translation scored — the pair-quality table.
2. Glossary enforcement: 10 domain terms through LLM translation, with and without the glossary — term-preservation rate.
3. Placeholder safety: `{variable}` and `<tag>` in translated text — extract-translate-reinsert vs naive; show the breakage.

**Worked approach:** exercise 3's extract-translate-reinsert pattern is the template discipline (W3-01) applied to translation — the failure mode of naive translation is structural corruption.

## E4 — Embedding consistency (file 04)

1. The contract artifact: `CONTRACT` dict + `encode_with_contract` wrapper + a test that fails on any drift.
2. Cross-model agreement: MiniLM vs BGE top-5 neighbors on 30 sentences — agreement rate; where they disagree, judge which is right.
3. Dedup precision sweep: thresholds 0.90/0.95/0.98 on hand-labeled pairs — precision/recall per threshold; pick the operating point.

**Worked approach:** exercise 1's contract wrapper is the artifact that makes embeddings safe across systems — the W4-03 drift rule as a runtime assertion.

## E5 — The integration sprint (parent file 06's task, deepened)

1. Pick one NLP task for your capstone (summarization/QA/translation/embeddings); build it with the model you selected in W2-06's protocol.
2. Wire it behind the same interface as your other capstone components (W9-05's contract style).
3. Evaluate with the shared harness; add the results to the W2-06 README's comparison table.
4. Write the deployment note: versioning, monitoring hooks (W10-04), and the failure modes you'll watch.

**Worked approach:** the sprint's value is the *integration* — a standalone model demo is week-2 level; a wired component with contracts and evals is capstone-level.

## Self-assessment

- Can you explain the retrieval sandwich (closed-book → extractive → RAG) with your own examples?
- Can you verify a summary's faithfulness programmatically, and name what the checks miss?
- Can you state the embedding consistency contract for your system — and test for violations?
