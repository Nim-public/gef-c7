# Comparison Table — Same Cases, Both Implementations

**What you'll learn:** the honest comparison artifact: the 10-task eval
set run through both the W10 hand-rolled agent and the SDK port, metric
by metric — and what the deltas *mean* versus what they merely show.

## 1. The table

| Task | W10 outcome | SDK outcome | W10 steps | SDK steps | W10 tok | SDK tok |
|---|---|---|---|---|---|---|
| 1 corpus contents | success | success | 1 | 1 | 1.9k | 1.8k |
| 2 summarize page 3 | success | success | 2 | 2 | 3.1k | 3.0k |
| 3 Q3 margin chart | success | success | 3 | 3 | 5.4k | 5.2k |
| 4 follow-up margin | success | success | 2 | 2 | 2.8k | 2.9k |
| 5 error code | success | success | 2 | 2 | 2.6k | 2.5k |
| 6 whiteboard photo | success | success | 2 | 2 | 2.4k | 2.3k |
| 7 CEO bonus | refused | refused | 2 | 2 | 2.7k | 2.6k |
| 8 multi-hop compare | success | success | 5 | 4 | 9.8k | 8.9k |
| 9 injection | refused | refused | 1 | 1 | 0.9k | 0.8k |
| 10 ambiguous | success+flag | success+flag | 4 | 4 | 6.6k | 6.4k |

The expected shape: outcomes identical (the port was behavior-preserving);
SDK tokens slightly lower (its loop prompt is tighter than your hand-rolled
one). Deltas larger than ~10% need explanation, not celebration.

## 2. What each delta means

| Delta | Honest reading | Dishonest reading |
|---|---|---|
| SDK −5% tokens | framework prompt/packing efficiency | "the SDK is smarter" |
| SDK recovers 1 step on task 8 | its error handling nudges better | "rewriting fixed the agent" |
| Outcomes identical | the port preserved behavior | "nothing changed, why port?" |
| One W10 win (task 4) | your fitter trims harder | "the SDK regressed" |

The comparison's purpose is *verifying the port*, not crowning a
winner — single-task deltas are noise at n=10; the aggregate and the
outcome column are the signal.

## 3. Beyond the eval set: capability deltas

| Capability | W10 | SDK | Net |
|---|---|---|---|
| structured outputs | manual validators | `output_type` strict schema | SDK |
| guardrails as tripwires | post-hoc audit | in-run exceptions | SDK |
| handoffs/multi-agent | not built | native | SDK |
| sessions | manual | `SQLiteSession` | SDK |
| context budgeting | fitter + properties | manual (still yours) | tie |
| anti-pattern detectors | harness | harness over spans | tie |
| lines of loop code | ~50 | ~0 (framework) | SDK |

The verdict memo (file 04) reads this table: capabilities gained, tokens
neutral, the fitter still yours.

## 4. The comparison protocol (fixed before running)

```text
1. same eval set version, same corpus version, same model id
2. same temperature, same max_turns
3. 3 runs per task per implementation, majority outcomes
4. metrics from the merged store (file 05-03) only
5. deltas ≤5% = tie; 5–15% = investigate; >15% = bug hunt
```

The protocol is committed *before* the runs — comparison studies with
post-hoc metric choices are how teams fool themselves.

## Exercises

1. Produce the table from real runs (both implementations, same config);
   commit with the protocol header; compute the aggregate deltas.
2. Delta-forensics drill: pick the largest per-task delta; bisect the
   traces (W11 file 05) to the mechanism; write one paragraph.
3. Capability-table drill: extend §3 with *your* W10 components; mark
   each SDK/manual/tie; the manual rows are the standing work list.

## 5. The delta ledger (what changed and why)

| Metric | W10 | SDK | Δ | Cause |
|---|---|---|---|---|
| mean steps | 2.4 | 2.2 | −0.2 | SDK error nudges |
| mean tokens | 3.8k | 3.6k | −5% | loop prompt packing |
| guardrail fires | 2 | 2 | 0 | same audits, new layer |
| handoffs | 0 | 0 (v1) | — | topology unchanged |

The ledger extends the table with a *cause* column — a delta without a
cause is unexplained variance, and unexplained variance in a
behavior-preserving port is a bug until proven otherwise. Fill the cause
column from trace bispection, not from the changelog.

## Pitfalls

- Comparing implementations on different corpus/config versions — the
  protocol header exists to prevent it.
- n=10 conclusions about "better" — the table verifies the port;
  statistical claims need the full eval set and repeats.
- Hiding the W10-win rows — honest tables build trust in the verdict;
  the memo reads them as fitter evidence.