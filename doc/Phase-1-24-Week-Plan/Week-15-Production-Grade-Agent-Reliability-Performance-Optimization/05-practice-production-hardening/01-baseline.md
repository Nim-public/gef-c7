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

## 4. The baseline metric definitions (the left column's spec)

| Metric | Definition | Instrument |
|---|---|---|
| success rate | gold-matched outcomes / runs | eval set + harness |
| p50/p95 tokens | per-task token distribution | fitter ledger |
| p50/p95 latency | end-to-end wall time | the ledger wrapper |
| $/task | spend per completed task | cost model + usage |
| quality judge | rubric total / 8 | the calibrated judge |
| rail trip rates | aborts per rail | the budget ledger |

The definitions are the baseline's spec — every metric names its
instrument, so the after-state cannot quietly change the measuring
stick. The W9-04 metric dictionary holds the full formulas; this table
is the production week's subset.

## 5. The environment pin (the noise floor's declaration)

```markdown
# Baseline environment
- machine: [your spec], [OS], [python]
- model: [pinned id], temperature 0
- corpus: manifest v[N], knowledge wrap parity green
- network: [connection class if hosted APIs]
- time of runs: [window — hosted APIs vary by load]
```

The environment pin is the noise floor's declaration — hosted APIs vary
by time of day, and a baseline captured at 3 a.m. is not comparable to
an after-state captured at peak. The pin makes the comparison honest or
explains the noise.

## Exercises

1. Capture the baseline under the protocol; commit the JSON with the
   header; verify re-running reproduces it (±noise).
2. Weak-spot drill: confirm each §2 row against your current system
   (e.g., trip a runaway and show unbounded spend) — the before-state,
   demonstrated.
3. Header drill: the baseline JSON carries the full version stamp; a
   teammate reproduces it from a fresh clone.
4. Noise-floor drill: run the baseline twice at different hours; the
   delta bounds the noise — the after-state's improvements must exceed
   it to count.