# Comparison vs W11 — Same Cases, Final Framework Evidence

**What you'll learn:** the Agno data agent against the W11 SDK agent on
the same 15 cases — the capstone's framework evidence, with the
verification nodes as the differentiator.

## 1. The table

| Case | W11 SDK | W12/13 Agno | Notes |
|---|---|---|---|
| 1–5 corpus QA | success | success | parity |
| 6–10 analytics | 4/5 (one numeric drift) | 5/5 | verification nodes win |
| 11 mixed | 3/4 grounded | 4/4 | dual routing |
| 12 labeled sources | partial | full | source field |
| 13–14 refusals | 2/2 | 2/2 | parity |
| 15 ambiguous | flagged | flagged | parity |
| tokens p50 | 4.1k | 4.3k | +5% (verification turns) |
| latency p50 | 3.2 s | 3.5 s | +10% |

Fill from runs. The expected shape: parity on corpus QA, Agno winning
the numeric class *because of the verification nodes* — the +5% tokens
is the price of honesty, and it is the point.

## 2. What the delta means (the port discipline again)

| Delta | Honest reading |
|---|---|
| numeric 4/5 → 5/5 | verification nodes catch the drift |
| +5% tokens | one extra verify turn on numeric answers |
| corpus parity | both frameworks wrap the same tested tools |

The W11 comparison protocol (same cases, same config, 3 runs) applies —
the fourth comparison of the program, same rules.

## 3. The framework verdict, final form

```markdown
## Framework decision (final, W13)
- W11 SDK agent: the capstone's core loop (gates, strict outputs).
- Agno: the data-agent build (Knowledge wrap + toolkits) — kept for the
  analytics path where its toolkits and verification compose best.
- CrewAI: evaluated (W12-06); roles pattern ported; not the runtime.
- All three share: trajectory store, eval set, batteries, budget rules.
```

"Build on both, share everything" is the honest capstone answer: the
frameworks are *mechanisms*, the system (store, evals, policies) is
yours. The verdict memo records which mechanism each path uses and why.

## 5. The verification value drill (the table's fine print)

```text
runs with verify enabled:    5/5 numeric correct, +5% tokens
runs with verify disabled:   3/5 numeric correct (2 silent drifts)
```

The two-line drill is the comparison's most important number: the
verification node's *marginal value* — two silently-wrong numbers per
five, caught for five percent more tokens. That ratio is the argument
for the honesty layer, and it belongs in the framework memo verbatim.

## Exercises

1. Run the 15 cases through both agents; fill the table; investigate any
   parity break on cases 1–5 (corpus QA must be identical — same
   knowledge, same rules).
2. Verification-value drill: disable the verify node; rerun cases 6–10;
   count the numeric drifts — the node's value, measured.
3. Final-memo drill: write the framework decision (§3) into the boundary
   memo; cite the table and one cost number.

## 5. The comparison pin note

**Task:** extend `reports/sdk-versions.md` with the comparison header:
both agent versions, the 15-case set version, the protocol (3 runs,
majority), and the rerun command.

**Worked approach:** the four-way framework comparison arc ends here —
the pin note is its reproducibility record, the same header discipline
every comparison since W9 has carried.

**Pass criterion:** note committed; the rerun command reproduces the
table's outcome column.

## Exercises (continued)

4. Parity-failure drill: force a corpus-QA mismatch between the two
   agents (change one instruction); the parity test must catch it —
   the port's contract, proven by its violation.