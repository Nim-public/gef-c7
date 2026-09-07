# Exercises — Chunking Strategies

> Subfolder index: [README.md](README.md) · Parent: [../02-chunking-strategies.md](../02-chunking-strategies.md)

Labs for this subfolder. Shared fixture: your capstone corpus (≥20 documents) + the 25-query eval set (built in these labs).

---

## E1 — The boundary census (file 01)

1. Chunk 10 documents three ways (fixed/recursive/headers); count mid-sentence boundaries per strategy; eyeball 5 boundaries each.
2. The overlap math: verify `step = size - overlap` produces no infinite loops at your chosen settings; test the edge case `overlap == size`.
3. The minimum-viable floor: find the smallest `size` where every chunk contains one complete sentence.

**Worked approach:** the boundary census is the eyeball check that catches what metrics miss — a chunk that scores well but reads badly is a UX problem.

## E2 — Structure-aware extraction (file 02)

1. Header chunking on a real markdown doc — verify section paths, test the filtered retrieval.
2. Table extraction: 3 tables chunked whole; retrieve "what does the pricing table say?" — the whole-table chunk must win.
3. The transcript pipeline: diarized meeting output (E5-01) → speaker-turn chunks — verify speaker metadata and retrieval quality.

**Worked approach:** exercise 2 is the demonstration that generic splitters destroy tables — the "before" (generic) and "after" (whole-table) retrieval comparison is the evidence.

## E3 — The measured sweep (file 03)

1. Build the 25-query eval set (the fixture all sweeps use).
2. Run the full size×overlap sweep; produce the reporting table; identify the knee.
3. The context-aware upgrade: add contextual headers (W5-01) at the winning size; re-measure — the delta is the header trick's value on YOUR corpus.

**Worked approach:** exercise 3's before/after is the sweep's payoff — the delta justifies the extra processing, or rejects it.

## E4 — The metadata certification (file 04)

1. Schema review: every field has a named consumer; cut the orphans; add the missing ones.
2. The migration drill: add a field to existing chunks via backfill; verify completeness (zero chunks missed).
3. The citation rendering: from metadata alone, generate three citation formats for 5 chunks — inline, footnote, and tooltip.

**Worked approach:** exercise 3's three citation formats from one metadata schema demonstrates the design principle: the metadata is written once, consumed many ways.

## Self-assessment

- Can you state your chunking config (size, overlap, strategy) with the sweep evidence?
- Can you name the metadata field that enables each of: filtered retrieval, citation rendering, and security filtering?
- Can you add a new document type to the pipeline with the right chunking strategy and metadata in under 30 minutes?
