# Week 5 — Advanced Retrieval, Evaluations & Chatbots: Study Guide

> Full schedule: [../README.md](../../README.md)

**Sessions:** Sat 3 Oct, 7–10 PM IST (Session 1) · Sun 4 Oct, 7–10 PM IST (Session 2) · Office Hours Thu 8 Oct, 7–8 PM IST

**Weekly task:** [06-capstone-task-rag-chatbot.md](06-capstone-task-rag-chatbot.md)

---

## Why this week matters

Week 4's engine retrieves *okay* chunks; this week makes it retrieve *the right ones, provably*. Advanced chunking, embedding-model selection, hybrid filtering, fusion and reranking each buy retrieval quality points — and the evaluation harness is what proves they did. Then the engine disappears behind a chatbot with guardrails, which is the actual product form your capstone ships.

## What you will be able to do after this week

- [ ] Upgrade chunking: semantic and content-aware strategies, measured against Week 4's harness
- [ ] Run a structured embedding-model bake-off (MiniLM, mpnet, E5, BGE, OpenAI, Cohere, ELSER)
- [ ] Add metadata filtering and multi-query fusion to retrieval
- [ ] Add a reranker (cross-encoder) on top of fused retrieval
- [ ] Wrap retrieval in a chatbot with guardrails (responsible AI)
- [ ] Evaluate answers with Ragas (faithfulness, relevancy, context precision/recall) and explain results to users

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-advanced-chunking.md](01-advanced-chunking.md) | Semantic chunking, content-aware chunking, contextual headers | 2–3 h |
| 2 | [02-embedding-models.md](02-embedding-models.md) | Model bake-off incl. sparse (ELSER) & APIs | 3 h |
| 3 | [03-hybrid-filtering-fusion-reranking.md](03-hybrid-filtering-fusion-reranking.md) | Filters, multi-query fusion, cross-encoder reranking | 3–4 h |
| 4 | [04-rag-chatbot-guardrails.md](04-rag-chatbot-guardrails.md) | RAG chatbot architecture + responsible-AI guardrails | 3 h |
| 5 | [05-response-evaluation-explanations.md](05-response-evaluation-explanations.md) | Ragas metrics, explanation generation | 3 h |
| 6 | [06-capstone-task-rag-chatbot.md](06-capstone-task-rag-chatbot.md) | RAG chatbot over your data (task) | 4–5 h |

## Environment setup

```powershell
pip install sentence-transformers transformers lancedb rank_bm25 ragas datasets
pip install openai python-dotenv pytest
```

## Self-check before Week 6

1. Your hit rate is 0.55 and the boss wants 0.8. List four retrieval-side interventions in the order you'd try them, cheapest first.
2. Why does a cross-encoder reranker outscore bi-encoder retrieval — and why not use it over the whole corpus?
3. Faithfulness is 0.7. Name the two most likely pipeline stages responsible and how you'd confirm which.
4. What does ELSER do that dense embeddings can't? What do dense embeddings do that ELSER can't?
5. Your chatbot's guardrail layer has 30 ms budget. What goes in, what gets cut?
