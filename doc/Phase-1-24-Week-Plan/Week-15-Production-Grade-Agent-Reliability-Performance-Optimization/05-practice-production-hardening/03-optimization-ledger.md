# The Optimization Ledger — Attributed Improvements

**What you'll learn:** the optimization ledger: every improvement
(prompt reorder, routing, caching, middleware) recorded with its
*attributed* delta — measured in isolation, summed honestly.

## 1. The ledger format

| # | Change | Measured alone | Attributed delta | Cumulative |
|---|---|---|---|---|
| 1 | prefix reorder (caching) | −38% prompt cost | −38% | −38% |
| 2 | routing ladder | −12% tokens | −9% | −43% |
| 3 | middleware (retry→middleware) | 0 cost, +reliability | n/a | — |
| 4 | verify nodes | +5% tokens | +5% | −38% |

| Rule | Why |
|---|---|
| measured alone first | the delta must be attributable |
| then cumulative | interactions are real but must not hide |
| negative improvements recorded | honesty (verification costs tokens) |
| every row cites its runs | the ledger is evidence |

The ledger is the W12-04 cost table's dynamic form: optimizations
interact (caching and routing compound; verification costs), and the
cumulative column is the only number the demo quotes.

## 2. The attribution method

```python
def attributed_delta(baseline: float, after_change: float) -> float:
    return (after_change - baseline) / baseline

# each change measured against the PREVIOUS cumulative state,
# not the original baseline — deltas chain like the fitter's budget.
```

| Change type | Measurement |
|---|---|
| prompt change | the pvN bump, A/B on the eval set |
| routing change | the threshold change, both models run |
| middleware change | fault-injection + cost runs |
| verification change | the mutation drill + cost runs |

The attribution is one-variable-per-experiment (the W9 bake-off rule):
each ledger row's delta is measured against the previous cumulative
state with everything else held.

## 3. The ledger's maintenance (it never closes)

| Trigger | Ledger action |
|---|---|
| a new optimization lands | a new row |
| a regression appears | the row's delta turns negative — visible |
| a component upgrades | re-attribute the affected rows |
| the demo quotes a number | it must be the cumulative column |

The maintenance is the standing rule: the ledger is a living table, and
the demo quotes the cumulative column — which is why every row's
attribution matters.

## Exercises

1. Create the ledger; add row 1 (prefix reorder) with its measured
   delta; commit with the run artifacts.
2. Attribution drill: land the routing ladder; measure against the
   cumulative state; the delta must reflect the interaction with row 1
   (caching changes the routing economics).
3. Honesty drill: add the verification row (positive token cost); the
   ledger shows the honesty premium — and the memo defends it.