# 06 — Weekly Task: RAG Chatbot with Evaluation & Explanations

> Week 5 index: [README.md](README.md) · **Due: before Week 6 (by 10 Oct)**

**Task (from the schedule):** *Develop a RAG-based Chatbot from personal or project-specific data, exploring response evaluation and explanations.*

This is the flagship deliverable of the retrieval arc: your Week 4 engine behind Week 3's conversational interface, upgraded with Week 5's retrieval stack, guarded, and *measured*.

---

## 1. Deliverable

```
ragbot/
  app.py                 # chatbot (CLI/Gradio) calling the search engine
  guards.py              # input + output guardrails (file 04)
  eval/
    eval_set.jsonl       # 30 questions with reference answers
    run_eval.py          # Ragas four-metric run
    results.md           # metrics table + before/after story
  README.md               # architecture, guardrail design, failure analysis
```

Demo transcript: 8 turns showing — a grounded cited answer, a multi-hop question answered via fusion, a no-answer refusal, an injection deflection, and one answer with its explanation line.

## 2. The chatbot (core loop)

Assemble `turn()` from file 04: input guards → retriever (fusion + rerank + prefilter, file 03) → grounded generation (file 01's contract + Week 3's constitution) → output guards → explanation line. Target: **p95 < 5 s** end-to-end; record your latency table.

Retrieval upgrades to include (each with its measured contribution in `results.md`):

- [ ] Contextual headers or semantic chunking (file 01) — with harness numbers
- [ ] Embedding bake-off winner pinned (file 02), revision recorded
- [ ] Fusion + cross-encoder reranker (file 03), stage table
- [ ] Prefiltered metadata (permissions/type) — security test shown

## 3. Evaluation (graded component)

30-row eval set: 15 answerable (reference answers written *before* looking at bot outputs), 5 paraphrase-twins of each other (consistency probes), 10 unanswerable-in-corpus.

`run_eval.py` reports the four Ragas metrics (file 05) per slice:

| Slice | Faithfulness | Relevancy | Ctx precision | Ctx recall | n |
|---|---|---|---|---|---|
| all |  |  |  |  | 30 |
| answerable |  |  |  |  | 20 |
| unanswerable |  |  |  |  | 10 |

Then the **story**: one intervention (your choice — reranker, chunking upgrade, prompt change), metrics before → after, and one paragraph interpreting *which metric moved and why that's the stage you fixed*. This before/after story is the actual skill — the metrics are just instruments.

Also: judge stability check (run the eval twice, report score spread). If spread > 0.1, your conclusions need bigger n — say so.

## 4. Explanations & guardrails (graded component)

- [ ] Citation on every factual claim; invalid-citation validator active (file 04 §3)
- [ ] No-answer escape fires on ≥ 9/10 unanswerable questions
- [ ] Input guardrails: injection battery + off-domain + PII-in (10 cases, logged)
- [ ] Confidence hook: rerank-score-based escalation (file 04 ex. 5) with a stated threshold and its trip rate
- [ ] `explain()` line rendering sources + retrieval confidence per answer

## 5. Rubric

- [ ] End-to-end p95 latency recorded with stage breakdown
- [ ] Eval table: 4 metrics × ≥3 slices, judge model + temperature documented
- [ ] One before/after improvement story with a number
- [ ] Guardrail trip log committed (JSONL) — this is next month's eval gold
- [ ] README: architecture diagram (ASCII fine), 3 failure modes with diagnoses
- [ ] Week-6 seam noted: which parts of this stack will ingest *structured* data (hint: the retriever interface)

## 6. Stretch (pick one)

- Streaming answers with citations arriving progressively
- Follow-up question handling: rewrite "what about refunds *there*?" into a standalone retrieval query (fusion prompt does this — extend it to use chat history)
- Multi-source toggle: let the user pick scope (`--source handbook` / `--type faq`) and show how filters change the answer
- Judge swap: run Ragas with a different judge model; report score deltas (file 05 exercise 4)

Office Hours (8 Oct) is mid-build for this task — bring the *eval table*, not the demo: mentors can fix architecture from bad numbers, but nothing from no numbers.
