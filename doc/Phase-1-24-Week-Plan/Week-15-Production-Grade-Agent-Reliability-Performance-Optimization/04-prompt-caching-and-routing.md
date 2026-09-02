# 04 — Prompt Caching & Model Routing

> Week 15 index: [README.md](README.md)

**Session 2 topics:** *Prompt caching & prompt structuring to cut cost/latency. Model routing: send easy prompts to cheaper SLMs (RouteLLM).*

---

## What you'll learn

- Prompt caching: how providers discount *repeated prefixes* and how to structure prompts to earn the discount
- Prompt structuring for cache hits — the order-of-parts rule
- Model routing: RouteLLM-style classification sending easy prompts to SLMs, hard ones to frontier models
- The eval-driven router: choosing your threshold from data, not vibes

## 1. Prompt caching

Providers (OpenAI, Anthropic, DeepSeek, and serving engines via prefix caching, file 03) discount input tokens that **match a previously seen prefix** — typically 50–90% off cached tokens and lower TTFT. The cache is *prefix-based*: it matches from character 0, so whatever varies must come **after** whatever stays.

### The structuring rule (this is the whole technique)

```text
BAD:   [context docs] [system] [question]        ← everything varies → nothing cached
GOOD:  [system constitution] [tools/schemas]     ← stable, huge → cached
       [few-shot examples]                       ← stable → cached
       [today's date]                            ← changes daily → cache boundary here
       [retrieved context + question]            ← varies per request → never cached
```

Your capstone is accidentally cache-hostile right now: a per-request date, or a user question pasted early, breaks the prefix for every token after it. Audit the prompt assembly (W4-01's `answer()`) and re-order: stable constitution → stable few-shots → varying context → question.

### Measured expectations

| Workload shape | Cache hit potential |
|---|---|
| agent with a long fixed constitution + many turns (your W10–14 bots) | high — 70–90% of input tokens cached |
| RAG with a fixed template, varying context | template + instructions cached; context varies |
| one-shot varied questions | near zero — restructure or don't bother |

Anthropic's explicit cache-control headers and OpenAI's automatic prefix caching differ in mechanics (explicit `cache_control` breakpoints vs automatic ≥1024-token prefixes) — read your provider's doc and *verify the discount in the billing response* (`cached_tokens` in usage), not the marketing page.

## 2. Prompt-structuring audit (do this on every production prompt)

1. Re-order to [stable][stable][variable] (§1)
2. Move per-request data to the **end** (recency bonus, W3-02)
3. Freeze volatile literals out of the cached prefix (dates, usernames)
4. Keep cached prefixes **identical byte-for-byte** — one changed token invalidates from there
5. Measure: `cached_tokens` before/after — the discount is the proof

## 3. Model routing (RouteLLM pattern)

Two-tier serving: a **router** classifies each request, sending easy ones to a cheap SLM and hard ones to a frontier model. Your capstone already built the pieces — this file assembles them:

```python
from openai import OpenAI

slm = OpenAI(base_url="http://localhost:11434/v1", api_key="x")   # W2-05 local SLM
frontier = OpenAI()                                               # API

def route(question: str) -> str:
    verdict = zero_shot_classify(question)          # W2-02 / W1-07 logprobs
    if verdict.confidence > 0.8 and verdict.tier == "easy":
        return answer_with(slm, question)
    return answer_with(frontier, question)
```

Router choices, in increasing sophistication:

| Router | Mechanism | From your work |
|---|---|---|
| rules | length/keywords/domain regex | W6-04's router |
| zero-shot classifier | NLI/LLM logprobs | W2-02, W1-07 |
| **RouteLLM-style** | a small model *trained* on preference data predicting "can the weak model answer?" | the published framework (see resources) |
| cascade | try SLM → self-check/judge → escalate | W2-05's SLM-first pattern + W5-04 confidence |

### Calibrating the threshold (the graded part)

Every misroute has a cost:

- **Easy → frontier**: wasted money (typically 5–20× per token) but correct
- **Hard → SLM**: cheap *and wrong* — quality regression

Sweep the threshold on your 25-question harness × both models; plot accuracy vs cost; pick the knee. Report the misclassification rates *both ways* — the W10-04 metrics discipline applied to the router itself.

## 4. Where routing composes with the rest of Week 15

| Layer | What it optimizes | This file |
|---|---|---|
| prompt structure | input tokens (cache hits) | §1 |
| model routing | per-request model price | §3 |
| inference engine | tokens/s at fixed cost | file 03 |
| retries/timeouts | wasted spend on failures | file 01 |

Order of implementation (cheapest first): prompt restructure (hours, zero risk) → caching verification (billing check) → SLM cascade for obvious-easy classes → full router with a trained judge. Measure each against the W14-06 baseline; keep what the table proves.

## Exercises

1. Prompt-cache audit: reorder your capstone agent's prompt assembly to [stable][variable]; measure `cached_tokens` over 20 same-session turns. Report the cost delta.
2. Cache-boundary drill: move the date from the prefix to the tail — what happens to the hit rate? (This is why "today" lives in the system prompt's *end*, or is injected per turn.)
3. Build the rule-based router (question length + keyword classes) → SLM vs frontier; measure accuracy and cost on your 25-case harness.
4. RouteLLM-style: label 100 of your logged questions as SLM-solvable (from W11-06's eval) and train/zero-shot a router; beat the rule-based version's accuracy at equal cost.
5. Cascade with verification: SLM answers first; a *judge* checks schema + grounding (W5-04); only failures escalate. Report quality parity and the cost curve.

## Pitfalls

- **Caching PII prefixes** — cached prompts persist server-side; per-user dynamic data in the prefix is a privacy + hit-rate mistake (W15-02's trace hygiene, same rule)
- **Assuming cache hits are automatic** — OpenAI needs ≥1024-token prefixes and exact matching; Anthropic needs explicit breakpoints; verify in `usage`
- **Router trained on the eval set** — the router that aces its own training questions lies; hold out cases (W5-05)
- **SLM for safety-critical classification** — the cheap model misrouting *injection attempts* to the cheap path is a security regression (W3-02)
- **Micro-optimizing before measuring** — prompt restructure is free; the router is an ML system needing its own eval; sequence accordingly

## Resources

- OpenAI [prompt caching guide](https://platform.openai.com/docs/guides/prompt-caching) · Anthropic [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — mechanics + `cache_control`
- [RouteLLM](https://github.com/lm-sys/RouteLLM) (LMSYS) — the trained-router framework and its benchmarks
- vLLM `--enable-prefix-caching` (file 03) — the self-hosted version of §1
- W2-05 (SLM serving), W10-04 (metrics), W14-06 (baseline) — the inputs
