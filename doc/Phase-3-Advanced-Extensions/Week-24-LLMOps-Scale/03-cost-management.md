# 03 — Cost Management for LLM Systems

> E8 index: [README.md](README.md)

**Core topics:** *Token accounting per feature, budgets, and the optimization ledger.*

---

## What you will be able to do after this week

- [ ] Attribute cost per feature/user/query with a token ledger
- [ ] Set and enforce budgets at every layer (per request, per user, per feature, global)
- [ ] Maintain the optimization ledger (W15-05) as a living document
- [ ] Forecast cost under growth scenarios before they happen

## 1. The token ledger (attribution first)

Every call logs: feature, user, model, prompt tokens, completion tokens, cached tokens, cost:

```python
PRICES = {"gpt-4o-mini": {"in": 0.15, "out": 0.60, "cached_in": 0.075},   # $/1M
          "gpt-4o": {"in": 2.50, "out": 10.00, "cached_in": 1.25}}

def cost_of(model, usage) -> float:
    p = PRICES[model]
    return (usage.prompt_tokens - getattr(usage, "cached_tokens", 0)) * p["in"] / 1e6 \
         + getattr(usage, "cached_tokens", 0) * p["cached_in"] / 1e6 \
         + usage.completion_tokens * p["out"] / 1e6

def ledger_row(feature, user, model, usage, latency):
    return {"ts": now(), "feature": feature, "user": user, "model": model,
            "in": usage.prompt_tokens, "out": usage.completion_tokens,
            "cached": getattr(usage, "cached_tokens", 0),
            "cost_usd": round(cost_of(model, usage), 6),
            "latency_s": latency}
```

Every call site passes its `feature` ("triage", "rag-answer", "chart") — the ledger answers the questions budgets need: which feature, which user cohort, which model, cached vs not. (W10-04's JSONL gains a cost dimension; the schema is one row.)

## 2. Budgets at every layer

| Layer | Mechanism | Example |
|---|---|---|
| **Request** | token/turn caps (W15-01 `RunBudget`) | ≤ 60k tokens, ≤ $0.50 |
| **User** | daily quota, rate limit | 100 queries/day, $2/day |
| **Feature** | monthly allocation + alert at 80% | RAG answers ≤ $500/mo |
| **Global** | hard ceiling + degradation mode | circuit-break to SLM-only (W15-04) |

```python
class FeatureBudget:
    def __init__(self, monthly_usd: float):
        self.monthly, self.spent = monthly_usd, 0.0

    def charge(self, usd: float, feature: str) -> None:
        self.spent += usd
        if self.spent > self.monthly:
            raise BudgetExceeded(f"{feature} over monthly budget")
        if self.spent > 0.8 * self.monthly:
            alert(f"{feature} at 80% of budget")          # W15-02's alerting
```

The degradation mode matters as much as the cap: over-budget features degrade to the SLM path (W15-04) or a queue — not to an outage.

## 3. The optimization ledger (living document)

From W15-05's table, now maintained continuously:

| Intervention | Date | Metric before | Metric after | $/mo saved | Status |
|---|---|---|---|---|---|
| prompt restructure (W15-04) | 2026-11 | cached 0% | cached 71% | $310 | ✅ shipped |
| router v2 (W15-04) | 2026-12 | $0.011/task | $0.004/task | $620 | ✅ shipped |
| vLLM serving (W15-03) | — | — | — | — | ⏸ pending GPU |

Each row links to the eval/PR that proved it (W14-06 → W15-05 → this ledger). New optimization ideas enter as *hypotheses with projected savings* and leave as measured rows or rejections.

## 4. Forecasting (before the invoice)

```python
def forecast(queries_per_day, tokens_per_query, model, growth_monthly=0.2, months=6):
    cost = [queries_per_day * tokens_per_query * PRICES[model]["in"] / 1e6 * 30]
    for m in range(1, months):
        queries_per_day *= (1 + growth_monthly)
        cost.append(queries_per_day * tokens_per_query * PRICES[model]["in"] / 1e6 * 30)
    return cost            # the growth curve your budget must absorb
```

Run it per feature with realistic growth (your A/B data shows adoption) — and per *planned change* (the new multimodal feature from W9 multiplies image-token costs; forecast it before building, W9-03 §4).

## Exercises

1. Instrument every capstone call site with the ledger row; run one week; produce the per-feature/per-model cost table.
2. Budget ladder: implement FeatureBudget with degradation to the SLM path (W15-04) at 100% — simulate over-budget by doubling traffic in a load test.
3. Optimization ledger: add three real rows from your W15-05 work (prompt restructure, routing, serving) with measured numbers.
4. Forecast: your ledger's growth rate × 6 months → the budget curve; mark where the SLM-routing and caching savings bend it.
5. Per-user attribution: top-10 users by cost — are they power users (fine) or a leak (bug)? Investigate the top one.

## Pitfalls

- **Attribution without feature tags** — one blended bill teaches nothing; the `feature` field is the ledger's spine
- **Cached-token accounting skipped** — W15-04's savings are invisible without the `cached` column (and the router's economics depend on it)
- **Budgets without degradation** — a hard stop is an outage; every cap has a lesser-mode (W15-04's SLM path)
- **Forecasting at constant volume** — growth compounds; the curve, not the point estimate, is the plan
- **Optimizing the wrong line** — a $200/mo line optimized for weeks while a $2,000/mo line grows unwatched; the ledger orders the work

## Resources

- OpenAI/Anthropic [usage & pricing docs](https://platform.openai.com/docs/api-reference/usage) — the `cached_tokens` fields
- W15-01 (budgets), W15-04 (caching/routing), W14-06 (baseline) — composed here
- [OpenTelemetry GenAI cost attributes](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — standard token/cost attributes (file 04)
- Cloud provider FinOps frameworks — the budget/alert vocabulary at org scale
