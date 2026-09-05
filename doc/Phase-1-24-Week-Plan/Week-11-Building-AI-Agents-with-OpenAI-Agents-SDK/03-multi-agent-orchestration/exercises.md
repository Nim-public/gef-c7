# Exercises — Multi-Agent Orchestration

Expanded set with worked approaches. The deliverable: one topology
implemented (handoff router, chain, or delegation — justified by your
boundary memo), anti-pattern detectors green, state-passing audited.

## 1. Topology implementation (from 01–03)

**Task:** implement the topology your boundary memo implies (for most
capstones: handoff router + chaining for the hot path); run the 10-task
eval set through it.

**Worked approach:** the memo's percentages decide — 80% single-hop stays
a chain; the multi-hop tasks exercise handoffs. Mixing both is expected;
mixing them *unjustified* is the anti-pattern.

**Pass criterion:** eval set green; the topology matches the memo's
prediction; deviations documented.

## 2. The router tax, measured (from 01-handoff-pattern)

**Task:** for each task, compute direct-path vs handoff-path cost
(tokens); report the aggregate tax with your p_specialist.

**Worked approach:** the tax formula's inputs come from the trace spans
— triage turn tokens vs direct answer tokens. If the tax exceeds 30% on
your dominant class, the class should be a chain (the memo again).

**Pass criterion:** the tax table committed; one routing decision
revisited or confirmed by it.

## 3. Delegation budget inheritance (from 03-delegation)

**Task:** if you use agents-as-tools: set inner `max_turns=3`; force an
inner loop; verify the wrapper degrades honestly and the manager reports
it (not silently retries).

**Worked approach:** the degraded-inner-answer must carry a flag the
manager can relay — the typed `Answer.degraded` field is the channel.
Silent retry inside a nested span is the failure mode this exercise
exists to kill.

**Pass criterion:** inner budget fires; outer answer reports degradation;
trace shows the nested stop.

## 4. State-passing audit (from 04-state-passing)

**Task:** for every boundary in your topology, fill the crossing table
(what crosses, channel, rule compliance); run the summary-fidelity drill
(ids/numbers survive).

**Worked approach:** the audit is five minutes of honesty per boundary —
the checklist in §4 is the rubric. The fidelity drill reuses the fitter's
P3/P4 properties on handoff summaries.

**Pass criterion:** boundaries documented; fidelity drill green; any
context grab-bag item ticketed.

## 5. Anti-pattern sweep (from 05-anti-patterns)

**Task:** run the three detectors over all stored trajectories; produce
the health table (ping-pong rate, spiral rate, bloat trend); fix the
worst offender's root cause.

**Worked approach:** detectors are ten lines each and run in the harness
forever — the sweep is their first employment. The fix order follows the
catalog: stay-zones, loop-breaker, boundary statements.

**Pass criterion:** health table committed; zero undetected instances
after fixes; detectors in CI.

## 6. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Topology matches boundary memo | implementation + memo | 3 |
| Router tax measured per class | tax table | 3 |
| Inner budgets inherited + honest degradation | delegation drill | 3 |
| State-passing boundaries documented | audit table | 3 |
| Anti-pattern detectors in harness | health table + CI | 4 |

**Pass bar:** 13/16 to proceed to file 04 (voice agents). The detector
suite (4-pointer) is the topology's insurance — it runs on every
trajectory from now on.

## 7. The topology one-pager

**Task:** write `reports/topology.md`: your implemented topology as a
diagram (router/specialists/chain stages), each agent's one-line job
boundary, tool lists, and the measured router tax — the architecture
page the capstone reviewers read.

**Worked approach:** every claim in the diagram cites a number from
exercises 2–5; the one-line boundaries are the bloat antidote (file 05)
in documentation form.

**Pass criterion:** the page passes the reviewer test — topology,
boundaries, and costs in one read, no vibes.

## Pitfalls recap

- Topologies chosen by novelty rather than the class distribution — the
  memo is the spec; novelty is a hypothesis for one task, not an
  architecture.
- Nested spans uncounted — delegation's cost is invisible to naive
  counters; read the spans.
- Anti-pattern detectors written but not run in CI — the sweep is a
  snapshot; the harness makes it a trend.
