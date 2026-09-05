# Exercises — Agno Introduction

Expanded set with worked approaches. The deliverable: your agent ported
to Agno's four fields, served in a UI, with the framework-mapping table
completed.

## 1. The four-field port (from 01-agent-structure)

**Task:** port the W11 SDK agent to Agno: same tools (as `@tool` or a
small Toolkit), same constitution in `instructions`, same typed output
via `output_schema=Answer`; run the 10-task eval set.

**Worked approach:** the port order from W11 file 06 applies unchanged —
tools first, loop second, typing third, battery after each. The eval
outcomes must match W11's; deltas get the comparison-table treatment
(cause column or nothing).

**Pass criterion:** 10/10 outcome parity; the mapping table frozen from
the final code.

## 2. Playground run-through (from 02-playground)

**Task:** serve the agent; run 3 tasks in the UI; inspect one tool call
per run; verify the tool args/results match what your harness's traces
recorded for the same queries.

**Worked approach:** the UI-vs-harness comparison is the trust check —
the Playground is interactive; the store is authoritative; they must
agree on args and metrics for the same run.

**Pass criterion:** 3/3 runs consistent; one screenshot-equivalent note
in `reports/playground-notes.md`.

## 3. The completion table, finalized (from 03-framework-mapping)

**Task:** fill the W10/W11/W12 table with your implementation status per
cell; mark every N/A cell as Week 13+ scope or "not needed"; write the
final-build framework choice with its justification.

**Worked approach:** the table is the anti-churn device: three weeks of
ports produced three mappings — the final build picks one *mechanism*
and keeps all the *policies*. The justification cites your own numbers
(router tax, battery pass rates), never marketing.

**Pass criterion:** table complete; the framework decision written with
two cited numbers.

## 4. Migration drill (from 04-phidata-migration)

**Task:** port one legacy phiData snippet to current Agno; then migrate
your LanceDB corpus into `Knowledge` with `SearchType.hybrid`; diff the
retrieval results against your W09 stack on 5 queries.

**Worked approach:** the retrieval-parity check is the interesting one —
same engine (LanceDB), same table, same hybrid search → same hits. Any
difference is an embedder or chunking mismatch; name it.

**Pass criterion:** migrated snippet runs; 5/5 retrieval queries match
(or the embedding/chunking difference is documented).

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Four-field port, outcome parity 10/10 | eval results | 4 |
| Playground inspected, consistent with store | UI notes | 2 |
| Completion table finalized + decision | framework table | 3 |
| Migration drill with retrieval parity | migration report | 3 |
| Version pin note updated | reports/sdk-versions.md | 2 |

**Pass bar:** 11/14 to proceed to file 02 (knowledge and databases). The
port (4-pointer) is the week's foundation — same contract, new skin.

## 6. The framework cheat sheet

**Task:** write `reports/framework-cheatsheet.md`: one page, three
columns (W11 SDK / Agno / CrewAI), rows = the ten things you do every
week (define agent, add tool, typed output, session, UI, trace, eval,
budget, gate, deploy). Each cell: the exact API name.

**Worked approach:** the cheat sheet is the translation dictionary you
will use for the rest of the program — every row is a construct you have
*run*, not a doc quote. Rows you cannot fill from memory mark constructs
you never actually used (useful to know).

**Pass criterion:** 10 rows × 3 columns filled from your own code; the
sheet linked from all three framework subfolders' READMEs.

## Pitfalls recap

- Mapping tables that skip the "manual, still mine" rows — budgets, gates,
  and detectors survive every framework; write them down.
- UI-only debugging — the Playground shows runs; the harness proves
  regressions; use both.
- Blind `phi.` → `agno.` renames — the knowledge API restructured; verify
  against current docs per construct.