# Exercises — String Manipulation & Regex

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

Labs for this subfolder. Shared fixture: build a 1 MB synthetic "scraped corpus" (W16-02 patterns) — headers, PII, invoices, multilingual text, zero-width characters — reused across all exercises.

---

## E1 — String operations stress test (file 01)

1. Take 1,000 lines of the corpus; implement `clean_line` (strip, collapse whitespace, drop empties/comments). Report kept/dropped.
2. Deliberately break it: feed `None`, an empty string, and a 10 MB line. Make the function fail loudly (typed exceptions), not silently.
3. Benchmark three building strategies (`+=`, `join`, `StringIO`) on the corpus — table the times and explain the asymptotics.

**Worked approach:** the `+=` loop is O(n²) — time it at 10k/50k/100k lines and fit the curve.

## E2 — Template clinic (file 02)

1. Port the W3-01 `triage_prompt` into a `ChatPromptTemplate`-style function with JSON examples (brace escaping!), a few-shot block, and a token-budget assert.
2. Write 5 pytest cases: happy path, missing variable raises, `None` value caught, budget exceeded caught, JSON braces render intact.
3. Deliberately remove one assert and inject `None` — show the corrupted prompt that reaches the LLM.

**Worked approach:** the failure mode to demonstrate is the *silent* one — a prompt with "None" rendered where a category should be, which the model then answers around.

## E3 — Unicode forensics (file 03)

1. Scan the corpus for every invisible character from the §3 table; report per-type counts and the sites where they appear.
2. Find 3 confusable pairs (Cyrillic/Greek lookalikes in tickers or domains) using the confusables screen.
3. Build the NFC policy test: index the corpus twice (NFC-applied vs raw) and find queries whose results differ.

**Worked approach:** zero-width characters usually enter via copy-pasted web content — trace one back to its source page (W1-04 skills).

## E4 — Regex golf, production edition (file 04)

1. Write patterns for: Indian mobile numbers (multiple formats), GSTIN (`\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z]Z?[A-Z0-9]`), invoice references, dates in 3 formats.
2. For each: 10 positive tests, 10 adversarial negatives (near-misses). Target: zero false positives on the negatives.
3. Find the catastrophic-backtracking case in any pattern you wrote (test with a 10k-char non-matching string); fix it.

**Worked approach:** near-misses are the real test — a GSTIN regex that also matches PANs is the production bug.

## E5 — The extraction pipeline (file 05)

1. Build `extract_invoice` + `verify_extraction` + `scrub_pii` over 10 synthetic invoices; measure field-level accuracy per pattern.
2. Inject 5 corruptions (swapped digits, missing fields, extra text) — verify the verification layer flags each.
3. Pipeline order experiment: apply `scrub_pii` *before* `extract_invoice` — which fields break? Document the ordering constraint.
4. Sentence-aware chunking vs naive splitting on the same document: measure boundary quality (eyeball 10) and downstream retrieval hit-rate (W4 harness, 10 queries).

**Worked approach:** exercise 3's finding — PII scrubbing can destroy the very values you extract — is the ordering-constraint lesson; document it in the pipeline as a named stage order.

## Self-assessment

- Can you write a working extraction pattern with tests in under 10 minutes, including adversarial negatives?
- Can you explain (with a demo) why mixed Unicode normalization breaks dedup and search?
- Can you state, for each pipeline stage, what the previous stage must guarantee?
