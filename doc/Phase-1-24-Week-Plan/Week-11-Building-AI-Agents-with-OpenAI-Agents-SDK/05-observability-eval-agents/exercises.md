# Exercises — Observability & Eval for Agents

Expanded set with worked approaches. The deliverable: merged capture with
parity proven, replay workflow rehearsed on a planted failure, and the
trajectory regression suite in CI.

## 1. Span mapping + parity (from 01, 03)

**Task:** implement `walk_spans`/`spans_to_row`/`merge_row`; run the
parity test over 30 runs; document systematic gaps with sign and cause.

**Worked approach:** the parity witness column (`token_parity`) turns
the test into a per-row audit — systematic gaps (same sign every row)
indicate an accounting rule difference; random gaps indicate flakiness.

**Pass criterion:** 30/30 parity; the gap cause named in the metric
dictionary.

## 2. Replay debugging, executed (from 02-replay-debugging)

**Task:** plant a failure (vague description → tool misuse); run the
four-question workflow; produce the post-mortem artifact; add the test
that would have caught it.

**Worked approach:** the post-mortem's value is the *added test* — a
post-mortem without a regression case is a diary entry. The planted
failure should be one you would plausibly ship.

**Pass criterion:** post-mortem committed; the added test red before the
fix, green after.

## 3. Failure taxonomy over real runs (from 02)

**Task:** label every failed run in your store with the five-layer
taxonomy; produce the distribution; name Week 12's first task from it.

**Worked approach:** the distribution usually concentrates (70%+
descriptions-and-data, 20% budget, 10% guardrails) — the concentration
is the roadmap. Label from evidence (trace bisection), not vibes.

**Pass criterion:** distribution table committed; one Week-12 task
derived from the modal class.

## 4. Regression suite in CI (from 04-regression-suites)

**Task:** wire shape tests (push CI) + value gate (nightly); run the
mutation drill (degraded description → both layers red; restore → green).

**Worked approach:** the mutation drill proves both layers independently
— shape catches wiring, value catches quality. Tolerances set from *your*
nightly noise, documented.

**Pass criterion:** CI green on restore; both layers red under their
respective mutations.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Parity test green over 30 runs | merge test | 4 |
| Replay workflow + post-mortem + test | reports/post-mortem.md | 4 |
| Failure taxonomy over all failed runs | distribution table | 3 |
| Shape + value gates in CI, mutation-proven | CI config + drill | 3 |
| Metric dictionary updated (parity, handoffs) | dictionary | 2 |

**Pass bar:** 13/16 to proceed to file 06 (the SDK capstone). The parity
test (4-pointer) is the merge's foundation — one store or none.

## 7. The replay runbook

**Task:** write `reports/replay-runbook.md`: the debugging workflow as a
runbook — the four questions, the signature-to-layer table, the replay
snippet, the post-mortem template, and the speed KPI — the page you open
at 2 a.m. before a demo.

**Worked approach:** the runbook is the workflow in imperative form,
tested once on the planted failure. Its quality gate is the speedrun:
a teammate following it fixes the failure without talking to you.

**Pass criterion:** the runbook drives a fresh fix under the time
target; every command in it was executed as written.

## 6. The observability one-pager

**Task:** write `reports/observability.md`: the capture architecture
(spans → merge → parquet + JSONL), the two-layer regression suite, the
replay workflow, and the failure taxonomy distribution — one page, every
number cited.

**Worked approach:** this is the week's face for reviewers: "how do you
know what the agent did and whether it regressed?" — the page answers
with the artifacts, not promises. The debug-speed number from file 02's
drill belongs here.

**Pass criterion:** the page passes the teammate test: they can
reproduce a failure investigation from it alone, using the linked
commands.

## Pitfalls recap

- Post-mortems without added tests — the failure returns next week in a
  new costume.
- Parity failures ignored as "accounting noise" — systematic gaps are
  bugs; sign and consistency tell you which.
- Shape expectations copied from behavior — the eval set's design is the
  spec; observed habits are not a spec.