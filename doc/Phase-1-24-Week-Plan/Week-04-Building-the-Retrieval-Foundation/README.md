# Week 4 — Building the Retrieval Foundation: Study Guide

> Full schedule: [../README.md](../../README.md)

**Sessions:** Sat 26 Sep, 7–10 PM IST (Session 1) · Sun 27 Sep, 7–10 PM IST (Session 2) · Office Hours: see mentor channel

**Weekly task:** [05-capstone-task-search-engine.md](05-capstone-task-search-engine.md)

---

## Why this week matters

RAG is the single most-shipped LLM pattern in industry, and the next three weeks are all RAG: foundations (this week), advanced retrieval + chatbots + evals (Week 5), structured/tabular data (Week 6). Week 2 gave you embeddings; this week you build the system around them — and the capstone's search engine is the seam every later feature plugs into.

## What you will be able to do after this week

- [ ] Explain why base LLMs fail on private/fresh data, and what RAG does about it
- [ ] Draw and describe the full RAG architecture: ingestion → retrieval → generation
- [ ] Chunk documents four ways and justify size/overlap choices
- [ ] Store and search embeddings in FAISS and LanceDB (with metadata filtering)
- [ ] Implement keyword (BM25-style), semantic, and hybrid search
- [ ] Run Text2SQL on a structured table
- [ ] Ship a working search engine over your capstone corpus

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-rag-fundamentals.md](01-rag-fundamentals.md) | LLM limitations, BYOD, RAG architecture | 2 h |
| 2 | [02-chunking-strategies.md](02-chunking-strategies.md) | Fixed, overlap, recursive, structure-aware chunking | 3 h |
| 3 | [03-embeddings-vector-databases.md](03-embeddings-vector-databases.md) | FAISS index types, LanceDB, metadata filters | 3–4 h |
| 4 | [04-search-keyword-vs-semantic.md](04-search-keyword-vs-semantic.md) | BM25 vs vectors vs hybrid; scoring | 2–3 h |
| 5 | [05-capstone-task-search-engine.md](05-capstone-task-search-engine.md) | Build + evaluate the search engine (task) | 4–5 h |

## Environment setup

```powershell
pip install sentence-transformers faiss-cpu lancedb rank_bm25
pip install pypdf pandas requests beautifulsoup4   # corpus ingestion (Week 1 files)
```

## Self-check before Week 5

1. Your corpus has 50k chunks. Which FAISS index type, and what's the recall/speed trade vs flat search?
2. A user asks "refund policy" and the top hit is the *shipping* page. Name two independent things you could improve (retrieval side) and one (generation side).
3. Why does chunk overlap exist, and what failure does *too much* overlap cause?
4. When does keyword search beat embeddings — give a concrete query type from your capstone data.
5. What belongs in chunk metadata, and what does it enable downstream?
