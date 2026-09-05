# Baseline — W14-06 Numbers, Re-Measured

**What you'll learn:** the before-state: every metric the hardening will
claim to improve, re-measured on the current system under identical
conditions — the baseline is the before/after table's left column.

## 1. The baseline protocol

| Rule | Why |
|---|---|
| same eval set version | the cases are the constant |
| same model/config pins | the agent is the constant |
| same machine/environment | the noise floor is the constant |
| 3 runs × 15 cases, median | the W9 protocol |
| everything committed | the baseline is auditable |

```python
def capture_baseline() -> dict:
    return {
        "success_rate": ..., "p50_tokens": ..., "p95_latency_ms": ...,
        "cost_per_task_usd": ..., "quality_judge": ...,
        "trip_rates": {rail: rate for rail in RAILS},
        "version": AGENT_CONFIG,
    }
```

The baseline capture is the W10-04 harness run, frozen — committed as
`reports/baseline-w15.json` with the protocol header. Every later claim
of improvement points at this file.

## 2. The baseline's known weak spots (the targets)

| Weak spot | Baseline number | Week that fixes it |
|---|---|---|
| no spend rail | spend unbounded | W15 file 01 |
| retry storms under load | latency p95 | W15 file 01 |
| fallback usage untracked | blind spots | W15 file 01/02 |
| token cost (no caching) | $/task | W15 file 04 |
| all-strong routing | $/task | W15 file 04 |

The weak-spot table is the hardening week's agenda — each row names the
baseline number and the fix's week. The before/after table (file 04)
has one row per weak spot.

## Exercises

1. Capture the baseline under the protocol; commit the JSON with the
   header; verify re-running reproduces it (±noise).
2. Weak-spot drill: confirm each §2 row against your current system
   (e.g., trip a runaway and show unbounded spend) — the before-state,
   demonstrated.
3. Header drill: the baseline JSON carries the full version stamp; a
   teammate reproduces it from a fresh clone.