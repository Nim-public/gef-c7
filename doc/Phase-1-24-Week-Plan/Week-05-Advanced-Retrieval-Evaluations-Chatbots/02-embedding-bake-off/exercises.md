# Exercises — Embedding Bake-off

> Subfolder index: [README.md](README.md) · Parent topic: [../02-embedding-models.md](../02-embedding-models.md)

Labs for this subfolder. The bake-off table is the deliverable.

---

## E1 — The full bake-off (file 03)

1. Run 4 local models + 1 API model on your 25-query eval set; produce the complete table.
2. The prefix audit: E5 with and without prefixes — the quality delta measured and documented.
3. The robustness slice: evaluate on the adversarial queries (W4-04's probes) — which model handles identifiers, negation, and multilingual queries best?

**Worked approach:** exercise 1's table with the prefix audit is the bake-off's minimum viable output — the model selection decision requires this evidence.

## E2 — The degradation map (file 03)

1. For the selected model, evaluate per-slice (by document type, by query class) — find the weakest slice.
2. The slice-specific fix: for the weakest slice, try a different embedder OR add metadata enrichment — measure the slice improvement.
3. The drift canary: re-run the bake-off after a corpus update — has the ranking changed? (The W5-02 model lock-in check.)

**Worked approach:** exercise 2's slice-specific fix is the pattern that makes the bake-off actionable — the aggregate score hides the slice where the model fails.

## Self-assessment

- Can you state your selected embedder, its revision, its prefix requirements, and the evidence for the selection?
- Can you name the query classes where your embedder underperforms — and the mitigation?
