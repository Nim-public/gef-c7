# Exercises — Measuring Agents & Patterns

Expanded set with worked approaches. The deliverable: the harness producing
the three-dimension scorecard over ≥25 stored trajectories, judge
calibrated.

## 1. The store, filled (from 01-trajectory-instrumentation)

**Task:** wire the trajectory schema into your loop; run 25 queries from
your eval set; verify the parquet + JSONL pair (metrics + traces) with
the completeness test.

**Worked approach:** the completeness test (every field present, steps ==
trace length) runs per write — instrumentation bugs surface at run time,
not at eval time.

**Pass criterion:** 25 rows, 25 trace files, completeness test green on
all.

## 2. Scorecards by class (from 02-three-dimension-metrics)

**Task:** produce the class-split scorecard (success, efficiency,
process) with gold labels from your eval set; write the two-sentence
reading.

**Worked approach:** gold labels come from file 06's expected-route
table — success means *right answer via right behavior*. The reading
names the worst cell and its fix owner (descriptions, budget, or prompt).

**Pass criterion:** table committed to `reports/agent-scorecard.md` with
header (model, date, n); reading names one action.

## 3. Gate dry-run (from 03-hitl-gates)

**Task:** implement `GATE_POLICY` + simulated HITL (scripted 80/20
approver); measure gate rate, approval rate, and caught-rejects over 50
runs.

**Worked approach:** the simulation validates the *plumbing* (payloads,
options, logging) — the human judgment study is a later-week exercise.
Gate rate >20% on read-only workloads is a policy bug; expect ~0 gates
until write tools exist.

**Pass criterion:** report shows gate rate ≈0 on read-only runs; the
simulated write-tool case gates 100%.

## 4. Judge calibration (from 04-llm-as-judge)

**Task:** hand-label 10 trajectories; run the judge twice; produce the
agreement table; fix the lowest-agreement dimension with an anchored
example; remeasure.

**Worked approach:** the two-run self-consistency check comes first —
a judge that disagrees with itself has no resolution to calibrate. The
anchored example names what 0/1/2 look like *in your domain*.

**Pass criterion:** self-consistency ±1; human agreement ≥80% on 3 of 4
dimensions; the fourth documented as "known weak, hand-checked".

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| 25 trajectories, completeness test green | parquet + JSONL | 3 |
| Class-split scorecard + reading | reports/agent-scorecard.md | 4 |
| Gate policy + simulated report | gate report | 3 |
| Judge calibrated (2 runs, agreement table) | calibration table | 3 |
| Outcome-classifier vs hand-labels ≥8/10 | drill note | 2 |

**Pass bar:** 11/15 to proceed to file 05 (prompt engineering). The
scorecard (4-pointer) is the harness's face — it feeds every later
week's regression gates.

## 6. The instrumentation debt audit

**Task:** list every field in the trajectory schema; for each, name its
capture seam (loop return, fitter, registry audit, post-classifier) — any
field captured *inside the model call* is debt; migrate it to a seam.

**Worked approach:** the audit is one table (field → seam → status).
Fields captured mid-loop break on every loop refactor; seam-captured
fields survive. The audit usually surfaces 1–2 debt fields on a first
pass.

**Pass criterion:** complete table; zero fields captured inside model
calls; debt items ticketed with a due week.

## Pitfalls recap

- Gold labels invented after the runs — the eval set (file 06) defines
  them; retro-labelling is grading your own homework.
- Judge scores without rubric version — trends across edits are fiction;
  version the rubric like settings.
- Gate metrics from simulated approvers treated as human data — the
  simulation validates plumbing; label it as such.
