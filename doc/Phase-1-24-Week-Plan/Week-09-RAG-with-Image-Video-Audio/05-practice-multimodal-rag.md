# 05 — Practice: Multimodal RAG over Your Data

> Week 9 index: [README.md](README.md) · **Due: before Week 10 (by 14 Nov — break week 7–8 Nov)**

*(No formal task row in the schedule — this practice build consolidates the multimodal arc and leaves the capstone ready for the agentic phase.)*

---

## 1. Deliverable

```
multimodal-rag/
  ingest.py                # captions + embeddings → LanceDB (multi-vector + FTS)
  retrieve.py              # hybrid retrieval: text_vec + image_vec (+ BM25/RRF fallback)
  answer.py                # grounded text-LLM path + optional VLM path (router)
  app.py                   # Gradio UI: chat + image-search tab (file 01 patterns)
  eval/
    retrieval_eval.jsonl   # 20 text→image + 10 image→image queries
    results.md             # R@k table + latency table + tradeoff notes
  README.md                # architecture diagram, pattern choices, decisions
```

Minimum viable corpus: **≥50 multimodal items** (your capstone's images/audio, or a public set like product photos + descriptions).

## 2. Requirements (graded)

### Ingestion
- [ ] ≥50 items, manifest-driven (W7-01), resumable (file 04 checklist)
- [ ] BLIP captions + contextual headers (W5-01) — spot-checked for hallucination (W8-04)
- [ ] Two vector columns (`text_vec`, `image_vec`) + FTS index (W9-02)

### Retrieval
- [ ] Hybrid query path working (native `query_type="hybrid"` or your W4-04 RRF)
- [ ] Metadata prefilter demoed (category/price/permissions)
- [ ] Image-as-query demoed (pattern 2)

### Generation & safety
- [ ] Grounded text answers with `[id · source]` citations
- [ ] Router: text-only vs needs-VLM (even a rule-based v1, file 04 ex. 2)
- [ ] Injection battery incl. one text-in-image case (file 04 ex. 4)
- [ ] No-answer escape fires when retrieval confidence is low (W4-03 threshold)

### Evaluation
- [ ] R@1/5/10 tables for both query directions (W7-05 metrics)
- [ ] Latency table per stage (file 04 §4) with your measured numbers
- [ ] Ragas run on ≥15 text-path answers (W5-05)

## 3. The README architecture section (answer explicitly)

1. Which **pattern(s)** (file 03: P1/P2/P3) did you implement — and what did you *not* build, with the trade that justified it?
2. **Encoders** (from Week 8's decision note): ids, dims, revisions
3. **Index config**: flat vs IVF-PQ, `nprobe`/`refine_factor` operating point, measured recall
4. **Router rules** and their measured accuracy
5. **Cost per query**: embed + retrieve + generate, and the monthly projection at your capstone's expected volume

## 4. Agent-tool contract (Week 10 seam — write it now)

Define your multimodal RAG as a callable tool; Week 10–14 agents will invoke it:

```python
def search_knowledge(query: str, k: int = 5, filters: dict | None = None,
                     image_path: str | None = None) -> dict:
    """Returns {"hits": [{id, text, source, image_path, score}], "mode": "text|hybrid|image",
                "caveat": "no strong matches" | None}."""
```

Deterministic inputs, structured outputs, explicit caveats — that contract *is* the tool description the agents will read (file W10-03).

## 5. Rubric summary

| Area | Weight |
|---|---|
| Ingestion correctness + resumability | 20% |
| Hybrid retrieval + filters + image-as-query | 25% |
| Grounded generation + router + safety battery | 25% |
| Evaluation tables (retrieval + latency + Ragas) | 20% |
| README decisions (patterns, costs, agent contract) | 10% |

## 6. Stretch (pick one)

- Video: keyframe sampling (W7-02) → per-frame CLIP → temporal metadata ("3:20") in citations
- CLIP ↔ SigLIP backbone swap on your harness (W8-06 stretch) — numbers in the README
- Feedback loop: Gradio 👍/👎 per answer → JSONL → your Ragas eval set grows itself (W5-04's logging habit, now productized)

Bring the eval tables to Office Hours (5 Nov): Week 10 opens the agentic arc, and the first exercise will be wrapping *this* system as an MCP tool — the cleaner your `search_knowledge` contract, the faster that goes.
