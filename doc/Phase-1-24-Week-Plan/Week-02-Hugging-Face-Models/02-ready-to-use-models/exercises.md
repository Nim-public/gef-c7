# Exercises — Ready-to-Use Models

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

Labs for this subfolder. Shared artifact: the 40-case labeled ticket set (W2-06's mini-eval) — every lab reuses it, which is what makes the comparisons meaningful.

---

## E1 — Pipeline dissection (file 01)

1. Rebuild the sentiment pipeline from raw components; assert bit-identical outputs on 50 texts (same hardware, greedy path).
2. Task-registry census: 8 task names → default models → card audits → "keep/change" verdicts.
3. Custom postprocess: raw logits → per-token sigmoid for a multi-label variant — build the multi-label output format and test it.
4. Batching benchmark: 1,000 texts, batch 1/16/64 — throughput and memory table.

**Worked approach:** exercise 1's bit-identity assertion is the proof that you understand the three stages — any mismatch is a real bug to find (dtype, truncation, device).

## E2 — Sentiment deployment pack (file 02)

1. Run the sanity harness on 3 candidate models; produce the per-kind table (negation/sarcasm/neutral/mixed/domain-shift/encoding).
2. Score-distribution study on 100 real messages — histogram per label; decide deployability from the shape.
3. Calibration + threshold: reliability diagram; then the cost-optimal operating point from the W10-04 threshold economics.
4. Domain-adaptation check: fine-tune on 50 labeled tickets (W16-03); measure the gap closing on your sanity set.

**Worked approach:** exercise 2's histogram shape predicts everything — bimodal scores split cleanly at 0.5; a single hump centered at 0.6 means the model can't separate your classes and no threshold will fix it.

## E3 — NER + PII masking (file 03)

1. Aggregation comparison on 10 texts — all four strategies, diffed; document when `max` matters.
2. Adjacent-entity probe and fix: two consecutive names — verify split behavior, add the post-pass.
3. The PII masker: NER + regex composition, evaluated on 20 synthetic records — recall per PII type (file 03 §3's table).
4. Offsets invariant test: `text[start:end] == word` for 50 entities across 3 models — any violation is an alignment bug to fix.

**Worked approach:** exercise 3's per-type recall table drives the masking policy — NER for names, regex for emails/phones, and the union for coverage.

## E4 — Zero-shot mastery (file 04)

1. Template sweep: 5 hypothesis templates × 20 questions — top-1 agreement matrix; pin the winner with evidence.
2. Multi-class vs multi-label: 10 overlapping-category texts — which mode matches truth? (The scoring difference made concrete.)
3. Bootstrap workflow: zero-shot → hand-verify → train the W1-05 classifier → compare on held-out. Measure the bootstrap's value in final accuracy.
4. Calibration curve for zero-shot scores — before and after your template fix.

**Worked approach:** exercise 3's bootstrap loop (zero-shot labels → verify → train) is the cheapest path from "no labeled data" to "deployed classifier" — measure each step's contribution.

## E5 — The decision pack (file 05)

1. Full benchmark protocol on 40 cases: encoder vs LLM zero-shot vs LLM few-shot — accuracy, latency percentiles, cost per 1k.
2. Confidence-calibrated hybrid (§3) with the threshold sweep — accuracy vs escalation-rate plot; the operating point justified.
3. Cost model at 1M/day with the hybrid split applied — the break-even analysis.
4. Determinism audit: 3 runs per system on the same cases — drift quantified per system.

**Worked approach:** exercise 2's plot (accuracy vs escalation rate) is the router's tuning curve — the same plot W15-04's routing calibration needs, built here with real data.

## Self-assessment

- Can you explain what a sentiment score is — and what three things it is not?
- Can you produce a PII-masked text from raw input, with per-type recall evidence?
- Can you build and run the encoder-vs-LLM benchmark, and defend the routing threshold with your own numbers?
