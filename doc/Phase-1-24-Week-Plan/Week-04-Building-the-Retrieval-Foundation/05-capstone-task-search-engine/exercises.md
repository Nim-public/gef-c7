# Exercises — Search Engine Task

> Subfolder index: [README.md](README.md) · Parent: [../05-capstone-task-search-engine.md](../05-capstone-task-search-engine.md)

Labs that certify the search engine. The engine is the capstone's core retrieval component — every later week builds on it.

---

## E1 — Ingestion certification (file 01)

1. Ingest 30 sources; crash at 60%; resume — verify counts match a full run.
2. Duplicate detection: same content, 3 paths — one fingerprint, zero duplicate chunks.
3. Change detection: modify one document; verify only that source re-ingests.
4. The state dashboard: per-source state (done/failed/pending) in a CLI or Gradio view.

**Worked approach:** exercise 1's crash-resume is the ingestion certification — the state machine must survive any interruption without data loss or duplication.

## E2 — Search service certification (file 02)

1. The CLI: 10 queries across question types — verify results, citations, and the caveat behavior.
2. The API: wrap in FastAPI; test with curl; measure p95 latency.
3. The multi-consumer test: CLI, API, and Gradio all return identical results for the same query+filters.
4. The threshold drill: 20 wrong-passage queries — the caveat fires at the calibrated rate (not 0%, not 100%).

**Worked approach:** exercise 3's multi-consumer consistency test is the seam-integrity check — if the CLI and API return different results, there's a bug in the shared function.

## E3 — The evaluation certification (file 03)

1. The 25-query eval set built and hand-verified; the metrics table produced.
2. The failure deep-dive: the 5 worst queries traced through the pipeline; the failure class per query.
3. The before/after: one improvement (chunking, embedder, or threshold) applied; the metrics table re-run with the delta.
4. The eval-set maintenance: 5 new production queries added; the coverage gap documented.

**Worked approach:** exercise 3's before/after is the capstone's evidence pattern — every improvement claim carries a measured delta. This pattern repeats through W16-01's versioned evals.

## Self-assessment

- Can you ingest a new document and have it searchable in under 5 minutes?
- Can you explain your search engine's architecture (stores, arms, fusion) from memory?
- Can you state your hit rate, your threshold, and your p95 latency — with the evidence?
