# The Verdict — Lines Saved vs Capabilities Gained

**What you'll learn:** the week's closing memo: what the port cost, what
it bought, what remains manual, and the standing decision for Weeks
12–16 — written so a reviewer can audit it in five minutes.

## 1. The memo template

```markdown
# SDK port verdict — 2026-09-05

## Cost
- Port effort: 7 components, ~6 h, battery-green at each step
- Deleted: hand-rolled loop (~50 lines), registry transport (~40)
- Added: SDK dependency (pinned), trace-merge layer (~60 lines)
- Net code: −30 lines, +1 dependency

## Gained
- structured outputs (strict schema), guardrail tripwires, handoffs,
  sessions, built-in tracing, streaming — all battery-tested post-port

## Still manual (by design)
- context budgeting (fitter + property tests)
- gate policy (HITL triage table)
- anti-pattern detectors, trajectory store, metric dictionary

## Decision
- Weeks 12–16 build on the SDK agent; the W10 loop is deleted.
- Revisit triggers: trace-export breakage on SDK bump (pin + fixture),
  context-budget needs beyond the fitter, vendor lock-in pressure.
```

## 2. Reading the ledger honestly

| Line item | The trap it avoids |
|---|---|
| "Net code −30" | frameworks move code, they don't delete responsibility — the still-manual rows say so |
| "Gained, all battery-tested" | capabilities claimed without tests are marketing |
| "Revisit triggers" | lock-in is a risk you *schedule*, not ignore |

The memo's honesty test: could a teammate re-implement your agent from
it? If the still-manual rows are vague ("some context stuff"), the port
wasn't understood — only performed.

## 3. What Weeks 12–16 inherit

| Consumer | Inherits |
|---|---|
| W12 (evaluation week) | the SDK agent as the system under test |
| W13 (multimodal agents) | typed outputs + guardrails as composition seams |
| W14–15 (workflow/demo) | the boundary memo + harness as the product spine |
| Capstone reviewers | the verdict memo + baseline gate |

The port's purpose was never the SDK — it was putting your agent on a
maintained substrate before the capstone's final weeks made changes
expensive.

## 4. The standing risks, named

| Risk | Mitigation in place |
|---|---|
| SDK breaking changes | pinned version + span-shape fixture test |
| vendor coupling (strict schema, tracing key) | tool logic stays in plain functions; swap-out memo |
| framework feature gravity ("let's use their memory") | the still-manual list is policy; additions re-enter through the battery |

## 5. The verdict's review — five minutes, by a skeptic

The memo is written for a skeptical reviewer. The five-minute audit:

```text
1. Costs cite git numbers?           (git log --stat, not estimates)
2. Gains cite tests?                 (battery rows, not feature lists)
3. Still-manual rows name owners?    (files + property tests)
4. Triggers have weeks/metrics?      (W12+ calendar)
5. Deletion drill in the log?        (no parallel path remains)
```

Any "no" is a memo gap, not a reviewer failure — the memo is the
decision record *because* it survives this audit.

## Exercises

1. Write the verdict memo from your port's actual numbers (hours from
   your log, lines from `git log --stat`); no estimated figures.
2. Audit drill: hand the memo to a teammate; they must name your
   still-manual components from it alone — the five-minute audit.
3. Trigger rehearsal: simulate one revisit trigger (SDK minor bump);
   verify the pinned-version fixture catches it and names the fix.
4. Counterfactual drill: write the one-paragraph case for *staying*
   hand-rolled; if you cannot argue it, your memo's cost column is weak —
   strengthen it.

## Pitfalls

- Verdicts written from vibes ("it feels cleaner") — the cost table has
  real numbers or the memo is a mood.
- Deleting the W10 tests with the W10 loop — the tests are the contract
  that made the port verifiable; they outlive both implementations.
- Revisit triggers without owners or weeks — a trigger nobody owns is
  a wish; tie each to a week or a metric.

## Resources

- [`../05-observability-eval-agents/04-regression-suites.md`](../05-observability-eval-agents/04-regression-suites.md)
  — the gates that make the verdict durable.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/04-metrics-table.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/04-metrics-table.md)
  — the baseline the verdict is measured against.