# The Metrics Table — The Harness Output

**What you'll learn:** the week's single artifact: one command producing
the full metrics table — scorecard dimensions, eval-set results, battery
status, judge flags — committed as the agent's baseline.

## 1. The table, as produced by one command

```bash
py scripts/agent_metrics.py --out reports/agent-metrics.md
```

```text
# Agent metrics — eval-set v1 — 2026-09-05 — model: pinned-id — config: AGENT_CONFIG v1

## Scorecard (n=10, 3 runs/task, majority)
| # | task (short)        | success | steps | tokens | tools ok | outcome |
|---|---------------------|---------|-------|--------|----------|---------|
| 1 | corpus contents     | ✓ 3/3   | 1.0   | 1.9k   | ✓        | success |
| 2 | summarize page 3    | ✓ 3/3   | 2.0   | 3.4k   | ✓        | success |
| 3 | Q3 margin chart     | ✓ 2/3   | 3.3   | 5.8k   | ✓        | success |
| 7 | CEO 2019 bonus      | ✓ 3/3   | 2.0   | 2.8k   | ✓        | refused |
| 9 | prompt injection    | ✓ 3/3   | 1.0   | 0.9k   | ✓        | refused |

## Process
loop rate 0.00 | error recovery 100% | degraded 0/30 | dead tools: none

## Judge (rubric v1, calibrated ±1)
mean total 6.8/8 | flagged (<5): 1 run → hand-checked

## Batteries
Tier 1: 24/24 | Tier 2 (nightly): 9/10 tasks at 3/3
```

Every cell derives from the trajectory store (file 04) or the batteries
(file 03) — the table is *assembly*, which is what makes it trustworthy.

## 2. The header rules (unchanged, now load-bearing)

```python
AGENT_HEADER = {
    "eval_set": "v1", "constitution": "cv1", "hints": "hv3",
    "model": "pinned-id", "date": "2026-09-05", "runs_per_task": 3,
    "machine": "6-core CPU, 32GB",
}
```

Header fields map one-to-one to versioned variables: eval set, rubric,
constitution, hints, model. Any change without a bump makes trend lines
meaningless — the table's comparability *is* the header's job.

## 3. Reading the table — the weekly loop

| Signal | Reading | Action owner |
|---|---|---|
| success <0.8 on a class | route or description gap | file 02 descriptions |
| steps p50 > budget/2 | fitter or task shape | file 05 fitter |
| any Tier-2 task flips | model drift | sensitivity note (file 03) |
| judge flags ≥2 runs | rubric or real failure | hand-check queue (file 04) |

The reading is two sentences in the report footer — the numbers exist to
name one next action, not to decorate.

## 4. The baseline gate

```python
BASELINE = {"success_rate": 0.80, "mean_judge": 6.5, "loop_rate": 0.05}

def gate(current: dict, baseline: dict) -> int:
    ok = (current["success_rate"] >= baseline["success_rate"] - 0.05
          and current["mean_judge"] >= baseline["mean_judge"] - 0.5
          and current["loop_rate"] <= baseline["loop_rate"] + 0.03)
    return 0 if ok else 1
```

The gate converts this week's table from a report into a safety net:
Week 11's changes (multi-agent, new tools) run against it, and regressions
fail CI with a readable diff — the same discipline as the retrieval
baseline from Week 07.

## Exercises

1. Produce the table from your 30 runs (10 tasks × 3); verify every cell
   traces to the store; commit as the v1 baseline.
2. Mutation drill: degrade one tool description; rerun; confirm the table
   (and gate) catch it; restore.
3. Trend drill: run the table on two different days; diff — any cell that
   moves without a config change is a finding (drift, caching, or
   flakiness); name it.

## Pitfalls

- Tables assembled by hand from scattered logs — one command or it will
  not survive Week 11.
- Baselines updated to quiet a red gate — baselines move only via
  accepted eval runs, the rule since Week 07.
- Metrics without the header — the table is unreproducible and the
  rubric (and your future self) will say so.

## Resources

- [`../04-measuring-agents-patterns/`](../04-measuring-agents-patterns/)
  — the store and scorecard this table renders.
- [`../03-mcp-servers-fastmcp/03-client-batteries.md`](../03-mcp-servers-fastmcp/03-client-batteries.md)
  — the battery rows at the table's foot.
