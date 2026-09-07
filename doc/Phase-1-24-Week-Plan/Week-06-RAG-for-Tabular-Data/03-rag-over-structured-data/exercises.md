# Exercises — RAG over Structured Data

Expanded set with worked approaches. The deliverable: the generated
schema prompt, the four-layer validator, the repair loop measured, and
the grounded answer format audited.

## 1. The schema prompt (from 01-schema-prompts)

**Task:** generate the prompt from `sqlite_master`; diff against the
hand-written version; run the date-grounding drill (three phrasings →
one BETWEEN).

**Worked approach:** the generated prompt is the anti-drift version —
diffing shows what the hand-written one missed (usually a new column).
The date drill covers "June", "Q3", and "last 30 days".

**Pass criterion:** the generated prompt adopted; 3/3 date phrasings
resolve identically.

## 2. The validation stack (from 02-validation-layers)

**Task:** implement the four layers; run the trick battery (multi-
statement, comment-hiding, LIMIT-swallowing); the independence drill
(disable layer 1; layers 2–3 still hold).

**Worked approach:** the trick battery is the parser's proof — regexes
alone miss the comment tricks, so the structural parse is required.
The independence drill is the depth property.

**Pass criterion:** 6/6 tricks caught; the independence drill green;
the row-cap message honest.

## 3. The repair loop (from 03-repair-loops)

**Task:** implement the loop with the error→hint mapping; run the
8-query ladder; produce the attempts histogram; the exhaustion drill.

**Worked approach:** the histogram is the loop's report card — first-
pass rate >70% is healthy, and the hints drive attempt-2 recoveries.
The exhaustion drill is the honesty test.

**Pass criterion:** first-pass >70%; exhaustion <5%; the hint mapping
validated per error class.

## 4. Result formatting (from 04-result-formatting)

**Task:** implement `format_result`; run it on the ladder outputs; the
empty drill; the synthesis audit (every prose number paired to rows).

**Worked approach:** the pairing audit (W14 file 02-04) extends to SQL
results — every number in the prose traces to the shown rows or the
audit line. The empty case is the honesty path.

**Pass criterion:** 8/8 answers carry audit lines; the empty case
honest; the pairing audit green.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Generated schema prompt adopted | diff + prompt | 3 |
| Validator: 6/6 tricks + independence | layer tests | 4 |
| Repair loop: histogram + hints validated | metrics + mapping | 4 |
| Formatting: audit lines + empty honesty | format tests | 4 |
| Pin note (Text2SQL stack) | pin note | 2 |

**Pass bar:** 15/18 to proceed to file 04 (the hybrid bridge). The
validator (4-pointer) is the pipeline's safety — the layers are
independent by the drill's proof.

## 7. The Text2SQL failure-mode walkthrough (the reviewer's page)

**Task:** write `reports/text2sql-walkthrough.md`: one query per
failure class (dialect error, wrong join, HAVING misuse, hallucinated
number) walked end-to-end — the bad SQL, the error, the repair, the
final grounded answer.

**Worked approach:** the walkthrough is the pipeline's documentation
-by-example — each failure class from §1's diagnosis tree shown with
its repair. The reviewer sees the loop *working*.

**Pass criterion:** four walked failure classes; every repair shown
with the before/after SQL; the page cites the repair metrics.

## 7. The Text2SQL pin note (the pipeline's manifest)

**Task:** consolidate the Text2SQL stack in `reports/sdk-versions.md`:
the schema prompt version, the validation layers, the repair metrics,
and the formatting contract — one block.

**Worked approach:** the Text2SQL manifest follows the pin discipline:
the prompt, the validator, the loop metrics, and the format contract —
each citing its drill.

**Pass criterion:** the manifest lists the stack with green commands as
recorded.

## Pitfalls recap

- Hand-typed schema prompts — they drift from the DDL; generate from
  the catalog.
- Single-layer validation — regexes miss comment tricks; the layers
  are independent by design.
- Unbounded repair loops — three attempts, then the honest failure;
  the counter is the bound.