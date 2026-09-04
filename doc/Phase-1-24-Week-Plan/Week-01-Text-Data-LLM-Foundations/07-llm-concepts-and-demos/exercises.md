# Exercises — LLM Concepts & Demos

> Subfolder index: [README.md](README.md) · Parent: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md)

Labs for this subfolder. Shared fixture: the W10-04 agent (with its 10-case eval set) and the W1-05 ticket classifier.

---

## E1 — API census (file 01)

1. Field census: 5 calls with varied parameters; `model_dump()` the responses; build a table of every field, its type, and its meaning.
2. Finish-reason survey: craft calls producing `stop`, `length`, `content_filter`, and `tool_calls` — one call each; document the handler for each.
3. Reconciliation: your tiktoken counts vs `usage.prompt_tokens` on 10 prompts — compute the per-model overhead constant (chat template + role markers).

**Worked approach:** exercise 3's overhead constant feeds every cost forecast afterward — measure it once per model.

## E2 — Context economics (file 02)

1. Cost curves: cumulative input cost over 30 simulated turns for raw / trimmed / summarized / hybrid strategies — one plot, four lines.
2. Retention probes: after each strategy, ask about facts from deleted turns; measure admit-vs-invent rates (the W5-04 refusal discipline under memory pressure).
3. Re-injection design: pick the 5 facts that must survive trimming; implement re-injection; verify they're present after 30 turns at half the budget.

**Worked approach:** exercise 2's invent-rate is the scariest number in this lab — a memory system that makes the agent *confidently* hallucinate is worse than amnesia.

## E3 — Sampling forensics (file 03)

1. Temperature plots: top-5 probability bars at T ∈ {0.2, 0.7, 1.5} for 3 prompts; mark where ranking flips.
2. Reliability diagram: 30 classification calls at T=0 — predicted confidence (from logprobs) vs observed accuracy in 5 bins.
3. Determinism probe: 10 identical calls (T=0, same seed) today and tomorrow — mismatch count; document the drift.

**Worked approach:** exercise 3's cross-day drift is the argument for distributional baselines (E8-04's bridge question) — bit-identity is not a property you can demand.

## E4 — Alignment observation (file 04)

1. Stop-machinery lab: EOS, stop-sequences, and max-tokens — force each finish reason; verify the handler map (file 01 ex. 2).
2. Streaming characterization: chunk-size distribution over 10 answers; token-vs-chunk count ratio; the buffering implications.
3. Cancellation economics: close 10 streams mid-generation; sum the billed usage vs the ungenerated estimate — quantify the saving.

**Worked approach:** exercise 2's chunk-size distribution is what your UI buffering must handle — the frontend lesson from W11-04, now with data.

## Self-assessment

- Can you reconcile provider token counts with your own counts, and explain the residual?
- Can you state the three memory operations (trim/summarize/re-inject) and when each is the right tool?
- Can you produce a reliability diagram for logprob confidence, and name the decision it feeds?
