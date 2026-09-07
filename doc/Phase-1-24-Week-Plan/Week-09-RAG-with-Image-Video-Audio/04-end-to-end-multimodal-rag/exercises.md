# Exercises — End-to-End Multimodal RAG

Expanded set with worked approaches. The deliverable: the full pipeline
green end-to-end with a committed ledger and contract-verified responses.

## 1. Ingest to gate (from 01-ingestion)

**Task:** run ingest on your manifest; then run the validation gate; then
verify: row count == manifest count, two vector columns populated per
modality rules, caption_version stamped everywhere.

**Worked approach:** the gate runs *inside* the ingest script's happy path
— a corpus that would fail validation never serves. The verification
assertions are one `tests/test_ingest.py`.

**Pass criterion:** all three checks green; second run adds zero rows.

## 2. Retrieval route coverage (from 02-hybrid-retrieval)

**Task:** for each routing class, log which search subsets fire; verify
that P1-fts fires FTS only, P2 fires image_vec only, P1-merged fires both.

**Worked approach:** the retriever logs its subset per call; the test
asserts subset == route's contract. This is the router-executor agreement
check — cheap and prevents the wrong-column bug class permanently.

**Pass criterion:** 3 route classes, 3 correct subsets, one test.

## 3. Generation audit gate (from 03-grounded-generation)

**Task:** run 10 P3-quota answers; every response carries `audit`; inject
one phantom citation and one no-citation answer; both must flag.

**Worked approach:** audit is pure — test it directly with crafted inputs
(phantom ids, empty citations) rather than through the model; the model
then gets a smaller spot-check (3 answers hand-verified).

**Pass criterion:** audit tests green; 3 hand-verified answers logged.

## 4. The committed ledger (from 04-cost-latency-ledger)

**Task:** produce the p50/p95 table for both modes from 50 measured
answers; commit `reports/latency-ledger.md` with the measurement script
name and machine spec.

**Worked approach:** 50 answers = 25 queries × 2 runs; report per stage
per mode. The drift check (two runs within 20%) is the honesty gate —
if it fails, find the warm-up or the noisy neighbor before publishing.

**Pass criterion:** table + drift note + machine spec committed.

## 5. Capstone: end-to-end demo script (from all files)

**Task:** write `scripts/demo.py`: 5 queries covering all routes, printing
the answer, mode, citations, and ledger line per query — the demo that
runs from a fresh clone with one command.

**Worked approach:** the script is the integration test users see: it
must degrade gracefully (W8 ladder) when a component is down, and its
output *is* the architecture section's evidence.

**Pass criterion:** fresh-clone run succeeds; every answer shows mode +
citations; ledger lines sum to sane totals (<p95 × 1.5).

## 7. The one-command acceptance run

**Task:** wrap everything (ingest check → battery → eval tables → demo)
into `scripts/accept.py` that exits nonzero on any failure — the single
command a reviewer (or you, pre-demo) runs to certify the build.

**Worked approach:** acceptance = the four gates in sequence with early
exit and a final one-line verdict per gate. Runtime budget: <5 min;
anything slower means caching, not skipping.

**Pass criterion:** green run prints four PASS lines; any injected
failure (bad hash, nprobe=1) makes the corresponding gate red.

## 6. The kill-chain drill (the demo's real test)

**Task:** run `demo.py` five times, killing a different component each
time (LanceDB, BLIP, the LLM, the router's FTS index, the quota counter)
— the demo must degrade with a visible mode flag every time, never crash.

**Worked approach:** kill = point the component at a bad path (no monkey-
patching); the degradation ladder from W8 + the flagged answers from file
03 are the expected behavior. Log which component died and what the user
saw — that log *is* the reliability section of your README.

**Pass criterion:** 5/5 degradations handled; user-visible messages name
the degraded mode; ledger still records timings.

## Pitfalls recap

- Demo scripts that import UI modules — pure pipeline only; the app is a
  separate consumer.
- Ledger tables without machine spec — unreproducible numbers; spec line is
  mandatory.
- Integration tests without the degradation path — kill a component and
  re-run; the ladder is part of the contract.
