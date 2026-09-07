# Exercises — Code Review Agent

Expanded set with worked approaches. The deliverable: the two-layer
review (deterministic + LLM), the deterministic report, and the
diff-aware review wired into CI.

## 1. The deterministic layer (from 01-deterministic-layer)

**Task:** build the AST walk (four rules) + ruff runner; run both on the
fixture bad-file; every finding cites a line and a rule code.

**Worked approach:** the deterministic layer is the review's facts — it
runs first, and its findings go into the LLM prompt as *given* context.
The bare-except rule is the W10 anti-pattern, statically enforced.

**Pass criterion:** every AST finding line-accurate; ruff rule codes
stable across runs.

## 2. The LLM layer (from 02-llm-review-layer)

**Task:** build the `Finding`/`Review` models; run the LLM layer with
the scanner findings in context; run the dedup; hand-check 30% of
findings (the sampled QA).

**Worked approach:** the "do not restate scanners" rule is tested by the
dedup — a duplicate finding is the layer's failure mode. The sampled
hand-check is the judge discipline, code edition.

**Pass criterion:** zero duplicate findings post-dedup; 30% hand-check
agreement recorded.

## 3. The report (from 03-report-generation)

**Task:** generate the report; verify byte-identical reruns; the
severity-sort mutation test (unknown severity → loud failure); summary
counts match the detail list.

**Worked approach:** the determinism test is the report's contract —
regenerated reports must be byte-identical or something in the pipeline
is nondeterministic (temperature, ordering, timestamps).

**Pass criterion:** byte-identical reruns; the sort mutation caught;
counts consistent.

## 4. Diff-aware review in CI (from 04-diff-aware-review)

**Task:** implement `changed_lines`; wire the diff-aware prompt; run on
a fixture diff; the line-hint audit enforces scope; wire the CI job.

**Worked approach:** the diff scope is the review's efficiency argument —
findings only on changed lines, full-file context for judgment. The
off-by-one drill protects the line arithmetic.

**Pass criterion:** line-hint audit green; the CI job runs on a fixture
PR; findings scoped to the diff.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Deterministic layer: line-accurate findings | AST/ruff tests | 3 |
| LLM layer: structured, deduped, sampled-QA'd | review tests | 4 |
| Report: byte-identical, severity-sorted | determinism test | 4 |
| Diff-aware review in CI | CI run on fixture diff | 3 |
| Scan findings in the LLM prompt (no rediscovery) | prompt test | 2 |

**Pass bar:** 14/18 to proceed to file 04 (agentic RAG). The report's
determinism (4-pointer) is the review agent's trust anchor — a review
that changes between runs is not a review.

## 6. The review-agent pin note

**Task:** consolidate the review stack in `reports/sdk-versions.md`:
scanner inventory, Finding schema, report generator version, CI
triggers, and the determinism command — one block.

**Worked approach:** the review agent reviews your code; its own stack
gets pinned first. The note is the same format as every framework week:
what was verified, when, by which command.

**Pass criterion:** note committed; the determinism and audit commands
green as recorded.

## 7. The review severity calibration (the judge protocol, code edition)

**Task:** hand-label 10 findings' severities; run the LLM layer twice;
build the agreement table per severity class; reword the rubric where
agreement drops below 80%.

**Worked approach:** the calibration protocol (W9 judge → W13 rubric →
here) — the severity classes are the rubric's dimensions. "Critical"
disagreements matter most: they route to humans first.

**Pass criterion:** two-run self-consistency ±1; hand agreement ≥80% on
critical/major; the rubric version stamped.

## Pitfalls recap

- LLM-only reviews — hallucinated line numbers and missed mechanical
  issues; the deterministic layer is the facts.
- Reports hand-edited after generation — derived data is regenerated;
  hand edits are lost changes.
- Findings outside the diff — the audit enforces scope; whole-file
  re-reviews are the budget leak.