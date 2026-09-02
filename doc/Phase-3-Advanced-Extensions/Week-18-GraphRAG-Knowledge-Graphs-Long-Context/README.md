# Extension E2 — GraphRAG, Knowledge Graphs & Long Context

> Extensions overview: [../README.md](../README.md)

**Builds on:** W4–6 (RAG stack) · W13 (graphs as orchestration — now graphs as *data*)

**Practice build:** [05-practice-graphrag.md](05-practice-graphrag.md)

---

## Why this extension matters

Vector RAG answers "what documents mention X" but fails at **multi-hop and global questions** — "how are these three vendors connected?", "summarize the main themes across 300 reports". GraphRAG adds an entity-relational structure that answers *connection* and *global summary* questions vectors can't, and long-context strategies redraw the RAG-vs-context-window boundary. This week adds the third retrieval brain to your capstone alongside W6's SQL.

## What you will be able to do after this week

- [ ] Model a corpus as a knowledge graph: entities, relations, extraction pipelines
- [ ] Implement GraphRAG-style retrieval: local (entity-centric) + global (community summary) search
- [ ] Explain when graphs beat vectors — with your corpus's examples
- [ ] Choose RAG vs long-context placement per question type; apply context compression
- [ ] Run a hybrid retrieval architecture (vector + graph + SQL) behind one router

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-knowledge-graphs-rag.md](01-knowledge-graphs-rag.md) | KG basics, entity/relation extraction, why graphs | 3 h |
| 2 | [02-graphrag-implementation.md](02-graphrag-implementation.md) | Microsoft GraphRAG: communities, local/global search | 3–4 h |
| 3 | [03-long-context-strategies.md](03-long-context-strategies.md) | Lost-in-the-middle, compression, RAG vs LC | 2–3 h |
| 4 | [04-hybrid-architecture.md](04-hybrid-architecture.md) | Vector + graph + SQL behind one router | 3 h |
| 5 | [05-practice-graphrag.md](05-practice-graphrag.md) | GraphRAG over your corpus (practice) | 4 h |

## Environment setup

```powershell
pip install networkx pandas community flask-limiter   # networkx = graph store (stdlib-adjacent)
pip install langchain-community                        # optional loaders
```

## Self-check before E3

1. "Which of our vendors also appear in the lawsuit documents?" — why does vector top-k fail this, and what graph operation answers it?
2. GraphRAG's *global* search doesn't retrieve chunks at all — what does it retrieve, and what question shape is it for?
3. Your model has a 1M-token window. Why is "just paste everything" still wrong for 80% of questions?
4. What does "lost in the middle" predict about where your answer chunk should sit in a 50k-token context?
5. In your capstone, which question type is graph-shaped vs vector-shaped vs SQL-shaped? (One example each.)
