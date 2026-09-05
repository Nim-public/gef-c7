# Exercises — Production Hardening

Stretch tasks and the self-review rubric. The deliverable: the measured
baseline, the live reliability layer, the attributed ledger, and the
before/after table.

## 1. The baseline (from 01-baseline)

**Task:** capture the baseline under the protocol; commit the JSON; the
weak-spot table confirmed against the live system.

**Worked approach:** the baseline is the before/after table's left
column — its protocol (same set, pins, machine, 3× median) is the
before/after's validity. The weak-spot confirmation is the week's
agenda-setting.

**Pass criterion:** baseline JSON committed and reproducible; weak spots
demonstrated live.

## 2. The reliability layer live (from 02-reliability-layer)

**Task:** deploy per the checklist; run the four chaos drills; the
trip-rate table over 50 normal runs; one budget tuned from the data.

**Worked approach:** the chaos drills assert user-visible *and*
internal behavior — the drills are the deployment's acceptance. The
trip-rate tuning is the budget's calibration, version-bumped.

**Pass criterion:** checklist green; chaos drills pass; trip rates <5%;
the tuned budget version-bumped.

## 3. The optimization ledger (from 03-optimization-ledger)

**Task:** create the ledger; land prefix caching and the routing ladder;
every row measured alone then cumulative; the verification row included
(positive cost, defended).

**Worked approach:** the ledger's discipline is one-variable-per-row and
cumulative honesty — the verification row's positive cost is the
program's trade made explicit.

**Pass criterion:** rows committed with run artifacts; the cumulative
column quoted by the demo.

## 4. The before/after table (from 04-before-after)

**Task:** run the after-state eval; fill the table with attribution;
the quality guard verified (no regression); the demo page rendered.

**Worked approach:** the table is the week's face — every delta
attributed, every attribution cited, the quality guard checked before
any celebration.

**Pass criterion:** the table committed; the quality guard green; the
demo page rendered with linked artifacts.

## 5. Self-review rubric (the production week's rubric)

| Criterion | Evidence | Points |
|---|---|---|
| Baseline captured + reproducible | baseline JSON | 4 |
| Reliability layer live, chaos-proven | drill results | 4 |
| Ledger: attributed rows incl. honesty premium | ledger | 4 |
| Before/after table with attribution + quality guard | the table | 4 |
| Pin notes updated (budgets, caching, routing) | pin notes | 2 |

**Pass bar:** 15/18 to close Week 15. The ledger (4-pointer) is the
hardening week's honesty — improvements without attribution are
anecdotes.

## Pitfalls recap

- Improvements claimed without isolation — the ledger's attribution
  method is the discipline.
- The quality guard skipped for speed — a faster, worse agent fails the
  trade; the guard is checked before the celebration.
- Baselines re-measured *after* the changes "for fairness" — the
  before-state is frozen first; that is what makes after/before a
  measurement.