# Offline vs Online — Golden Sets and Live Signals

**What you'll learn:** the two signal families: offline evals (golden
sets, controlled, comparable) and online signals (live traffic, real but
noisy) — what each detects, and the bridge that turns online failures
into offline cases.

## 1. The two families

| Property | Offline (golden set) | Online (live signals) |
|---|---|---|
| data | fixed, gold-labeled | whatever arrives |
| comparability | high (versioned) | low (traffic shifts) |
| catches | regressions, quality bars | emergent failures, distribution drift |
| latency of signal | per eval run | continuous |
| cost | per run | free (logs) |

The offline set is the *contract* (does the system meet its bar?); the
online signals are the *radar* (is the world drifting away from the
contract?). W13's self-improving loop (mining failures) is the bridge.

## 2. The online signal catalog

| Signal | Source | Drift it detects |
|---|---|---|
| refusal rate | outcome counts | corpus coverage vs real queries |
| route distribution | router decisions | query mix shift |
| zero-hit rate | retrieval logs | vocabulary drift |
| latency p95 | the ledger | load or dependency decay |
| human-correction rate | edit protocol | classification rot |

Each signal has a threshold (the trip-rate discipline from W15 file
01) — a signal crossing its threshold names the offline work: add cases,
re-chunk, re-route. The catalog is the production review's radar page.

## 3. The bridge (online failure → offline case)

```text
1. online signal crosses threshold (e.g., zero-hit rate up)
2. sample the offending queries
3. cluster (the W13 mining query)
4. gold-label from your data (or discover the corpus gap)
5. add the case family to the eval set (version bump)
6. the offline set now guards against the drift's return
```

| Step | Artifact |
|---|---|
| 2–3 | the cluster table |
| 4 | gold labels or a corpus-gap ticket |
| 5 | the eval-set changelog row |

The bridge is the self-improving loop (W14 file 04-03) driven by live
signals instead of post-mortems — the same artifacts, a faster trigger.

## 5. The signal thresholds (the radar's calibration)

| Signal | Threshold | Set from |
|---|---|---|
| refusal rate | >25% weekly | the baseline week's distribution |
| zero-hit rate | >10% of queries | retrieval logs |
| route distribution shift | >20% class-mix change | the router logs |
| latency p95 | >1.5× ledger baseline | the ledger |
| human-correction rate | >5% | the edit protocol |

The thresholds are the W15 trip-rate discipline applied to online
signals — each set from a measured baseline, each with an owner and a
cadence. A signal without a threshold is a chart, not a radar.

## 6. The bridge's failure mode (the radar that cries wolf)

| Failure mode | Symptom | Fix |
|---|---|---|
| threshold too tight | thresholds cross weekly, no real drift | widen from the baseline's noise floor |
| bridge cases added without clustering | the eval set fills with duplicates | the cluster step is mandatory |
| signals ignored after false alarms | nobody reads the radar | recalibrate before the next true alarm |

The failure modes are the radar's maintenance — a bridge that adds
cases on every blip dilutes the eval set; the clustering step and the
noise-floor calibration are what keep the radar's signal real.

## Exercises

1. Implement the signal catalog's thresholds on your live logs (or
   simulated traffic); produce the signal dashboard table.
2. Bridge drill: cross one threshold with synthetic traffic; walk the
   six steps; the eval set gains the case family.
3. Signal-vs-golden drill: name one failure each signal family alone
   would miss — the two families' necessity, argued from your system.
4. Calibration drill: set every threshold from its baseline's noise
   floor; a false alarm drill proves the calibration matters.