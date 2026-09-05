# Exercises — Custom Tools & Toolkits

Expanded set with worked approaches. The deliverable: `CorpusTools` and
`AnalyticsTools` toolkits, battery-tested, parity-proven against the W10
MCP surface.

## 1. Toolkit construction (from 01, 02)

**Task:** build `CorpusTools` (retrieve, get_unit_text, get_image) with
mode config; construct demo and eval agents with different
`include_tools`; verify scoping assertions.

**Worked approach:** the two-constructor drill (demo vs eval) proves the
config surface — same class, different privilege. The agent's *visible*
tool set is the assertion, not the constructor's.

**Pass criterion:** scoping assertions green; derived schemas match the
W10 hand-written ones (modulo style).

## 2. Advanced tools drilled (from 03-advanced-data-tools)

**Task:** build `AnalyticsTools`; run the guarded-SQL battery; execute
the verification drill (answer + independent `verify_number`, both SQLs
in the transcript) and the chart drill (file lands repo-relative, answer
names it).

**Worked approach:** the verification drill is the numeric-hallucination
test — the answer's number must be *derivable* from the second query's
rows, checked by the harness, not by vibes.

**Pass criterion:** battery 4/4 refusals; verification transcript shows
both queries; chart artifact exists and is cited.

## 3. Cross-surface parity (from 04-toolkit-testing)

**Task:** the parity test between the W10 MCP surface and the Agno
toolkits over all shared tools; commit the parity table.

**Worked approach:** same Week-09 functions, two skins — the drift
detector is the deliverable. Semantic parity (names, args, hints) is the
bar; wire-shape differences are documented, not absorbed.

**Pass criterion:** parity test green for all shared tools; drifts (if
any) ticketed with owners.

## 4. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Toolkits built, schemas derived correctly | diff tests | 3 |
| Guarded-SQL battery 4/4 | guardrail tests | 3 |
| Verification + chart drills | transcripts | 3 |
| Cross-surface parity green | parity test | 4 |
| Flag drills (scoping, stop, cache) | flow tests | 2 |

**Pass bar:** 13/16 to proceed to file 04 (the analytics agent). The
parity test (4-pointer) is the discipline anchor — one source of truth
for tools, two skins.

## 8. The toolkit pin note

**Task:** extend `reports/sdk-versions.md` with the toolkit inventory:
class names, derived-schema date, Agno version, and the parity-test
command from exercise 3.

**Worked approach:** toolkits are code, but their *schemas* are derived
at runtime — the pin note records when the derivation was last verified
against the W10 hand-written contracts.

**Pass criterion:** note committed; the parity command green as of the
recorded date.

## 6. The toolkit design review

**Task:** present your two toolkits (`CorpusTools`, `AnalyticsTools`) to
the review persona: surface list, scoping matrix (which agent sees what),
flag inventory (stop/cache/show), and error contracts per tool — one
page in `reports/toolkit-review.md`.

**Worked approach:** the review is the tool-surface page (W10 file 03)
re-skinned: same rigor, new mechanism. Every tool row carries its
derivation source (hints/docstrings) and its battery cases; the review
passes the W10 standard or it is not done.

**Pass criterion:** every tool has a contract, a battery row, and a
scoping entry; the page links the parity test.

## 7. The flag decision table

**Task:** for each tool in both toolkits, decide: `stop_after_tool_call`?
`show_result`? `cache_results`? Write the table with the *reason* per
decision — flags are behavior, not decoration.

**Worked approach:** terminal tools (finalize, submit) get
`stop_after`; formatting tools get `show_result`; expensive deterministic
tools get cache with a TTL. A flag without a reason gets removed — the
table is the review that keeps the toolkit minimal.

**Pass criterion:** decision table committed; one flag deliberately
*removed* with the reason (proving the review was real).

## Pitfalls recap

- Toolkits without docstring discipline — the model reads them exactly
  like MCP descriptions; same bar.
- Scoping verified by reading code — assert the *visible* set; the
  model's view is the truth.
- Verification hooks that re-run the same query — independence is the
  property; test that the second query differs.