# Exercises — Practice: Agents SDK Capstone

Stretch tasks and the self-review rubric. The deliverable: the completed
port, the comparison evidence, the debugged-and-tested failure, and the
verdict memo.

## 1. Port discipline audit (stretch)

**Task:** reconstruct the port's commit history into the §1 gate table
(component → battery gate → green/red sequence); verify *every* step had
its gate run before the next commit.

**Worked approach:** `git log --oneline` of the port should read as the
gate table — if any commit skipped its gate, the port's discipline claim
is weakened (and the missing gate's failure mode is worth finding).

**Pass criterion:** gate table matches the commit history 1:1; any gap
documented honestly.

## 2. Comparison under repetition (stretch)

**Task:** rerun the comparison table with 3 repeats per task per
implementation; report aggregate deltas with ranges; confirm or revise
the §2 readings.

**Worked approach:** single-run deltas invite over-reading; the ranges
separate signal from sampling noise. Expect the outcome column to stay
identical (the port was behavior-preserving) and token deltas to
stabilize within ±5%.

**Pass criterion:** ranges reported; no reading reversed; the protocol
header updated with the repeat count.

## 3. Trace-debugging speedrun (stretch)

**Task:** plant a *different* failure class (budget death on task 8 via
`max_turns=2`); run the workflow; target <45 minutes from symptom to
merged post-mortem.

**Worked approach:** the second drill tests the workflow, not you — the
signature table (file 05-02) should route straight to the budget layer;
the handler + `include_in_history=False` semantics are the fix.

**Pass criterion:** post-mortem merged under 45 min; the added test is
the turn-limit fallback case.

## 4. The Week 12 readiness review (stretch)

**Task:** assemble the artifact set Week 12's evaluation week will
consume: verdict memo, baseline JSON, harness command, eval set v2, and
the open-questions list — one page of links.

**Worked approach:** the readiness review is the handoff pattern
(W10-06 exercises) applied across a week boundary — links to committed
artifacts only; anything not committed is not ready.

**Pass criterion:** the page exists; a teammate can run the harness from
it without asking questions.

## 5. Self-review rubric (grade before the week ends)

| Criterion | Evidence | Points |
|---|---|---|
| Port completed, battery-green per step | gate table + git log | 4 |
| Comparison table with protocol header | reports/comparison.md | 3 |
| Planted failure debugged + regression test | reports/post-mortem.md | 4 |
| Verdict memo: costs, gains, still-manual, triggers | verdict memo | 4 |
| Deletion drill (W10 loop removed, suite green) | git + CI | 2 |

**Pass bar:** 14/17 to close Week 11. The verdict memo (4-pointer) is
the capstone's decision record — Weeks 12–16 cite it.

## 6. The Week 12 integration rehearsal

**Task:** dry-run Week 12's entry condition: from the readiness page
(exercise 4 of file 05), a teammate runs the harness, reads the baseline,
and names the two open questions — in under 10 minutes, without asking
you anything.

**Worked approach:** the rehearsal is the handoff's acceptance test — if
the teammate stalls on any step, the missing artifact is a Week 12
blocker discovered a week early.

**Pass criterion:** teammate completes the run + read + questions in
<10 min; every stall point fixed on the spot.

## 7. The closing retrospective entry

**Task:** append to `doc/capstone/retrospective.md`: what the port
changed about your plan (capability bets, manual-policy list, boundary
updates), each citing an artifact from this week.

**Worked approach:** the retrospective entries are the compounding record
— three citations (verdict memo, comparison ledger, handoff page) with
one-line consequences each.

**Pass criterion:** three entries, each with an artifact citation and a
plan consequence.

## Pitfalls recap

- Port steps committed without their gates — the discipline claim dies in
  the commit history; run the gate, then commit.
- Comparison conclusions from n=1 runs — repeats or silence.
- Verdict memos without revisit triggers — lock-in without a schedule is
  just lock-in.