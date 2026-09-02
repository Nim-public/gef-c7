# 05 — Practice: GraphRAG over Your Corpus

> E2 index: [README.md](README.md) · **Due: before E3**

*(Practice build — adds the third retrieval brain to your capstone and extends the W16 eval harness to graph questions.)*

---

## 1. Deliverable

```
graphrag/
  extract.py             # entity/relation extraction → graph (file 01)
  communities.py         # community detection + summaries (file 02)
  search_local.py        # entity-anchored retrieval (file 02 §3)
  search_global.py       # map-reduce over summaries (file 02 §2)
  router.py              # 4-arm router: sql | vector | graph_local | graph_global (file 04)
  eval/
    graph_cases.jsonl    # 15 graph-shaped questions
    results.md           # comparison table + failure analysis
  README.md              # decisions, costs, integration
```

Demo: one multi-hop question (graph beats vector, shown side by side), one global-theme question (map-reduce), one fused multi-source answer with unified citations.

## 2. Requirements (graded)

### Graph construction (file 01)
- [ ] ≥50 chunks extracted, schema-guided, with evidence fields verified (≥90% evidence-valid on a 20-edge audit)
- [ ] Entity resolution pass (alias merge) with pre/post node counts
- [ ] All nodes/edges carry `chunks` citations

### GraphRAG (file 02)
- [ ] Communities + summaries generated; summaries constrained to listed entities/relations
- [ ] `search_local` and `search_global` working with citations
- [ ] Incremental re-extraction demonstrated on 5 new chunks

### Router & fusion (file 04)
- [ ] 4-arm router with logged decisions; route accuracy on 30 questions
- [ ] RRF fusion across ≥2 arms on 5 multi-source questions; unified citations validated by `qa_check`

### Evaluation
- [ ] 15 graph-shaped questions (multi-hop ×5, entity-detail ×5, global-theme ×5)
- [ ] Comparison: graph vs vector top-k on the same questions (side-by-side answers)
- [ ] Cost ledger: extraction + summary LLM calls vs per-query costs (file 02 §4)

## 3. Rubric

| Area | Weight |
|---|---|
| Graph construction quality (extraction, resolution, evidence) | 30% |
| GraphRAG modes (local + global) working with citations | 25% |
| Router + fusion integration with the W6/W9/W14 stack | 20% |
| Evaluation (graph cases + comparisons + costs) | 20% |
| README decisions | 5% |

## 4. README decisions (answer explicitly)

1. **Graph value assessment**: what % of your capstone questions are graph-shaped (W18-01's table)? Is the graph worth its ingestion cost?
2. **Schema choices**: entity/relation types, open vs guided extraction, and the extraction hallucination rate you measured
3. **Router placement**: where the graph arm sits in your W14 architecture, and which router level (L1/L2/L3) governs it
4. **Cost verdict**: index-time vs query-time costs (file 02 §4's ledger) and the corpus-size threshold where GraphRAG pays off
5. **E3 bridge**: one long-context question your corpus poses ("summarize all 300 reports" class) — would global graph search or long-context paste serve it better? (E3-03's framework, pre-applied)

## 5. Stretch (pick one)

- Multi-hop visualization: render the graph neighborhood (networkx + matplotlib or pyvis) for a demo answer
- Temporal edges: add `updated` timestamps to relations and answer "as of 2025" questions (W7-01 metadata discipline)
- GraphRAG + reranking: rerank graph-retrieved *chunks* with the W17-04 cross-encoder — does the fused quality improve?

Bring the route-accuracy table to your next mentor session: the four-arm router (W14 verdict + graph arm) is the capstone's final retrieval architecture candidate — this table is the evidence for the freeze.
