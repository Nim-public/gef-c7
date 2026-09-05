# Exercises — Knowledge & Databases

Expanded set with worked approaches. The deliverable: your corpus in
Agno `Knowledge` with parity proven, the grounding battery green, and
the dual pipeline routing correctly.

## 1. Knowledge wrap + parity (from 01-knowledge-lancedb)

**Task:** wrap your W09 units table in `Knowledge` (hybrid + your
embedder); run the 5-query parity loop against your W09 search function;
document hit-order deltas.

**Worked approach:** the parity loop is the acceptance gate for the whole
wrap — same engine, same table, same queries. Deltas mean embedder or
chunking drift; name them or fix them, never accept silently.

**Pass criterion:** 5/5 golden queries match (or deltas explained);
embedder id pinned in `reports/sdk-versions.md`.

## 2. Ingestion with round-tripping (from 02-ingestion-by-source)

**Task:** ingest via the manifest loop with metadata; verify `unit_id`
survives to citations; run the idempotency proof (twice = no change).

**Worked approach:** metadata round-trip is the citation life-line —
a search hit whose metadata lost `unit_id` produces uncitable answers.
The idempotency proof is the W9-04 discipline, one command.

**Pass criterion:** citations carry real `unit_id`s; double-ingest adds
zero rows.

## 3. Insufficiency battery (from 03-grounding-rules)

**Task:** write the grounding constitution; run the 5-case insufficiency
battery at 3 runs each; produce the rule→case→result table; bump the
constitution version.

**Worked approach:** the skip-detection instrumentation (search-call
count per run) is the battery's new instrument — it measures *routing*,
not just answers. The near-miss cases (partial + gap) are the graded
hard ones.

**Pass criterion:** 5 cases × 3 runs; skip counts as expected; table
committed with `cvN` stamp.

## 4. Dual-pipeline routing (from 04-dual-pipeline)

**Task:** build the dual-pipeline agent; run the route battery (5 query
classes); report route accuracy; compare with the W9 regex router's
accuracy on the same queries.

**Worked approach:** the comparison is model-routing vs regex-routing on
identical queries — the W9 router was your baseline; the model should
match it on clear classes and beat it on ambiguous ones. Misses get the
hint-A/B treatment.

**Pass criterion:** route table committed; accuracy ≥ W9 router's; SQL
guardrails verified (zero side effects).

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Knowledge parity 5/5 golden queries | parity report | 4 |
| Ingestion idempotent, metadata round-trips | ingest test | 3 |
| Insufficiency battery green (5 cases × 3) | battery table | 4 |
| Dual-pipeline route accuracy ≥ W9 router | route table | 3 |
| SQL guardrails drilled (4 patterns) | guardrail tests | 2 |

**Pass bar:** 12/15 to proceed to file 03 (custom tools). The battery
(4-pointer) is the grounding deliverable — the skip case is new, and it
is the one that ships wrong.

## Pitfalls recap

- Embedder drift between stacks — parity loop catches it in one run;
  pin the id.
- Batteries without the skip case — agentic RAG's new failure is not
  retrieving; test the skip.
- SQL guards in instructions only — the tool validates; the model is
  untrusted.