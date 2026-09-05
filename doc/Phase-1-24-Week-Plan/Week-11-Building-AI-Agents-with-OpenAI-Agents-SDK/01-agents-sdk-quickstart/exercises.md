# Exercises — Agents SDK Quickstart

Expanded set with worked approaches. The deliverable: your Week-09/10
tools and constitution running under the SDK, with tracing merged into
your trajectory store.

## 1. Anatomy mapping, completed (from 01-sdk-anatomy)

**Task:** finish the W10→SDK mapping table for your agent; mark each row
"SDK" or "manual, still mine"; the manual rows are this week's remaining
work list.

**Worked approach:** expected distribution: loop, tools, output typing,
sessions, tracing → SDK; context fitting, registry revalidation posture,
gates → manual. The table is the porting plan for file 06.

**Pass criterion:** every W10 component classified; the "manual" list
matches file 06's porting scope.

## 2. Turn accounting (from 02-loop-mechanics)

**Task:** with canned tool calls, predict turns for the three call shapes
(1 call, 3 parallel calls, 2 calls + handoff); verify against
`RunResult`; then set `max_turns=2` on task 8 (multi-hop) and verify the
handler fires with `include_in_history=False`.

**Worked approach:** turn = model invocation. The multi-call shape being
*one* turn is the counter-intuitive bit; the handler exercise proves the
fallback replaces your `"budget exhausted"` string cleanly.

**Pass criterion:** predictions match; fallback fires; session stays
clean (no degraded exchange).

## 3. Typed-answer migration (from 03-structured-output)

**Task:** define `Answer` (answer, citations, confidence, degraded); add
the citation validator; port the citation audit from W9-04 to Pydantic;
run the impossible-query task — the model-time validation must catch a
phantom citation.

**Worked approach:** the validator needs the retrieved-ids set in
context — wire it through the run context (this is the exercise's real
work); the audit logic itself is unchanged from Week 09.

**Pass criterion:** phantom citation raises at model time; a clean run
validates; the audit logic diff vs W9-04 is logic-identical.

## 4. Session lifecycle (from 04-sessions)

**Task:** multi-turn drill (2 runs, one session); undo drill (`pop_item`
before a corrected retry); budget drill (40-item episode through your
fitter's trimmed-list pattern); verify tokens-in stays bounded while the
session retains all items.

**Worked approach:** the trimmed-list pattern (session = store of record,
trimmed list = model input) is the load-bearing move — the drill proves
both halves (bounded tokens, full retention).

**Pass criterion:** three drills green; the bounded-tokens/full-retention
pair demonstrated in one report table.

## 5. Tracing merged (from 05-tracing)

**Task:** local trace processor → JSONL; `trace_to_trajectory` → parquet
rows; run 10 tasks; confirm the W10 scorecard computes identically from
SDK traces vs your hand instrumentation (tolerance ±5% on tokens).

**Worked approach:** the merge test is the acceptance gate — the two
capture paths (your seams, SDK spans) must agree, or one is wrong; name
the discrepancies (handoff spans have no W10 equivalent).

**Pass criterion:** 10/10 trajectories reconstructed; scorecard parity
within tolerance; discrepancies documented.

## 6. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Mapping table complete (SDK vs manual) | mapping table | 2 |
| Turn accounting + handler drill | test run | 3 |
| Typed Answer + validator catching phantoms | structured-output tests | 4 |
| Session drills (multi-turn, undo, budget) | drill report | 3 |
| Traces → trajectory parity ≤5% | merge test | 3 |

**Pass bar:** 12/15 to proceed to file 02 (tools, handoffs, guardrails).
The typed-answer migration (4-pointer) is the week's first real win —
validation moves to model time.

## Pitfalls recap

- Mapping tables that mark everything "SDK" — context fitting and gates
  stay manual; honesty in the table is the porting plan.
- Validators that mutate instead of raise — hidden fixes hide model
  failures.
- Token double-counting between spans and your ledger — one source of
  truth per metric, named in the dictionary.
