# 04 — Guardrails & Responsible AI: Deep Dive

> Parent topic: [../04-rag-chatbot-guardrails.md](../04-rag-chatbot-guardrails.md) · Week 5 index: [../../README.md](../../README.md)

The guardrail sandwich (input screening → grounded generation → output validation) and the responsible-AI practices that make the chatbot production-credible.

**Key content from the parent topic:**

- **Input guards**: regex screening for injection phrases, PII scrubbing before indexing, rate limits, length caps — fast, always-on, no LLM needed
- **Output guards**: citation validation (every `[doc:id]` must resolve to a retrieved chunk), schema enforcement, refusal detection, numeric grounding (W12-04's `numbers_supported`)
- **Responsible AI**: grounding + citations for auditability, reliable refusals (tested, not assumed), privacy (scrub + prefilter), human escalation on low confidence

The trip log (every guardrail event recorded as JSONL) is the W16-01 eval seed — production failures become regression tests.

For the full implementation, the guardrail table, and the composition-drill exercises, see the parent file and the W5-04 exercises.
