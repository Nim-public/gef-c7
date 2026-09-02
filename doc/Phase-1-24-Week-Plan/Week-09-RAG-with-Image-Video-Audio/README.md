# Week 9 — RAG with Image/Video/Audio

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 31 Oct, 7–10 PM IST (Session 1) · Sun 1 Nov, 7–10 PM IST (Session 2) · Office Hours Thu 5 Nov, 7–8 PM IST

**Practice build:** [05-practice-multimodal-rag.md](05-practice-multimodal-rag.md)

---

## Why this week matters

Three weeks of groundwork pay off here: Week 7's aligned multimodal data + Week 8's chosen encoders become a working **multimodal RAG** — images, audio, and video entering the same retrieval system as your text, wrapped in a Gradio app deployable as a demo. This is also the last week before the agentic arc (Weeks 10–14), so your multimodal RAG becomes a *tool* the future agents can call.

## What you will be able to do after this week

- [ ] Build and deploy Gradio apps: image generation, product cataloging, RAG chat
- [ ] Use LanceDB's multimodal features: multiple vector columns, IVF-PQ-style compression, native hybrid search
- [ ] Choose among the four multimodal RAG patterns with measured trade-offs
- [ ] Build an end-to-end multimodal RAG: ingest (captions + embeddings) → retrieve (hybrid) → generate (VLM) → cite
- [ ] State the performance/complexity trade-offs (caption cost, VLM cost, latency) for your capstone

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-gradio-multimodal-apps.md](01-gradio-multimodal-apps.md) | Gradio features, food-image generator, product cataloger | 3 h |
| 2 | [02-lancedb-multimodal.md](02-lancedb-multimodal.md) | Multimodal tables, IVF-PQ, native hybrid search | 3 h |
| 3 | [03-multimodal-rag-patterns.md](03-multimodal-rag-patterns.md) | Traditional RAG review; the four multimodal patterns; examples | 2–3 h |
| 4 | [04-end-to-end-multimodal-rag.md](04-end-to-end-multimodal-rag.md) | The full build: ingest → retrieve → generate → cite | 4 h |
| 5 | [05-practice-multimodal-rag.md](05-practice-multimodal-rag.md) | Multimodal RAG over your data (practice) | 4 h |

## Environment setup

```powershell
pip install gradio lancedb transformers sentence-transformers
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install rank_bm25 pandas pillow
```

## Self-check before Week 10

1. Your image corpus is 200k items and queries must return in <100 ms. Which index configuration (flat vs IVF-PQ-ish), and what recall did you measure at that setting?
2. A user asks "find products similar to this photo but under ₹2000" — which retrieval arms run, and who merges?
3. Pattern 1 (caption-then-index) vs pattern 2 (CLIP joint space): what does each *miss* about the other's strength?
4. Where exactly does a VLM sit in your pipeline, and what does it cost per query?
5. If your multimodal RAG were an agent tool (Week 10 preview), what would its input/output contract be?
