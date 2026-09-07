# Exercises — Structured Data Retrieval Capstone

Expanded set with worked approaches. The deliverable: the extended
schema, the gold-SQL eval, the deployed router, and the safety battery —
the week integrated and graded.

## 1. Schema + edge-case corpus (from 01-schema-ingestion)

**Task:** extend the schema; generate the edge-case corpus; prove the
rebuild determinism; the PII drill on serialized notes.

**Worked approach:** the edge cases are designed to trigger named
failure modes (the LEFT JOIN count trap, the outlier stability, the
masking layer). The rebuild determinism is the W10 discipline applied
to the warehouse.

**Pass criterion:** edge-case families present; rebuild deterministic;
the PII masking fires on serialized notes.

## 2. The gold-SQL eval (from 02-text2sql-eval)

**Task:** write gold SQL + result sets for the 8 ladder queries; run
the Text2SQL agent; the per-band accuracy report; the scorer drill
(alternative SQL accepted).

**Worked approach:** the result-set scorer accepts any formulation
producing the gold rows — the drill proves it by writing an alternative
JOIN order for Q5.

**Pass criterion:** 8 golds verified; the per-band report committed;
the alternative-SQL drill green.

## 3. The deployed router (from 03-router-implementation)

**Task:** deploy `TabularRouter`; run 25 queries; the per-rung accuracy
table; the miss-analysis drill (fix the modal miss type).

**Worked approach:** the logged decisions feed the miss analysis — the
router's misses are classified (rules/classifier/shape) and the modal
type fixed with a remeasure.

**Pass criterion:** the per-rung table committed; the modal miss fixed
with before/after numbers.

## 4. The safety battery (from 04-safety-battery)

**Task:** run the eight-probe battery; the independence drill
(validator disabled, ro-mode still blocks); the nightly model-behavior
edition.

**Worked approach:** the battery's two editions — tool tests (pure,
fast, push CI) and model-behavior tests (does the model generate
blocked shapes? nightly). Both committed.

**Pass criterion:** 8/8 probes contained at their named layers; the
nightly model edition run once and recorded.

## 5. Self-review rubric (the weekly capstone's rubric)

| Criterion | Evidence | Points |
|---|---|---|
| Extended schema + edge-case corpus | DDL + generator | 4 |
| Gold-SQL eval: per-band accuracy | gold set + report | 4 |
| Router: per-rung accuracy + miss analysis | router report | 4 |
| Safety battery: 8 probes + independence | battery tests | 4 |
| Pin note (capstone task stack) | pin note | 2 |

**Pass bar:** 16/18 to close Week 06. The safety battery (4-pointer) is
the capstone task's non-negotiable — a tabular agent that can write is
a failed capstone.

## 6. The capstone-task pin note (the week's manifest)

**Task:** consolidate the capstone-task stack in `reports/sdk-versions.md`:
the extended schema, the gold-SQL eval, the deployed router, and the
safety battery — one block.

**Worked approach:** the capstone-task manifest follows the pin
discipline: the schema, the gold set, the router, and the battery —
each citing its drill.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## 7. The structured-retrieval walkthrough (the reviewer's page)

**Task:** write `reports/structured-walkthrough.md`: one query per route
(SQL, paste, hybrid) walked end-to-end — the query, the route decision,
the artifact, and the grounded answer. The page demonstrates the whole
week's architecture.

**Worked approach:** the walkthrough is the routing tree (file 04-01)
in motion — one query per route with the artifacts shown. The reviewer
sees the decision tree *working*.

**Pass criterion:** three walked routes; every artifact cited; the
grounding audit green on each.

## 8. The pitfalls recap (the week's failure catalog)

- Edge cases omitted from the corpus — the count trap and outliers go
  untested; design the families in.
- Gold SQL string-matched — result sets are the gold; string matching
  punishes valid alternatives.
- The battery testing only the tool — the model-behavior edition asks
  whether the *model* attempts the attacks.
- Rebuild without determinism — an unseeded generator makes every eval
  run incomparable.
- Escalations without evidence — the exhausted repair carries the
  attempted SQL and the schema excerpt.