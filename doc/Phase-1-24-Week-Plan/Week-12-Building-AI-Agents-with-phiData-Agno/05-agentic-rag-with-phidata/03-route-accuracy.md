# Route Accuracy — Measuring the Model's Routing vs the W9 Router

**What you'll learn:** the measurement protocol for the model-as-router:
expected-route gold labels, tool-usage assertion, and the head-to-head
against the W9 regex router on identical queries.

## 1. The measurement design

| Component | Spec |
|---|---|
| queries | your 25-task eval set (classes preserved) |
| gold | expected tool-power per query (from file 02's battery) |
| runs | 3 per query, majority |
| metric | route accuracy = correct power chosen / total |
| comparison | same queries through the W9 regex router |

```python
def route_accuracy(runs: list[dict], gold: dict[str, set[str]]) -> float:
    correct = 0
    for r in runs:
        used = {t["tool"] for t in r.trace if t["type"] == "tool"}
        correct += used <= gold[r["query"]] and bool(used)
    return correct / len(runs)
```

The gold is a *set* (multi-power answers are legal for compound
queries) — strictness matches the W9 router's contract, not the model's
phrasing.

## 2. The head-to-head table

| Class | n | W9 regex acc | Model acc | Δ | Reading |
|---|---|---|---|---|---|
| charts | 6 | 0.83 | 0.83 | 0 | tie — regex was fine |
| exact-term | 5 | 1.00 | 0.93 | −0.07 | model paraphrases; FTS hint helps |
| numeric | 5 | 0.60 | 0.93 | +0.33 | model beats regex on ambiguity |
| ambiguous | 5 | 0.40 | 0.73 | +0.33 | the model's whole value |
| absent | 4 | 1.00 | 1.00 | 0 | both refuse |

The expected shape: regex wins on rigid classes, the model wins on
ambiguous ones — and the *hybrid* (regex pre-router for exact-term,
model otherwise) is the Capstone-grade answer if your numbers say so.

## 3. Miss analysis (the W10 discipline, re-applied)

| Miss type | Example | Fix locus |
|---|---|---|
| under-search | answered without searching | constitution floor (file 01) |
| over-search | 3 searches on a lookup | stop rule (file 02-03) |
| wrong power | SQL for a semantic question | priority wording (file 02) |
| mixed sources silently | web fact, unlabeled | `source` field guardrail |

Each miss gets the predict-actual treatment (W10 file 03): the diff is
one line, the fix is one wording or schema change, the A/B measures it.

## 4. The comparison table, committed

```text
# Route accuracy — eval-set v2 — model pinned — 2026-09-05
| router      | accuracy | notes |
|---|---|---|
| W9 regex    | 0.77     | measured (W9-05) |
| model (W12) | 0.90     | this file |
| hybrid      | 0.93     | regex for exact-term, model else |
```

The hybrid row is computed, not aspirational: route by regex when the
query matches an exact-term pattern, else trust the model. It reuses
your W9 router *as a component* — the framework week's theme, one more
time.

## Exercises

1. Run the head-to-head over your 25 queries; produce the table with the
   Δ column and readings.
2. Miss-analysis drill: take every model miss; classify into the §3
   types; fix the modal type; remeasure.
3. Hybrid drill: implement the regex-for-exact-term pre-router; measure
   the hybrid accuracy; decide per the table.

## Pitfalls

- Gold labels invented after running — the eval set defines them;
  retro-routing is grading your own homework.
- Accuracy without the miss taxonomy — 0.90 tells you nothing about what
  to fix; the miss types do.
- Hybrid claimed but not measured — compute it from the same runs; the
  table's third row is earned.