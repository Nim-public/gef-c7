# Exercises — Analytics Agent

Expanded set with worked approaches. The deliverable: the analytics agent
with verified numbers, honest caveats, and an audit trail the reviewer
can walk.

## 1. Prebuilt + wrapper (from 01-prebuilt-finance-toolkits)

**Task:** integrate the prebuilt finance toolkit; wrap its price tool
with the provenance trio (`as_of`, `source`); run the limit drill
(blocked source → honest degradation).

**Worked approach:** the wrapper is where your W10 discipline meets
someone else's tool — provenance in, honesty out. The degradation drill
reuses the W8 ladder one more time.

**Pass criterion:** 3 responses carry `as_of` + `source`; the blocked
case answers honestly.

## 2. The composition loop (from 02-guarded-table-analytics)

**Task:** run 5 analytics queries; every answer carries `sql_used` +
`rows_considered`; one answer uses the schema tool first (verify in the
trace).

**Worked approach:** the schema-before-query rule is checked from the
trace, not the transcript — the tool-call order is the compliance
evidence.

**Pass criterion:** 5/5 answers with full provenance; schema-call-before-
first-query on unfamiliar tables.

## 3. Verification + mismatch drill (from 03-numeric-hallucination-defenses)

**Task:** wire `VERIFICATION_POLICY`; run 10 numeric queries; force one
mismatch (buggy verification SQL); grade the agent against the §3 rubric.

**Worked approach:** the mismatch grading is the drill's teeth: flag
present in *user view*, both queries shown, no silent pick. A perfect
10/10 with no mismatches means the drill wasn't planted correctly.

**Pass criterion:** verify-fires per policy; the mismatch is flagged in
the user view; both SQL texts visible.

## 4. The numeric eval set (from 02)

**Task:** add 5 numeric tasks with computable golds; score exact-match
on the number; wire into the W11 value gate.

**Worked approach:** numeric exact-match is the strictest eval in the
program — one digit off is wrong. The gate addition means Week 13+
changes can't silently break the analytics path.

**Pass criterion:** 5 tasks in the set; exact-match scored; the gate
tolerance for this metric is zero (numbers are exact).

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Wrapper + provenance in responses | drill output | 3 |
| Composition loop: provenance on 5/5 | transcripts | 3 |
| Mismatch drill: flag in user view | drill report | 4 |
| Numeric eval wired to the gate | eval + CI | 3 |
| Dual renderers (user vs reviewer) | render tests | 3 |

**Pass bar:** 13/16 to proceed to file 05 (agentic RAG). The mismatch
drill (4-pointer) is the analytics week's teeth — it proves the defenses
fire when reality disagrees with the model.

## Pitfalls recap

- Prebuilt tools trusted without provenance — wrap for timestamps and
  sources.
- Verification theater (verdict ignored) — the mismatch drill exists to
  catch the silent override.
- Caveats hidden from users — honesty is user-visible or it is not
  honesty.