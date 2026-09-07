# The Test Pyramid — Stubbed Unit, Contract, Integration, Soak

**What you'll learn:** the four test tiers for agents: stubbed unit
tests (seconds), contract tests (recorded-model), integration (live,
nightly), and soak tests (hours, drift and leak detection) — each with
its CI slot and what it alone can catch.

## 1. The pyramid

| Tier | Model | Runtime | Catches | CI slot |
|---|---|---|---|---|
| 4. soak | real, hours | hours | memory leaks, drift, cost creep | weekly |
| 3. integration | real | minutes | wiring, latency, fallbacks | nightly |
| 2. contract | recorded responses | seconds | schema/prompt/parse breaks | every push |
| 1. stubbed unit | none | seconds | logic, reducers, policies | every push |

The pyramid inverts cost and coverage: tier 1 runs thousands of times
per day and catches logic; tier 4 runs weekly and catches what only
*time* reveals. Every tier below this program's existing suites is
already built — this file is the *organization*.

## 2. Tier 2 — contract tests (recorded responses)

```python
# tests/contracts/cassettes/task3.yaml — recorded model responses
def test_task3_contract(vcr):
    result = run_agent("Which chart shows Q3 margin?")
    assert result.outcome == "success"
    assert result.citations == ["u042"]
```

Contract tests replay *recorded* model responses against the current
code: the prompt templates, parsers, validators, and tool wiring are
exercised for real; only the model is frozen. They catch the breaks
that stubs hide — a changed variable name in a template, a new required
field, a reordered tool schema.

## 3. Tier 4 — soak tests (what only time shows)

| Soak signal | Detection | Failure it catches |
|---|---|---|
| memory growth | RSS per 100 runs | leaked state, growing histories |
| cost creep | $/task trend | prompt bloat, retrieval inflation |
| quality drift | R@10 / judge trend | model updates, cache rot |
| error-rate creep | failure-class counts | a dependency slowly dying |

```python
def soak_checkpoint(run_no: int, rss_mb: float, cost: float, quality: float):
    log_metric(run_no, rss_mb=rss_mb, cost=cost, quality=quality)
    assert rss_mb < 2000, "memory leak suspected"
```

Soak runs the eval set 200× overnight with checkpoints every 25 runs —
the assertions are *trends*, not single values. The W10 soak drill's
ancestor: the fixture that passed 5 runs and failed at 50.

## 4. The pyramid's CI wiring

```yaml
push:    [tier-1, tier-2]
nightly: [tier-3]
weekly:  [tier-4-soak]
pre-demo: [tier-1..3 + acceptance]
```

| Rule | Why |
|---|---|
| tiers never skip downward | push CI must stay under 2 min |
| nightly failures block deploys | tier 3 is the deploy gate |
| soak failures open tickets | weekly; the drift chart drives |

## 5. The pyramid's cost table (the CI budget)

| Tier | Runs/week | Machine time | $/week (API) |
|---|---|---|---|
| 1. unit | ~2000 | ~70 min CI | 0 |
| 2. contract | ~200 | ~35 min CI | 0 |
| 3. integration | ~30 | ~45 min | ~$5 |
| 4. soak | 1 | ~8 h | ~$20 |

The cost table is the pyramid's own budget — the test suite's spend is
part of the program's ledger. Tier 3/4 API costs are the price of the
nightly drift detection and the weekly trend chart; both pay for
themselves in one prevented demo failure.

## Exercises

1. Organize the existing suites into the pyramid; verify tier runtimes;
   anything over budget gets marked or split.
2. Contract-cassette drill: record 10 task responses; break a template
   variable; tier 2 must catch it while tier 1 passes.
3. Soak drill: run the eval set 100× overnight with checkpoints; the
   trend chart (RSS, cost, quality) is the deliverable.
4. Pyramid drill: introduce one bug per tier (logic, template, wiring,
   drift config); each tier must catch exactly its own bug.
5. Cost drill: fill §5 with your actual counts; the CI minutes and API
   spend land in the program ledger.
6. Shape drill: count tests per tier; draw the pyramid; name any
   anti-pattern present and its fix.

## 6. The pyramid's anti-patterns (what breaks the shape)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| the ice-cream cone | more integration than unit tests | push logic into pure functions |
| the hourglass | heavy unit + heavy E2E, no contracts | add tier 2 cassettes |
| the broken pyramid | real-model calls on push | move to nightly |
| flaky middle | contract tests failing randomly | re-record; fix ordering |

The anti-pattern catalog is the pyramid's health check — the shape is
diagnosed by counting tests per tier. The fix column cites the
structure: pure functions feed tier 1, recorded responses feed tier 2,
real models stay in tiers 3–4.