# Exercises — Practice: Your First MCP Agent

Stretch tasks and the self-review rubric. The deliverable: the assembled
agent, 10-task eval green with gold labels, red-team battery wired, and
the committed metrics baseline.

## 1. Assembly certification (stretch)

**Task:** the assembly test suite: smoke test (canned + real), bridge
fidelity, config-stamp presence on every trajectory, and the
impossible-config assert.

**Worked approach:** the suite is the assembly diagram as code — one test
per box's interface. The config-stamp assert (every row carries
`AGENT_CONFIG` versions) is what makes every later A/B attributable.

**Pass criterion:** suite green on both LLM modes; stamps present on 100%
of rows.

## 2. Eval-set hardening (stretch)

**Task:** add 5 tasks to the set (one per routing class + one new
impossible + one multi-hop requiring `history_page`); gold-label all;
re-run the metrics table.

**Worked approach:** new tasks enter via the procedure gate (stumped
twice, new tool, new red-team case) — not by inspiration. Each new row
gets its expected-tools set written *before* the first run.

**Pass criterion:** 15-row table, gold verified by eye, version bumped to
v2.

## 3. Red-team depth proof (stretch)

**Task:** the dependency-map drill from file 03, executed: disable each
defense, record which rows catch it, restore. Produce the defense→row
dependency map.

**Worked approach:** the map is the security architecture's evidence —
three architectural layers should each be caught by 2+ rows; the
model-dependent layer by 0–1 (that is why it is layered under
architecture).

**Pass criterion:** dependency map committed; no defense is single-point
of failure for all rows.

## 4. Baseline gate wired (stretch)

**Task:** wire `agent_metrics.py` + the baseline gate into CI; verify
with the mutation drill (degraded description → red; restore → green).

**Worked approach:** thresholds come from the v1 table ±tolerances
(success −0.05, judge −0.5, loop +0.03) — set from *your* baseline, not
borrowed numbers.

**Pass criterion:** gate green on restore; red on both mutations
(descriptions and loop-rate injection).

## 5. Self-review rubric (grade before the week ends)

| Criterion | Evidence | Points |
|---|---|---|
| Agent assembled; smoke green both modes | assembly tests | 4 |
| Eval set v1: 10 tasks, gold verified, routes strict | eval table + runs | 4 |
| Red-team battery: 3 fixtures + hash interlock | Tier 1 CI | 4 |
| Metrics table + baseline gate in CI | reports/agent-metrics.md | 4 |
| Boundary memo + tool surface v1 linked | capstone docs | 2 |

**Pass bar:** 14/18 to close Week 10. The metrics table (4-pointer) is
the week's face — every later agent week reads its trend lines.

## Pitfalls recap

- Eval sets that avoid the agent's weak spots — tasks 7 and 9 exist
  because honesty is the product.
- Hash interlock skipped "just this once" — the corpus is the capstone;
  guard it absolutely.
- Rubric self-review from vibes — every row cites a committed artifact,
  or it does not count.
