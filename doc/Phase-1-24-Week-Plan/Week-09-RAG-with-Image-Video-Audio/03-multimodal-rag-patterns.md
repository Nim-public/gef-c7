# 03 — Multimodal RAG: Patterns & Real-World Examples

> Week 9 index: [README.md](README.md)

**Session 2 topics:** *Real-World Multimodal RAGs with LanceDB. Review of Traditional RAG. Multimodal RAGs and real world examples. Performance and Complexity Tradeoffs.*

---

## What you'll learn

- Traditional RAG, reviewed as a *specification* your multimodal system must still satisfy
- The four multimodal RAG patterns — and exactly what each trades away
- Real-world example systems mapped to patterns
- The performance/complexity table you'll defend at the capstone review

## 1. Traditional RAG, reviewed (W4-01 in one table)

The Week 4 contract doesn't change with modality:

| Contract item | Text RAG (W4) | Multimodal RAG (W9) |
|---|---|---|
| ingestion: parse → chunk → **embed** → index | PDF/HTML → prose chunks | images/audio/video → captions/frames/transcripts + embeddings |
| retrieval: embed query → top-k (+ filter, W5) | text↔text cosine | text↔image, text↔audio, or cross-modal |
| generation: grounded prompt, cite, refuse when insufficient (W4-01) | context = text chunks | context = text **and/or images/audio refs** |
| evaluation: hit rate, Ragas, citations (W5-05) | same | same harness, multimodal cases |

Keep the guardrails too: W3-02 injection discipline (images can carry text attacks — "prompt printed on a T-shirt" is a real vector), W5-04's input/output guards, prefiltered permissions (W5-03).

## 2. The four patterns

### Pattern 1 — Caption-then-index (translate to text)

Media → **captions/transcripts** (BLIP, Whisper — W2) → embed the text → *your Week 4 pipeline, unchanged*.

- ✅ cheapest to build; reuses everything; captions make text-LLM answers possible without VLM serving
- ❌ caption is a lossy bottleneck (layout, colors, counts, charts); captioning cost at ingest; caption hallucinations become corpus facts
- **Best when**: media volume is large, budget small, questions are "aboutness" rather than fine detail

### Pattern 2 — Unified embedding space (CLIP-style)

Embed media into a joint space (CLIP image encoder) alongside text; query by text *or* by image (W8-04, W9-02's two columns).

- ✅ direct cross-modal retrieval; no captioning cost; image-as-query support; fast ANN (W9-02)
- ❌ coarse granularity (whole-image embeddings); CLIP's weaknesses (counting, negation, fine detail, W8-04); still needs an LLM for answers
- **Best when**: similarity/search is the product ("find like this")

### Pattern 3 — True multimodal generation (retrieve media → VLM answers)

Retrieve by any of the above, then hand the *actual images* (plus text) to a vision-language model for the answer:

```
retrieve (text+image hybrid, W9-02) → top-k: 3 chunks + 2 images
      → prompt: question + text blocks + image refs → VLM → grounded, cited answer
```

- ✅ answers questions about *visual content itself* ("what color is the keyboard in the photo?"); citations can point at images
- ❌ VLM cost/latency per query; prompt budget consumed by image tokens; strongest injection surface (text inside images)
- **Best when**: visual detail is the question — quality-critical assistants

### Pattern 4 — Specialized extensions (awareness level)

- **ColBERT-style late interaction / multi-vector** per image region — precision reranking
- **Frame-level video RAG**: keyframe sampling (W7-02) + ASR transcript, both indexed; temporal metadata for "at 3:20 he says…"
- **Table-aware document RAG**: chart/table regions as separate chunks with their own serialization (W7 file 02's content-aware rules)

## 3. Real-world examples (pattern-mapped)

| System | Pattern | Why it fits |
|---|---|---|
| E-commerce "search by photo" | 2 (+1 for descriptions) | similarity *is* the query |
| Slide-deck assistant ("which slide had the churn chart?") | 1 + 2 hybrid | captions+layout text, CLIP for figure queries |
| Meeting-video archive ("what did we decide about pricing?") | 1 (ASR) + 4 (frame refs for citations) | transcript dominates; timestamps cite |
| Medical/imaging reference assistants | 3 | the *pixels* are the knowledge; strict grounding |
| Support ticket with screenshots | 1 + 3 | OCR/captions for routing, VLM for "as shown in your screenshot" |

## 4. Performance & complexity trade-offs (the decision table)

| | P1 caption-then-index | P2 joint embeddings | P3 VLM generation |
|---|---|---|---|
| ingest cost | caption pass (LLM/B model) | one embed pass | caption pass (usually) |
| query cost | 1 embed + LLM | 1–2 embeds + LLM | embeds + **VLM** (5–30× LLM cost) |
| p95 latency | ~1.5–3 s | ~1–2 s | 4–10 s |
| answers fine visual detail | weak | weak–med | **strong** |
| image-as-query | no | **yes** | yes (via P2 retrieval) |
| infra complexity | low | med | high (VLM serving, image plumbing) |
| failure modes | caption hallucination → corpus | CLIP blind spots (W8-04) | VLM hallucination, cost spikes |

The capstone synthesis (and the honest answer mentors look for): **layer them** — P1 always (cheap coverage), P2 for search-by-example, P3 for the high-value "look at this image" questions, routed by question type (the W6-04 router grows a third arm).

## Exercises

1. Run the same 10 questions through P1 (captions) and P2 (CLIP joint) on your corpus; tabulate which questions each answers. Build the routing rule from the differences.
2. Caption cost model: BLIP-base on your 1,000 images — time it; project to your corpus size. Is ingest cost a blocker for P1?
3. VLM cost model (P3): estimate image-token counts for 2 images/query (check your provider's vision pricing) vs text-only. At what query volume does P3 need its own budget line?
4. Failure probe: a chart image with numbers — ask the value via P1 (caption) vs P3 (VLM). Which is right? (This is the classic P1 weakness, made vivid.)
5. Design doc: draw your capstone's multimodal RAG as a pipeline diagram (W4-01 style) with the pattern(s) chosen and the router condition — file 04 turns this into code.

## Pitfalls

- **Pattern faith** — "we use multimodal RAG" without naming the pattern hides the trade-offs; name them
- **Caption-then-index with stale captions** — model upgraded → captions changed → index inconsistent (W7-02 versioning rule)
- **P3 without budget guards** — one viral image query = bill shock; caps per session (W5-04 rate guards)
- **Images in prompts without dedup** — same screenshot attached twice = double token cost, zero info
- **Forgetting text-attacks-in-images** — run W3-02's injection battery with images containing instruction text

## Resources

- Chen et al., *Multimodal RAG survey* (arXiv 2404.08755-family) — the taxonomy behind this file
- LLaVA (Liu et al., 2023) — the VLM answering pattern, §1–3
- LanceDB [multimodal RAG tutorials](https://github.com/lancedb/vectordb-recipes) — P1–P3 worked examples with LanceDB
- Anthropic/OpenAI vision docs — image token pricing models for the §4 cost math
