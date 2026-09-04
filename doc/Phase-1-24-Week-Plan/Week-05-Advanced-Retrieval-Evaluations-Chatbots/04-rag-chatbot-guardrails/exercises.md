# Exercises — Guardrails

> Subfolder index: [README.md](README.md) · Parent topic: [../04-rag-chatbot-guardrails.md](../04-rag-chatbot-guardrails.md)

Labs for this subfolder. The guarded_turn pipeline (file 01) is the fixture for all exercises.

---

## E1 — The guardrail certification (file 01)

1. Implement all guard layers; run 50 mixed queries (benign + adversarial); produce the per-guard event table.
2. The composition test: verify the guards work in sequence — a query that passes intake but fails output validation is still handled.
3. The false-positive audit: 30 benign queries — how many are incorrectly blocked? Tune thresholds until FP ≤ 5%.

**Worked approach:** exercise 1's per-guard event table is the security evidence (E7-01 §4) — every guard's behavior is measured, not assumed.

## E2 — The escalation drill (file 01)

1. Define the confidence formula; set the threshold; measure the escalation rate on benign traffic.
2. The handoff test: verify the escalation produces a clear message and logs the context for the human reviewer.
3. The escalation abuse test: can a user trigger escalation repeatedly to waste reviewer time? (Rate-limit the escalations.)

## E3 — The output quality audit (file 01)

1. For 20 answers: verify every citation resolves; every number appears in the source; the tone matches the constitution.
2. The hallucination stress test: force answers on topics with thin corpus coverage — measure the hallucination rate at different confidence levels.
3. The guard-detection test: inject a guard-evasion attempt (paraphrased injection); verify the output guard catches what the input guard missed.

## Self-assessment

- Can you name all guard layers in order, their trigger conditions, and their logged event types?
- Can your bot handle the injection battery with zero leaks and zero false blocks?
- Is your escalation rate measured, thresholded, and documented?
