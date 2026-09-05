# Regression Suites — Trajectory Assertions in CI

**What you'll learn:** the W10 baseline gate, upgraded to trajectory
assertions: shape tests (tools, steps, routes) plus value tests (metrics
vs baseline) — running in CI on every prompt or description change.

## 1. The two assertion layers

| Layer | Asserts | Catches |
|---|---|---|
| Shape | tools-as-sets, max steps, refusal behavior, handoff targets | wiring/description regressions |
| Value | success rate, judge totals, token p50 vs baseline | quality drift |

```python
@pytest.mark.parametrize("task", EVAL_SET_V2)
def test_trajectory_shape(task, canned_agent):
    run = run_agent(canned_agent, task["query"], max_steps=task["max_steps"])
    assert {t["tool"] for t in run.trace} == task["expected_tools"]
    assert run.steps <= task["max_steps"]
    if task.get("must_refuse"):
        assert run.outcome == "refused"
    if task.get("expected_handoff"):
        assert run.last_agent.name == task["expected_handoff"]
```

Shape tests run on the canned LLM (deterministic, seconds); value tests
run nightly on the real model (3× per task, majority). The split is the
W10 battery discipline, now covering topology.

## 2. The value gate (baseline ± tolerances)

```python
BASELINE = {
    "success_rate": 0.80, "mean_judge": 6.8,
    "p50_tokens": 5200, "handoff_rate": 0.37,
}
TOL = {"success_rate": 0.05, "mean_judge": 0.5, "p50_tokens": 0.15,
       "handoff_rate": 0.10}

def value_gate(current: dict) -> int:
    for k, base in BASELINE.items():
        if current[k] < base - TOL[k] * base:
            print(f"REGRESSION {k}: {current[k]} vs {base}")
            return 1
    return 0
```

Tolerances are *relative* and per-metric — tokens swing more than success
rates. The gate fails loud with the metric name and both numbers; a red
CI names the regression, not just its existence.

## 3. What the suite catches, by construction

| Change | Which layer catches it |
|---|---|
| tool description rewording | shape (tools-as-sets drift) |
| new handoff added | shape (unexpected handoff target) |
| model bump | value gate (nightly; all metrics) |
| budget trim | shape (steps) + value (tokens) |
| guardrail threshold change | shape (refusals) + value (success) |

The map is the point: each edit class has a named tripwire. When CI goes
red, the *layer* that fired tells you which edit class regressed before
you read a line.

## 4. Baseline maintenance (the standing rule)

```text
Baselines move only via accepted eval runs:
  1. run the harness on the candidate change
  2. review the diff (metric by metric)
  3. accept → commit new baseline JSON with the eval header
  4. reject → revert the change, not the baseline
```

The W07 rule, unchanged across six weeks, because it is the thing that
makes every gate mean something.

## Exercises

1. Port the eval set into `test_trajectory_shape`; run on the canned
   agent; fix any shape mismatch (or correct the set's expectations).
2. Value-gate drill: degrade a description on purpose; watch shape *and*
   value gates fire; restore; both green — the mutation test for the
   gates themselves.
3. Tolerance tuning: set token tolerance to 5% and watch nightly noise;
   raise it until false positives stop (without masking a real 10%
   regression); record the chosen tolerance and its rationale.

## Pitfalls

- Value gates on daily CI runs — cost and flakiness; nightly + pre-demo,
  shape gates on every push.
- Tolerances tuned to make CI green — the tolerance exists to catch
  regressions, not to hide them; document every widening.
- Shape expectations copied from observed behavior — expectations come
  from the eval set's design (file 06-02), or the suite grades your
  agent's habits instead of your spec.

## Resources

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/02-three-dimension-metrics.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/04-measuring-agents-patterns/02-three-dimension-metrics.md)
  — the metrics this gate guards.
- [`../06-practice-agents-sdk-capstone/`](../06-practice-agents-sdk-capstone/)
  — the port this suite will accept or reject.