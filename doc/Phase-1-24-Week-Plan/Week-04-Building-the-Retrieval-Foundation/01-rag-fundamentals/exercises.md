# Exercises — RAG Fundamentals

> Subfolder index: [README.md](README.md) · Parent: [../01-rag-fundamentals.md](../01-rag-fundamentals.md)

Labs for this subfolder. Shared fixture: 20 documents from your capstone domain (or the sample corpus).

---

## E1 — The limitations evidence pack (file 01)

1. Run the five limitation tests on your model; document each output verbatim.
2. For the private-data test: write 5 questions your corpus CAN answer — the model fails all 5 without RAG.
3. The provenance audit: for 10 bot answers, count verifiable claims — the number that motivates the citation contract.

**Worked approach:** exercise 2's comparison (no-RAG vs RAG on the same questions) is the before/after that anchors the entire retrieval arc.

## E2 — Pipeline assembly (file 02)

1. Build both pipelines over 20 documents; report per-stage timing and output counts.
2. The seam-drift drill: change the embedder at query time only — measure the retrieval collapse (W4-03's mismatch, demonstrated).
3. The failure injection: empty extraction for 20% of docs — trace the impact through every stage; verify the failure logging.

**Worked approach:** exercise 2's collapse measurement is the argument for the shared contract (E8-01's manifest) — the drift is measurable, the fix is the contract.

## E3 — Grounding certification (file 03)

1. Clause-by-clause: 4 tests, one per contract clause; each fails when the clause is removed.
2. The citation lifecycle: extract → validate → render; test with 0/1/5 citations.
3. The k-sweep: Ragas faithfulness (W5-05) at k ∈ {1, 3, 5, 10, 20} — the coverage/dilution curve.
4. The insufficiency battery: 5 unanswerable × 3 phrasings = 15 — ≥13/15 must escape; document the misses.

**Worked approach:** exercise 3's faithfulness-vs-k curve typically peaks at k=5 and declines — the dilution effect measured, which justifies the reranker (W5-03) that lets you retrieve more but paste less.

## E4 — The grounded answer quality bar (file 03)

1. For 10 grounded answers: verify every citation resolves; every number appears verbatim; every entity appears in its cited context.
2. The conflict test: two context blocks disagree (old vs new policy) — does the model pick, blend, or acknowledge? Write the disambiguation rule.
3. The multi-hop probe: a question needing TWO context blocks joined ("compare policy A with policy B") — does the grounded prompt handle it, or does it answer from one block only?

**Worked approach:** exercise 2's conflict test previews the multi-source fusion (W18-04) — the "which source wins" rule is an architecture decision, not a prompt hack.

## Self-assessment

- Can you name the five LLM limitations and show a measured failure for each?
- Can you assemble both RAG pipelines and state the seam contract between them?
- Can your grounded answers pass the four-clause certification — citations, numbers, escape, and only-context?
