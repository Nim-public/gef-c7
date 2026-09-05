# The Reliability Layer — Budgets, Retries, Handlers, Live

**What you'll learn:** deploying the W15 file 01 layer into the live
path: the RunBudget around every run, tenacity on every external call,
the handler map at the boundary — with chaos drills proving each piece
fires in production shape.

## 1. The deployment checklist

```text
[ ] RunBudget constructed per run from budgets.json (versioned)
[ ] all four rails checked inside the loop
[ ] tenacity on every external call (model, DB, search) — policies per §5
[ ] circuit breakers per dependency
[ ] handler map at the API boundary
[ ] failure-class labels flowing to the trajectory store
```

| Component | Verified by |
|---|---|
| budget rails | the four stress fixtures |
| retries | fault injection |
| breakers | dependency kill drill |
| handlers | the contract battery |

The checklist is the W10 assembly review's reliability edition — every
row cites its drill, and the drills run in CI (tier 1–2), not just
once.

## 2. The chaos drills (production-shape proof)

| Drill | Method | Expected |
|---|---|---|
| kill the model API mid-run | proxy that drops connections | retry → breaker → honest message |
| slow the model 10× | latency-injecting proxy | time rail trips, partial results |
| spend spike | inflated usage accounting | spend rail trips |
| corrupt a tool response | malformed payload | ToolError hint → user contract |

The chaos drills are the fault-injection harness (W15 file 01) run
against the *live* path — each drill asserts the user-visible behavior
(honest message, partial results, reference id) and the internal
behavior (rail tripped, breaker state, ledger row).

## 3. The reliability metrics (the live signals)

| Metric | Source | Healthy |
|---|---|---|
| rail trip rates | budget ledger | <5% per rail |
| retry amplification | retries / primary calls | <30% |
| breaker openings | breaker log | rare, correlating with incidents |
| contract-battery pass | CI | 100% |

The metrics are the reliability layer's report card — the same table
family as every week, now covering the failure paths. The trip rates
under normal load are the calibration check: a rail tripping constantly
means the budget or the task design is wrong, not the rail.

## Exercises

1. Deploy the layer per the checklist; run the four chaos drills; every
   drill asserts user-visible AND internal behavior.
2. Trip-rate drill: 50 normal runs; the trip-rate table; investigate any
   rail above 5%.
3. Budget-tuning drill: from the trip-rate data, tune one limit (tighter
   or looser); record the change in `budgets.json` with a version bump.