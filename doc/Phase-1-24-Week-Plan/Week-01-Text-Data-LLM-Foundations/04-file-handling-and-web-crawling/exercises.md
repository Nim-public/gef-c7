# Exercises — File Handling & Web Crawling

> Subfolder index: [README.md](README.md) · Parent: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md)

Shared fixture: build the synthetic scraped corpus from `02-regex-applied.md`'s exercises (1 MB, mixed quality) plus 6 PDFs (3 born-digital, 2 scans, 1 corrupted) — reused across all labs.

---

## E1 — Format triage (file 01)

1. Store the same 500k-row table as CSV, JSON (full), JSONL, and Parquet. Table: file size, full-load time, memory, append-a-row cost.
2. `safe_read` implementation (try encodings in order, return encoding used) — tested on BOM'd, latin-1, UTF-8, and corrupted files.
3. JSONL crash drill: truncate a JSONL file mid-line; write the tolerant reader; verify it processes all complete records and reports the dropped tail.

**Worked approach:** exercise 1's append-cost row is why JSONL exists — CSV appends break headers, JSON appends break the tree.

## E2 — PDF decision tree (file 02)

1. Route the 6-PDF fixture through the decision tree; document which layer each needed and the audit numbers (empty rate, median chars).
2. Table extraction quality: pdfplumber on the table-heavy PDF — reconstruct as markdown, eyeball 3 tables, list the cell-order errors.
3. OCR preprocessing sweep on the worst scan: baseline / grayscale / grayscale+upscale / +threshold / +deskew — word count and spot accuracy per variant.

**Worked approach:** the sweep table usually shows a 2–5× word-count difference between baseline and the best preprocessing — that delta *is* the value of preprocessing.

## E3 — Crawl hardening (file 03)

1. Rate-limit test: crawl 30 pages of a sandbox site with 0.5 s, 2 s, and randomized sleep — log HTTP status codes per profile; correlate throttling with politeness.
2. Robots compliance check: run `can_fetch` against 10 URLs across 3 sites; log the disallowed ones and what a violation would have risked.
3. Link-scope drill: verify same-site scoping against (a) an external link, (b) a `mailto:`, (c) a `javascript:` href, (d) a fragment-only link — fix any that leak through.
4. Offline replay: crawl 20 pages to disk; then disable network and re-run only the parse/extract stage — prove the pipeline splits cleanly into fetch and parse.

**Worked approach:** exercise 4's fetch/parse split is the architecture lesson — the crawl loop in file 03 §5 becomes trivially resumable once raw HTML is cached.

## E4 — Corpus builder certification (file 04)

1. Ingest 30 assets; kill the process twice at random points; resume to completion — verify final counts match a from-scratch run.
2. Duplicate detection: ingest the same content under 3 URLs; verify one fingerprint, one chunk set.
3. Change detection: modify one document by a single character; verify only that asset re-ingests (and its old chunks become orphans — run the cleanup).
4. Failure ledger: force 6 failures of 3 different classes (network, parse, empty) — verify the report's per-class counts and error messages are actionable.
5. Provenance audit: pick 5 chunks at random; trace each back to its source asset and content fingerprint via the metadata.

**Worked approach:** exercise 3's change-detection (one character → re-ingest) is the fingerprinting contract made visible — the property that makes W16-01's corpus versioning trustworthy.

## Self-assessment

- Can you state, for any file a practice build produces, which format it should be and why (JSON/JSONL/Parquet/CSV/raw)?
- Can you take a crashed ingestion run and resume it without duplicating a single chunk?
- Can you route an unknown PDF to the right extraction layer in under 5 minutes, with evidence?
