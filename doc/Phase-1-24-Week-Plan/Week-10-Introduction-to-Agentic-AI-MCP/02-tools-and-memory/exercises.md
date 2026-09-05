# Exercises — Tools and Memory

Expanded set with worked approaches. The deliverable: a validated registry
over your Week-09 tools plus a budgeted fitter, both property-tested.

## 1. Registry hardening (from 02-tool-registry)

**Task:** implement the full registry with the five-test contract suite;
wire your three retrieval tools with error contracts.

**Worked approach:** write the five tests *first* (they are the spec):
happy path, unknown tool, schema violation, contract error, schema
hygiene. The implementation is then 40 lines that must satisfy them.

**Pass criterion:** 5/5 green; every tool raises `ToolError` with a hint,
never a bare string.

## 2. Protocol conformance (from 01-function-calling)

**Task:** with a canned LLM, verify the wire format at all four movements:
schemas sent, JSON-string arguments parsed, tool messages with ids, error
observations in place.

**Worked approach:** capture the exact message dicts per step and assert
against the protocol table (§1's four movements). The test doubles as
documentation of what your loop speaks.

**Pass criterion:** conformance test green; one injected malformed-JSON
case recovered with an instructive observation.

## 3. The fitter, property-tested (from 04-context-budgeting)

**Task:** implement `fit_context` + per-layer compressors; property-test:
(a) output ≤ budget per layer, (b) ids/numbers survive, (c) determinism
(same input, same output, twice).

**Worked approach:** hypothesis-style: generate random layer contents
(with embedded ids/numbers), assert the three properties. The
id-survival property is the one that catches the mid-JSON truncation bug
class permanently.

**Pass criterion:** properties hold over 200 generated cases; one
regression fixture per compressor.

## 4. Memory tier audit (from 03-memory-taxonomy)

**Task:** run 5 trajectories with the scratchpad tool; produce the per-tier
token table (foundations file 02's trace + fitter's counts); verify the
scratchpad contains conclusions, not transcripts (hand-check 10 notes).

**Worked approach:** the audit is 10 hand-checked notes against the
tier's definition — the cheapest possible memory eval, and the one that
catches "scratchpad = history copy" early.

**Pass criterion:** per-tier table committed; ≥8/10 notes are
conclusions; the compression drill (70% budget) leaves answers unchanged.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Registry + 5-test suite green | tests/ | 4 |
| Protocol conformance test | wire-format assertions | 3 |
| Fitter + 3 properties over 200 cases | property tests | 4 |
| Per-tier token table from real runs | reports/memory-audit.md | 2 |
| Hint A/B: steps-to-recovery measured | A/B table | 2 |

**Pass bar:** 11/15 to proceed to file 03 (MCP). The fitter's properties
are the week's quiet keystone — every later context change runs through
them.

## Pitfalls recap

- Tests that mock jsonschema away — the validation gate is the product;
  test it for real.
- Compressors that preserve length, not decision surface — the
  id-survival property is the guardrail.
- Token tables from one trajectory — five runs minimum; variance is the
  finding.
