# 05 — Practice: Production Hardening of Your Capstone Agent

> Week 15 index: [README.md](README.md) · **Due: before Week 16 (by 2 Jan)**

*(No formal task row in the schedule — this practice hardens and optimizes the agent you've built across Weeks 10–14, against the W14-06 baseline.)*

---

## 1. Deliverable

```
production/
  reliability.py         # RunBudget, retries, handlers (file 01)
  tracing.py             # LangSmith export + PII scrubbing (file 02)
  serving/
    serve_notes.md       # vLLM/Ollama serving config + benchmarks (file 03)
  routing/
    router.py            # rule-based → calibrated router (file 04)
    routing_eval.md      # threshold sweep table
  tests/
    test_unit.py         # stubbed-LLM unit tests (file 01 §4)
    test_integration.py  # golden trajectories + budget aborts
  eval/
    results.md           # before/after: p95 latency, $/task, success rate
  README.md              # hardening report
```

Demo: the same W10-04 flagship trajectory — before (baseline) and after (hardened) — with the metrics table and one injected-failure recovery shown live.

## 2. Requirements (graded)

### Reliability (file 01)
- [ ] `RunBudget` (turns/tokens/time/spend) active on every entry point; all four aborts tested
- [ ] `tenacity` retries on retryable errors only, with a per-run retry budget and circuit breaker
- [ ] Exception→user-contract handler map; partial results on abort (checkpoints or scratchpad)
- [ ] Unit tests stubbed (no LLM) covering budget/validation/parsers; integration suite pinned

### Observability (file 02)
- [ ] LangSmith (or equivalent) tracing on, with PII scrubbing before export
- [ ] Regression dataset hosted (W10-04 cases); one prompt version change → diff report
- [ ] Five alert conditions defined with thresholds from your baseline

### Optimization (files 03/04)
- [ ] Prompt restructure for cache hits — `cached_tokens` measured before/after
- [ ] Serving benchmark: vLLM/WSL or Ollama — tokens/s + p95 at 1/4/16 concurrency, documented config
- [ ] Router calibrated on your harness: threshold sweep table (accuracy vs cost), misclassification rates both ways

## 3. The before/after table (the graded centerpiece)

From your W14-06 baseline (p95, $/task) to post-hardening:

| Metric | Baseline (W14) | Hardened (W15) | Delta |
|---|---|---|---|
| p95 latency (s) |  |  |  |
| p50 latency (s) |  |  |  |
| $/task |  |  |  |
| cached-token share |  |  |  |
| success rate (15 cases) |  |  |  |
| tool-error rate |  |  |  |

Every improvement row names **which intervention** moved it (prompt restructure? routing? serving config?) — attribution is the deliverable, not just the delta.

## 4. Rubric

| Area | Weight |
|---|---|
| Reliability layer (budgets, retries, handlers, partial results) | 25% |
| Observability (LangSmith/JSONL merge, regression dataset, alerts) | 20% |
| Optimization (caching measured, serving benchmarked, router calibrated) | 30% |
| Before/after table with attribution | 15% |
| README hardening report | 10% |

## 5. README hardening report (answer explicitly)

1. **Baseline vs hardened** table (§3) with per-row attribution
2. **Limits chosen** and the failure drills that validated them (four aborts, retried storms, circuit breaker)
3. **Observability topology**: LangSmith + your JSONL + alerts — what watches what
4. **Optimization ledger**: each intervention, its measured effect, and whether it stayed in the config
5. **W16 bridge**: your agent's remaining quality gaps (from the regression runs) — those become the fine-tuning/eval candidates of the final course week. Also: the LlamaIndex task will add a *new* retrieval system — list which production layers (budgets, tracing, routing) it must inherit on day one.

## 6. Stretch (pick one)

- Chaos drill: randomly fail 20% of tool calls during an eval run; measure recovery rate with vs without the error-phrasing layer (W10-05)
- Two-tier serving end-to-end: vLLM SLM + frontier API behind the router, single eval table across both
- Load profile: 100 sequential + 20 concurrent runs; produce a latency-distribution plot and identify the saturation point

Office Hours (24 Dec): bring the before/after table — Week 16's evals/fine-tuning decisions all read against the hardened numbers.
