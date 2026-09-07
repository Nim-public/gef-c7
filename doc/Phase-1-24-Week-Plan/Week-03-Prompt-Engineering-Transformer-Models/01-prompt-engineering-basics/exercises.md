# Exercises — Prompt Engineering Basics

> Subfolder index: [README.md](README.md) · Parent: [../01-prompt-engineering-basics.md](../01-prompt-engineering-basics.md)

Labs for this subfolder. Shared fixture: the W1-05 ticket dataset (150 examples) + the W10-04 trajectory harness.

---

## E1 — The contract upgrade (file 01)

1. Convert 3 of your prompts to full four-clause contracts (role/format/boundaries/evidence); run the W1-05 harness before/after.
2. Few-shot optimization: 5 example sets × 20 cases — the accuracy/token table; identify the highest-signal example.
3. The escape-hatch audit: 8 off-domain questions through your best prompt — OTHER-rate vs forced-fit rate.

**Worked approach:** exercise 2 usually reveals that ONE example carries most of the signal — removing it one at a time (leave-one-out) quantifies each example's contribution.

## E2 — CoT economics (file 02)

1. Zero-shot vs CoT vs structured-CoT on the 20 cases: accuracy, tokens, latency — the full §1 table.
2. The reasoning audit: for 10 structured-CoT outputs, read the reasoning fields — how often does the reasoning contain the error (vs the final label being wrong for the right reason)?
3. The cost-optimal split: apply CoT only to the cases the few-shot classifier flags as low-confidence (W5-04's hook) — measure the blended accuracy/cost.

**Worked approach:** exercise 3's selective-CoT is the production pattern — reasoning tokens only where the cheap path is uncertain.

## E3 — The chain (file 02)

1. Build the 3-link chain (summarize → classify → draft) with seam validation and per-link retry.
2. Failure injection: make link 2 return malformed JSON 30% of the time — measure propagation with and without seam fallback.
3. Chain refactor: convert the chain to LangGraph nodes (W13-03) — compare LOC, testability, and failure localization.

**Worked approach:** exercise 3's comparison is the practical LCEL/LangGraph motivation — the same chain, two frameworks, one measurable difference.

## E4 — Meta and multimodal (file 03)

1. The critique loop: 3 rounds of generate→critique→rewrite on your weakest prompt; eval each round; stop at the peak.
2. Test-generation: 20 generated stress cases → hand-verify → add the 12 verified ones to the eval; measure the new failure discovery rate.
3. Screenshot extraction: 5 UI screenshots through the multimodal contract with NO_DIALOG fallbacks; verify the verbatim-text checks.

**Worked approach:** exercise 2's verified-case pipeline is the sustainable eval-growth mechanism — the model writes what you'd never think to test, you verify what it writes.

## E5 — Variables and localization (file 03)

1. Migrate 3 f-string prompts to `PromptTemplate` with render asserts; demonstrate a caught missing-variable bug.
2. The localization sprint: English → Hindi versions of your triage prompt — token counts (W1-01.5), translation QA (W2-03 back-translation), and behavioral parity on 10 cases.
3. Budget-aware rendering: `render` enforces a token ceiling per section (system/few-shot/user) — implement and test with an oversized few-shot block.

**Worked approach:** exercise 2's behavioral parity check (does the Hindi prompt classify identically?) is the multilingual eval slice from W2-02 — now at prompt level.

## Self-assessment

- Can you state the four contract clauses and the test each enables?
- Can you compute the CoT cost-benefit inequality for your workload with real numbers?
- Can you run a meta-prompt loop that measurably improves a prompt without regressing the eval?
