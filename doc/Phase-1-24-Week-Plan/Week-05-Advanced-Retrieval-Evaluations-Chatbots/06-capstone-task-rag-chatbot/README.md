# 06 — Capstone Task: RAG Chatbot

> Parent topic: [../06-capstone-task-rag-chatbot.md](../06-capstone-task-rag-chatbot.md) · Week 5 index: [../README.md](../README.md)

The formal task: build the RAG chatbot with evaluation and explanations. The parent file contains the full requirements, rubric, and deliverable structure. This page summarizes the key checkpoints:

## Deliverables

1. **The chatbot** (`app.py`) — guarded turn pipeline with retrieval, generation, and output validation
2. **The eval** (`eval/`) — 30-case Ragas run with per-slice reporting
3. **The demo** — 8-turn transcript showing grounded answers, refusal, injection deflection, escalation

## The improvement evidence

Every capstone claims "we improved X" — the claim requires the before/after table:

| Metric | Before | After | Change |
|---|---|---|---|
| Hit rate @5 | | | |
| Faithfulness | | | |
| Answer relevancy | | | |
| p95 latency | | | |

The change that moved the metric is named (chunking upgrade, reranker, prompt fix) with its evidence — the W16-01 improvement-evidence pattern applied at week 5.

## The rubric highlights

- Architecture diagram with all stages named
- Eval table with n, slices, and judge version
- One improvement with measured delta
- Guardrail certification (injection, off-domain, PII, escalation)
- The W6 bridge: which components inherit into structured retrieval

## The W6 bridge

The RAG chatbot handles prose; Week 6 adds structured data (tables, SQL). The bridge: the chatbot's retrieval interface gains a second arm (SQL), the router gains a structured-data class, and the scope doc's data section gains the tabular sources. The W6-05 task builds on this foundation.
