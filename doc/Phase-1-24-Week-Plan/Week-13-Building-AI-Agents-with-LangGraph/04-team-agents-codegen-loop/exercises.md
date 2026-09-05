# Exercises — Team Agents & Codegen Loop

Expanded set with worked approaches. The deliverable: the bounded
self-repair graph in a tested sandbox, the supervisor topology, and the
team-vs-single verdict.

## 1. The repair graph (from 01-self-repair-graph)

**Task:** build the four-node cycle; run 5 codegen tasks; produce the
attempts-to-green histogram; verify the debug node breaks repetition
within 2 attempts.

**Worked approach:** the histogram is the loop's report card — a spike
at 4 (the bound) means the repair notes aren't directing; the phrasing
rules (W10 file 05-04) apply to repair notes verbatim.

**Pass criterion:** median attempts ≤2; no task hits the bound twice;
repair-note A/B table committed.

## 2. The sandbox (from 02-sandbox-discipline)

**Task:** build the subprocess sandbox; run the four escape probes;
document which hold; upgrade to the container for the ones that don't;
rerun.

**Worked approach:** the probe results *are* the decision — subprocess
walls hold for filesystem+env, fail for network+kernel; the container
closes those. The overhead measurement prices the upgrade.

**Pass criterion:** 4/4 probes contained post-upgrade; overhead measured
and accepted into the budget.

## 3. The supervisor (from 03-supervisor-topology)

**Task:** build the three-worker supervisor with the rule-based router;
run a research→analyze→write task; verify the turn sequence; then the
LLM-supervisor swap drill.

**Worked approach:** the rule version is the baseline — deterministic,
cheap, testable. The LLM swap measures what flexibility *costs* (tokens,
determinism) on tasks whose plans you already know.

**Pass criterion:** turn sequences correct; the LLM swap's delta
quantified; the promotion decision written with it.

## 4. The A/B verdict (from 04-team-vs-single)

**Task:** run the full protocol (10 codegen + 5 analysis, 3 runs each,
both architectures); produce the class-level table; write the per-class
verdict with the crossover rule.

**Worked approach:** the crossover rule is the deliverable — "≥3
distinct stages → team" (or whatever your numbers say). The verdict
feeds the boundary memo's agent-architecture section.

**Pass criterion:** the table with ranges; the crossover rule stated;
the memo updated.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Repair graph + attempts histogram | graph + report | 4 |
| Sandbox escape probes contained | drill results | 4 |
| Supervisor turn sequences verified | trace checks | 3 |
| Team-vs-single class verdict | A/B table | 4 |
| Bounded degradation under pressure | bound drill | 2 |

**Pass bar:** 14/17 to proceed to file 05 (the capstone task). The
sandbox (4-pointer) is non-negotiable — generated code without walls is
the one failure this program does not ship.

## 6. The codegen safety review

**Task:** write `reports/codegen-review.md`: the repair graph diagram,
the sandbox decision table, the escape-probe results, and the attempts
histogram — the codegen loop's safety and effectiveness evidence.

**Worked approach:** the review composes files 01–02 into one sheet: the
loop's learning curve (attempts histogram) next to its containment proof
(escape probes). A codegen feature ships only when both are green.

**Pass criterion:** the review answers "what happens when the generated
code misbehaves?" in one read, citing the probes.

## Pitfalls recap

- Test suites that assert only execution — the repair loop optimizes
  for garbage that runs; real assertions are the loop's fuel.
- Escape probes skipped "because it's my own code" — the drill is in CI;
  walls are tested or they are walls in name only.
- Global A/B verdicts — the class split and the crossover rule are the
  verdict; aggregates hide the boundary.