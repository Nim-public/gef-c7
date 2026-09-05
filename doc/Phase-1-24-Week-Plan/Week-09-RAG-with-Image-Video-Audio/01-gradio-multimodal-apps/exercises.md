# Exercises — Gradio Multimodal Applications

Expanded set with worked approaches. The goal across all five: one deployed
app with a tested contract, ready for Week 10 to call as a tool.

## 1. Model fluency drills (from 01-gradio-model)

**Task:** build a three-tab app shell (Ingest/Search/Catalog as in file 03)
with *stub* handlers (return canned data); verify queue behavior with two
browser tabs and one `gr.State` counter per tab.

**Worked approach:** the shell-first pattern — UI shape and state flow
settled before any model code. The two-tab state check (`history` differs
per tab) is the acceptance gate for `gr.State` understanding.

**Pass criterion:** independent per-tab state; queue enabled; stubs typed.

## 2. Generator app with full run tuples (from 02)

**Task:** extend the food generator with (a) `strength` img2img mode,
(b) displayed latency, (c) a "reproducibility" button that regenerates the
last image and compares hashes.

**Worked approach:** keep the run tuple in `gr.State` (seed, guidance,
steps, mode, strength); the compare button re-runs `generate` with the same
tuple and asserts byte-equality — surfacing determinism to users, not just
tests.

**Pass criterion:** two consecutive same-tuple generations hash equal;
mode switches preserve independent tuples.

## 3. Cataloger with invariant tests (from 03)

**Task:** implement ingest + search fully; add `tests/test_cataloger.py`
with the row-alignment invariant and the idempotency property (ingest same
file twice ⇒ one row).

**Worked approach:** use a temp SQLite file + a fresh matrix in a fixture;
`assert ingest_image(p, n, ...) == 0` on the second call. Property-style:
after any ingest sequence, `len(ids) == matrix.shape[0]`.

**Pass criterion:** both tests green; an injected duplicate-caption row is
caught by the invariant test.

## 4. Deploy and measure (from 04)

**Task:** deploy to a CPU Space; fill `reports/deployment-latency.md` with
cold start, p50/p95 search latency, and generation latency at default
knobs; compare with local numbers.

**Worked approach:** measure with a 20-query script against the API
endpoint (`gradio_client` or curl); p95 matters because your Week-10 agent
will chain these calls — tails multiply.

**Pass criterion:** the report contains local vs Space numbers and one
sentence on where the gap comes from (queue, cold cache, hardware).

## 5. Capstone seam: the tool contract (from 04-deployment-patterns)

**Task:** write `doc/capstone/tool-contract.md`: the JSON schema of
`retrieve` (in/out), error semantics (what a missing sidecar returns), and
the latency budget the Week-10 agent can assume.

**Worked approach:** the schema is the API exercise 2's return shape,
formalized; error semantics come from the W8 degradation matrix. Keep it
under one page — Week 10 reads it before building the agent.

**Pass criterion:** schema committed; a `curl` example reproduces the
documented response byte-for-byte (same fixture).

## Pitfalls recap

- UI types (`gr.Image`) leaking into handler signatures — pure functions +
  UI wrappers, or the API client breaks.
- Latency measured from the UI only — measure the *endpoint*; the UI adds
  render time your agent will not pay.
- Contracts without error semantics — Week 10's agent needs "missing sidecar
  → `{}` with flag", not an exception stack.
