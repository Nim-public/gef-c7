# 04.1 — The Guardrail Implementation

> Subfolder index: [README.md](README.md) · Parent topic: [../04-rag-chatbot-guardrails.md](../04-rag-chatbot-guardrails.md)

The guardrail sandwich as runnable code:

```python
def guarded_turn(bot, user_text: str) -> dict:
    # INPUT GUARDS
    if injection_detected(user_text):
        return {"reply": CANNED_REFUSAL, "guard": "injection"}
    pii_count = scrub_pii(user_text)                    # W2-02
    if pii_count > 3:
        return {"reply": "Please remove personal information.", "guard": "pii"}

    # RETRIEVE
    hits = advanced_search(user_text, k=5)              # W5-03
    if hits.get("caveat"):
        return {"reply": "I don't have that information.", "guard": "no_match"}

    # GENERATE (grounded, W4-01)
    answer = generate_grounded(user_text, hits["hits"])

    # OUTPUT GUARDS
    invalid = invalid_citations(answer, hits["hits"])
    if invalid:
        answer = regenerate_without_bad_citations(answer, hits)
    confidence = compute_confidence(answer, hits)
    return {"reply": answer, "citations": extract_citations(answer),
            "confidence": confidence, "guard": "passed"}
```

Every guard returns a structured result with a `guard` tag — the trip log (W15-02) records every event for the eval feedback loop (W16-01).

The confidence computation combines: rerank score (W5-03), citation coverage, and logprob signals (W1-07) — the escalation trigger for W5-04's human-in-the-loop.

## Exercises

1. Implement the full `guarded_turn` with all layers; test each guard individually and in combination (the composition test from W5-04).
2. The trip-log analysis: run 50 queries; count guard events per type; identify the noisiest guard and tune its threshold.
3. The escalation design: define the confidence formula, set the threshold, and measure the human-handoff rate on benign traffic — target ≤10%.

## Pitfalls

- **Guards that block everything** — the over-blocking failure (W5-04); track the false-positive rate per guard
- **Regeneration loops** — a failed citation check triggers regeneration, which fails again; cap at 1 retry
- **PII scrubbing that destroys the query** — over-aggressive masking removes the search terms; scrub for *logging*, not for *retrieval input*
- **The escalation path untested** — the handoff to human must work; test it like every other path

## Resources

- W5-04 parent, W3-02 (injection layers), W12-04 (numeric grounding), W10-04 (instrumentation) — composed here
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) · [llm-guard](https://github.com/protectai/llm-guard) — the framework alternatives
