# 05 — Weekly Task: Build an AI-Powered Search Engine

> Week 4 index: [README.md](README.md) · **Due: before Week 5 (by 3 Oct)**

**Task (from the schedule):** *Implement an AI-powered Search Engine in your capstone project.*

This is the first capstone component that is a *system*, not a function. Deliverable: a search engine over your capstone corpus with hybrid retrieval, metadata filtering, citations, and an evaluation harness — the foundation Weeks 5–6 upgrade and the Week 17+ capstone keeps.

---

## 1. Deliverable

```
search/
  ingest.py          # parse → chunk → embed → index (re-runnable, incremental)
  search.py          # hybrid search: BM25 + vectors + RRF + filters
  cli.py             # query from terminal, print results with citations
  search_eval.jsonl  # 25 queries with relevant chunk ids
  README.md          # decisions, eval table, failure modes
```

Demo: 5 queries in a transcript — 2 semantic wins, 1 keyword win, 1 filtered query, 1 "no results" case.

## 2. The ingestion pipeline (`ingest.py`)

From Weeks 1–4, assembled:

```python
# pseudo-flow, each stage a function you've already written
docs   = load_docs("data/raw")            # W1-04: PDF/HTML/CSV → text
chunks = chunk(docs, size=800, overlap=100, strategy="recursive")   # W4-02 + metadata
emb    = encode([c["text"] for c in chunks])                        # W2-03, normalized
store  = build_index(chunks, emb)         # W4-03: LanceDB table + BM25 corpus
```

Requirements:

- **Re-runnable**: delete/re-add by source id; no duplicate chunks on second run (test this!)
- **Incremental**: adding doc #51 doesn't rebuild 50 docs
- **Metadata schema** committed in `README.md` (id, source, page/section, doc_type, updated)
- One **ingestion report**: docs in → chunks out → embed time → index size

## 3. The search engine (`search.py`)

```python
def search(query: str, k: int = 5, doc_type: str | None = None) -> list[dict]:
    bm25_hits    = bm25_search(query, k=10, doc_type=doc_type)
    semantic_hits = vector_search(query, k=10, doc_type=doc_type)
    fused = rrf([h["id"] for h in bm25_hits], [h["id"] for h in semantic_hits])[:k]
    return fetch_full(fused)      # rejoin with text + metadata for citation
```

- Hybrid via RRF (file 04); both retrievers respect the same metadata filter
- Every result carries: text, source, section/page, and the component scores/ranks (for debugging)
- Threshold option: if the best vector distance is above your elbow (file 03, ex. 5), return `[]` + a flag — "no good match" is a first-class output

Interface choice (either): CLI `py search.py "refund timeline" --type policy` or a 20-line FastAPI `/search` endpoint (Base Camp 3 skills). Gradio UI if you want polish.

## 4. The evaluation harness (`search_eval.jsonl`)

25 queries, mixed on purpose:

- 10 paraphrase-y questions (semantic should win)
- 5 exact-identifier queries (codes, SKUs, names — keyword should win)
- 5 multi-constraint ("refund timeline for cancelled *annual* plans")
- 5 that have **no answer** in the corpus (engine should return nothing/low-confidence)

Report in `README.md`:

| System | Hit rate @5 |
|---|---|
| BM25 |  |
| Semantic (all-MiniLM-L6-v2) |  |
| Hybrid (RRF) |  |

Plus: 3 failure cases with one-line diagnoses (from file 04's categories).

## 5. Rubric

- [ ] Ingestion re-runnable + incremental; duplicates impossible
- [ ] Hybrid retrieval with metadata filtering working
- [ ] Citations on every result (source + section/page)
- [ ] Eval table with ≥3 systems; harness re-runnable in <1 min
- [ ] No-answer case handled explicitly
- [ ] README: chunking decision with evidence (size/overlap from your sweep), model choice, 3 failure modes

## 6. What Week 5 does to this engine (design for the seam)

- **Chunking** → semantic/content-aware upgrade (your harness decides if it helped)
- **Embeddings** → model bake-off (the harness runs unchanged)
- **Retrieval** → fusion gets multi-query expansion; add a **reranker** stage on top of the fused list
- **Search** → becomes a chatbot (Week 5's task) — your `search()` function is exactly what the chatbot calls as its knowledge tool

Design for that seam now: one function, clean dict in/out, no UI assumptions.

Bring your eval table to Office Hours — mentors will challenge your query set before your architecture, because a weak eval set makes every later "improvement" unfalsifiable.
