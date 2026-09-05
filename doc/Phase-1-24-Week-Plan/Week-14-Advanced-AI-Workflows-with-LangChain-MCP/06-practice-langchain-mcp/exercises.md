# Exercises — LangChain + MCP Capstone

Stretch tasks and the self-review rubric. The deliverable: the five-
framework verdict, the merged architecture record, the four-pillar demo,
and the complete gate integration.

## 1. The five-framework table (stretch)

**Task:** fill every parity cell from runs; the not-compared cells
listed with their cost to compare; the decision paragraph re-affirmed or
revised.

**Worked approach:** the fifth column (LangChain) comes from this
week's parity test; the others from their weeks. The not-compared list
is scoping honesty, not failure.

**Pass criterion:** the table committed; every cell cites a run or is
explicitly not-compared.

## 2. The architecture record (stretch)

**Task:** merge the four memos into `doc/capstone/architecture.md`;
re-measure the budgets; verify every trigger is executable from the
memo alone.

**Worked approach:** the merge is editorial (the numbers exist) — the
value is one page where the capstone's architecture is auditable end to
end.

**Pass criterion:** the record committed; the trigger simulation passes
for at least one trigger.

## 3. The four-pillar demo (stretch)

**Task:** run the demo fresh-clone; the degradation drill per pillar;
the latency table printed; the artifacts (charts, transcripts, audit
rows) committed.

**Worked approach:** the demo is the program's face — its evidence
lands in `reports/demo/` and the degradation drill is *part* of the
show, not an appendix.

**Pass criterion:** fresh-clone run green; degradation drills visible;
the latency table within budgets.

## 4. The gate inventory, mutation-proven (stretch)

**Task:** run the full mutation map (one planted bug per gate); every
gate trips; restore; every gate green; the map committed with dates.

**Worked approach:** the mutation map is the CI's characterization test
— it proves the safety net exists, not just that it is documented.

**Pass criterion:** the map committed; every gate proven; quarterly
re-run scheduled.

## 5. Self-review rubric (the program's capstone-week rubric)

| Criterion | Evidence | Points |
|---|---|---|
| Five-framework table from runs | framework table | 4 |
| Architecture record merged, triggers executable | architecture.md | 4 |
| Four-pillar demo, degradation drills | demo + reports | 4 |
| Gate inventory in CI, mutation-proven | gates.yml + map | 4 |
| Acceptance command fresh-clone green | accept.py run | 2 |

**Pass bar:** 15/18 to close Week 14. The mutation map (4-pointer) is
the integration's proof — the gates exist because they catch planted
bugs, on demand.

## 6. The capstone integration review

**Task:** write `reports/capstone-integration.md`: the five-framework
verdict, the architecture record, the four-pillar demo results, and the
gate inventory — one page, the program's integration summary.

**Worked approach:** the review composes the capstone-week's four files
into one evidence sheet: every framework decision cites its comparison,
every budget cites its ledger, every gate cites its mutation.

**Pass criterion:** the page answers "what did you build, how is it
architected, and how do you know it still works?" in one read.

## 7. The Week 15 handoff

**Task:** write `doc/capstone/week15-handoff.md`: the integration state,
the acceptance command, the open questions, and the extension weeks'
plan (E1–E10 on their branches) — the handoff pattern, fourth use.

**Worked approach:** the handoff is generated where possible (gate
statuses, baselines) and lists the extension-week plan with the branch
names — the next sessions resume from it.

**Pass criterion:** a teammate runs the acceptance command and reads the
handoff in under 15 minutes total.

## Pitfalls recap

- Parity cells guessed instead of run — the table's value is its
  evidence.
- Demos without degradation drills — happy-path demos are fragile
  demos.
- Gates documented but not wired — the CI config is the inventory or
  the inventory is fiction.