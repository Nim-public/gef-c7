# Week 15 — Production-Grade Agent Reliability & Performance Optimization

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 19 Dec, 7–10 PM IST (Session 1) · Sun 20 Dec, 7–10 PM IST (Session 2) · Office Hours Thu 24 Dec, 7–8 PM IST

**Practice build:** [05-practice-production-hardening.md](05-practice-production-hardening.md)

---

## Why this week matters

Everything since Week 10 works *in a demo*. This week makes it survive production: limits, retries, and error handling; tracing and guardrails at the platform level (LangSmith); tests for agent workflows; and then the performance half — inference engines (vLLM/SGLang), caching, and model routing that cut cost/latency without touching quality. Your W14-06 baseline numbers (p95, $/task) are the target of every intervention here.

## What you will be able to do after this week

- [ ] Add limits, retries with backoff, and structured error handling to agents
- [ ] Trace/debug with LangSmith (or equivalent) and enforce guardrails at the platform layer
- [ ] Write unit and integration tests for agent workflows
- [ ] Explain continuous batching, KV caching, and quantization as serving optimizations
- [ ] Apply prompt caching and prompt structuring to cut cost/latency with measured savings
- [ ] Implement model routing: easy prompts to SLMs, hard ones to frontier models

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-reliability-limits-retries-tests.md](01-reliability-limits-retries-tests.md) | Limits, retries, error handling, agent tests | 3–4 h |
| 2 | [02-tracing-guardrails-langsmith.md](02-tracing-guardrails-langsmith.md) | LangSmith tracing, datasets, guardrails | 2–3 h |
| 3 | [03-inference-optimization.md](03-inference-optimization.md) | vLLM/SGLang, continuous batching, KV cache, quantization | 3 h |
| 4 | [04-prompt-caching-and-routing.md](04-prompt-caching-and-routing.md) | Prompt caching, structuring for cost, model routing | 2–3 h |
| 5 | [05-practice-production-hardening.md](05-practice-production-hardening.md) | Harden + optimize your capstone agent (practice) | 4 h |

## Environment setup

```powershell
pip install langsmith tenacity pytest
pip install vllm               # Linux/GPU only — read the docs on Windows; use Ollama locally instead
pip install openai
```

## Self-check before Week 16

1. Your agent's p95 is 9 s: 6 s is the LLM, 2 s a slow tool, 1 s network. Rank the fixes by effort-to-impact — and name the one you *can't* fix with prompt changes.
2. Prompt caching cut your cost 40%. Why can it *also* cut quality if applied carelessly (what must stay outside the cached prefix)?
3. RouteLLM sends "easy" prompts to a 1B model. What defines "easy" in your system — and what happens on misclassification (both directions)?
4. Continuous batching raised throughput 5× at the same latency. What does that imply about your request mix?
5. Which of your W14 tests are *unit* (no LLM) vs *integration* (LLM) — and what did you have to stub to make the unit ones fast?
