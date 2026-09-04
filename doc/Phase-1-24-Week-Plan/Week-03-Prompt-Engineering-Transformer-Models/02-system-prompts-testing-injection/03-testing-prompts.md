# 02.3 — Testing Prompts

> Subfolder index: [README.md](README.md) · Parent: [../02-system-prompts-testing-injection.md](../02-system-prompts-testing-injection.md)

---

## What you'll learn

- The prompt test pyramid: unit (stubbed) → contract (real LLM, schema) → integration (trajectories)
- Determinism management: what to pin, what to tolerate
- The regression gate in CI

## 1. The test pyramid for prompts

| Level | LLM calls | What it verifies | Speed |
|---|---|---|---|
| **Unit** | 0 (stubbed responses) | rendering, validation, parsers, budgets | ms |
| **Contract** | 1 per case | output schema, refusal behavior | seconds |
| **Integration** | multi-turn trajectories | end-to-end behavior | minutes |
| **Regression** | full golden set | no behavioral drift across versions | minutes |

The pyramid's rule: **most tests stub the LLM**. Rendering, validation, budget checks, and parser logic are pure code — they get fast unit tests. Only schema/refusal checks need real calls.

```python
# unit: the renderer, stubbed
def test_render_missing_variable():
    with pytest.raises(KeyError):
        render("Hello $name")            # no name provided

# contract: real call, schema check
def test_triage_schema(triage_chain):
    out = triage_chain.invoke("charged twice")
    assert isinstance(out, Triage) and out.category in {"BILLING", "TECHNICAL", "ACCOUNT"}

# integration: trajectory
def test_full_trajectory(bot):
    r = bot.reply("I was charged twice")
    assert "BILLING" in r["route"] and r["citations"]
```

## 2. Determinism management

| Control | Mechanism |
|---|---|
| temperature=0 in tests | greedy output, stable |
| pinned model revision | no silent drift (W2-01) |
| pinned prompt versions | the test tests *this* prompt (W16-01) |
| recorded responses for unit tier | stubbed, no network |

Residual nondeterminism: even at T=0, providers may vary slightly across infra. The suite tolerates it: schema assertions (not exact strings), and flaky-case quarantine with tracking (W10-04's logs decide whether it's the test or the model).

## 3. The regression gate in CI

```yaml
# on PR touching prompts/** or src/agent/**
- run: pytest tests/unit -q                 # seconds, stubbed
- run: pytest tests/contract -q             # real calls, ~1 min
- run: python eval/regression.py --baseline eval/baseline.json   # W16-01
```

The gate: unit always; contract on prompt changes; regression compares against the pinned baseline (W16-01's versioned set) with a tolerance (E8-04's distributional discipline). Fail → the PR cannot merge — the same gate the E8-01 manifest enforces at deploy.

## 4. Flaky test handling

| Symptom | Cause | Action |
|---|---|---|
| intermittent schema failures | sampling noise despite T=0 | retry once; if persistent, quarantine + investigate |
| cross-day drift | model/infra updates | re-pin, re-baseline (W16-01) |
| order-dependent failures | shared state between tests | isolate fixtures |
| timeout flakiness | provider latency | generous timeouts, retry at the client |

Flaky tests are *data*: each one is either a real nondeterminism (product risk) or a test-design bug. Quarantine with a ticket — never delete silently (W10-04's log discipline).

## Exercises

1. Pyramid build: convert 5 of your W3-02 manual checks into the pyramid — 3 unit (stubbed), 2 contract; measure the suite runtime.
2. Stub library: record 20 real responses; build a replay client for unit tests — verify replay parity with live outputs.
3. Drift drill: update the model revision; run the regression against the old baseline — quantify the drift; re-baseline with a changelog entry (W16-01).
4. Quarantine tracker: mark 2 flaky tests; implement the retry-once + quarantine flow; ensure quarantined tests still report.
5. The gate drill: plant a prompt regression (weaken a refusal rule); verify CI blocks the merge; then fix and watch it pass.

## Pitfalls

- **Exact-string assertions on sampled output** — flaky by design; assert schema and semantic anchors
- **Tests sharing mutable state** — parallel runs cross-contaminate; fresh fixtures per test
- **Real-LLM unit tests** — slow, costly, flaky; stub the client boundary
- **Baseline drift without re-baselining** — the tolerance grows until the gate is meaningless; re-baseline on every intentional change
- **Prompt changes without battery runs** — the CI gate exists to prevent it; bypassing it is the anti-pattern

## Resources

- W3-02 parent, W15-01/02 (reliability/observability), W16-01 (versioning) — composed here
- pytest [fixtures/monkeypatch](https://docs.pytest.org/en/stable/) — the stubbing toolkit
- W11-05 (trace assertions) — the integration-tier pattern
