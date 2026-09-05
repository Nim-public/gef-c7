# Exercises — CrewAI Workflow

Expanded set with worked approaches. The deliverable: a working crew,
least-privilege roles, the process decision measured, and the
three-framework comparison finalized.

## 1. Crew construction (from 01-crewai-essentials)

**Task:** rebuild the extractor→answerer chain as a two-agent crew;
run the eval set; compare outcomes and tokens with W11's chain.

**Worked approach:** the comparison protocol (fixed corpus/config) once
more — the fourth column of the completion table. CrewAI's role slots
must carry the same constitution rules; the battery decides whether
they do.

**Pass criterion:** outcome parity on the eval set; the table's fourth
column filled from runs.

## 2. Role design tests (from 02-role-design)

**Task:** implement the capability table (role × tools × trust); write
the boundary tests (writer has no tools, analyst read-only); run the
privilege probe.

**Worked approach:** the tests are the role design — a role without a
boundary test is an adjective. The backstory-as-constraints rule gets
one battery case per constraint.

**Pass criterion:** capability table + boundary tests green; one
adjective-only backstory fixed.

## 3. Process bake-off (from 03-process-choice)

**Task:** run the 3-task pipeline in both processes; produce the
cost/latency/plan-quality table; assert plan coverage on hierarchical.

**Worked approach:** the manager tax formula gets real numbers from your
runs; the plan-coverage assertion (every task delegated exactly once) is
the hierarchical gate.

**Pass criterion:** both processes run; the tax measured; coverage
assertion green (or phantom tasks documented and fixed).

## 4. The final comparison (from 04-comparison-vs-w11)

**Task:** complete the four-way table; write the §4 framework decision
paragraph citing two of your own numbers; commit as the capstone's
framework record.

**Worked approach:** the decision is allowed to be "W11 SDK, with ported
patterns" — the citation requirement keeps it honest. The ported-ideas
list (Knowledge wrap, role slots) names *where* each idea lives now.

**Pass criterion:** decision paragraph in the boundary memo; the
completion table's every cell filled.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Crew runs the eval set | fourth column | 3 |
| Role boundary tests green | capability tests | 3 |
| Process bake-off with plan coverage | bake-off report | 4 |
| Framework decision, numbers cited | boundary memo | 4 |
| CrewAI role slots carry constitution constraints | battery cases | 2 |

**Pass bar:** 13/16 to close Week 12. The bake-off (4-pointer) is the
process decision's evidence — hierarchical without measurement is a
token tax.

## 6. The framework-week closing note

**Task:** append to `doc/capstone/retrospective.md`: the framework
decision and its two cited numbers, the ported-ideas ledger (from file
04's §5), and one sentence per framework on what you would use it for
next time.

**Worked approach:** the closing note is the three-week framework arc
(W10 hand-rolled → W11 SDK → W12 Agno/CrewAI) compressed into three
citations — the arc's value was the mapping tables, and the note says so
with links.

**Pass criterion:** three entries with artifact citations; the decision
sentence matches the boundary memo's framework record.

## 7. The CrewAI pin note

**Task:** extend `reports/sdk-versions.md` with the CrewAI stack:
version, process chosen, crew composition, and the bake-off command from
exercise 3.

**Worked approach:** CrewAI is the third framework in three weeks — the
pin note records it as *evaluated*, with its bake-off numbers, so the
completion table's fourth column stays reproducible after any upgrade.

**Pass criterion:** note committed; the bake-off command reproduces the
table's fourth column.

## Pitfalls recap

- Roles split by seniority adjectives — capability and privilege are the
  split; test the tools.
- Hierarchical plans unasserted — phantom tasks are silent missing
  deliverables.
- Framework decisions from tutorials instead of your tables — the
  completion table is the decision's evidence.