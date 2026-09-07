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

## 6. The production-hardening pin note (the week's manifest)

**Task:** extend `reports/sdk-versions.md` with the hardening stack: the
budget config version, the chaos-drill suite, the ledger version, and
the before/after run ids — one block.

**Worked approach:** the hardening week changed the runtime's behavior
(budgets, retries, handlers) — the manifest records which versions the
chaos drills and the before/after table verified.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 7. The production review page

**Task:** write `reports/production-review.md`: the baseline, the
reliability drill set, the ledger, and the before/after table — one
page answering "is this production-grade, and what is the evidence?"

**Worked approach:** the page composes files 01–04 into the week's
face: the before-state demonstrated, the layer chaos-proven, the
improvements attributed, and the quality guard green. The reviewer
question is answered by the table and its evidence chain.

**Pass criterion:** the page answers the production question in one
read; every claim cites its artifact.

## Pitfalls recap

- Improvements claimed without isolation — the ledger's attribution
  method is the discipline.
- The quality guard skipped for speed — a faster, worse agent fails the
  trade; the guard is checked before the celebration.
- Baselines re-measured *after* the changes "for fairness" — the
  before-state is frozen first; that is what makes after/before a
  measurement.