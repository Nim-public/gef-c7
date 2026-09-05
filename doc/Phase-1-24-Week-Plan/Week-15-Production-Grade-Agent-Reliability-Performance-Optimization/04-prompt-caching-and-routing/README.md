# Deep-Dive: Prompt Caching & Model Routing

Parent overview: [`../04-prompt-caching-and-routing.md`](../04-prompt-caching-and-routing.md)

Two hosted-cost levers: prompt caching (pay once for stable prefixes)
and model routing (pay small-model prices for easy queries). This
subfolder covers the stable/variable prefix rule, cache verification in
billing, the rules→classifier→RouteLLM routing ladder, and threshold
calibration.

## File map

| File | What it covers |
|---|---|
| [`01-prefix-structuring.md`](01-prefix-structuring.md) | The stable/variable order rule |
| [`02-cache-verification.md`](02-cache-verification.md) | `cached_tokens` in billing |
| [`03-model-routing.md`](03-model-routing.md) | Rules → classifier → RouteLLM |
| [`04-threshold-calibration.md`](04-threshold-calibration.md) | Misroute costs both ways |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-prefix-structuring.md` — reorder prompts to be cacheable.
2. `02-cache-verification.md` — verify the discount is real.
3. `03-model-routing.md` — the routing ladder.
4. `04-threshold-calibration.md` — calibrate the router's thresholds.

## Prerequisites

- [`../01-reliability-limits-retries-tests/01-run-budget.md`](../01-reliability-limits-retries-tests/01-run-budget.md)
  — the spend rail this optimizes.
- [`../03-inference-optimization/03-vllm-serving.md`](../03-inference-optimization/03-vllm-serving.md)
  — prefix caching, self-hosted edition.