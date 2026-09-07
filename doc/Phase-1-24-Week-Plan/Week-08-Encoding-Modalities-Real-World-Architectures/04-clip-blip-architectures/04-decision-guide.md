# Decision Guide — CLIP vs BLIP vs Full VLM per Job

**What you'll learn:** the decision table that ends the "which model"
debate: per capstone job, per cost budget, with the upgrade path written
down *before* you need it.

## 1. The decision table

| Job | Right tool | Wrong tool | Why |
|---|---|---|---|
| index corpus for retrieval | CLIP (or SigLIP) | VLM | one vector/unit, batch-cheap |
| rerank top-K pairs | ITM head (BLIP-style) | LLM look at each | pair-scoring without generation |
| caption missing sidecars | BLIP/LM or VLM | CLIP | CLIP cannot generate |
| answer questions about one image | VLM (LLaVA-class) | CLIP | needs generation + grounding |
| route a query to a modality | CLIP zero-shot | VLM | coarse call, latency-critical |
| OCR-heavy screenshots | dedicated OCR + text index | any VLM | pixel precision beats generation |
| audio content | ASR text + text index | CLAP alone | content lives in words |

The pattern: **CLIP-family for indexing and routing; generation models only
where text must be produced.** Every row's "wrong tool" fails on cost or
capability, not on accuracy vibes.

## 2. Cost model per 1k images (CPU, order-of-magnitude)

| Operation | Model | Cost | Notes |
|---|---|---|---|
| embed for index | CLIP-B/32 | ~2–3 min | once, at ingest |
| rerank top-10 per query | ITM | ~10 ms/query | per query, not per corpus |
| caption | BLIP-base | ~1 s/image | offline, ingest-time |
| VQA (one image, one Q) | LLaVA-7B (GPU) | ~1–3 s | demo-time, not ingest |
| zero-shot route | CLIP-B/32 | ~20 ms | per query |

Two budget rules follow: **generation never runs at query time in your
capstone's retrieval path** (only in answer synthesis), and captioning is
an *ingest-time investment* that buys permanent sidecar text.

## 3. The upgrade path (write it, don't improvise it)

```text
v1 (weeks 7–9):  CLIP-B/32 index + OCR/ASR sidecars + late-fusion RAG
v2 (week 13):    + ITM reranker on top-10 (if rerank eval shows ≥2-point gain)
v3 (stretch):    + VLM answer grounding for image-questions (token budget!:
                 576 tokens/image — see fusion file 04)
```

Each step has a *trigger* (an eval number), not a date. The decision memo
from the Week-08 lab holds all three rows with their triggers — that is how
a capstone avoids both premature VLM integration and permanent FOMO.

## 4. The three questions that pick the tool

1. **Does the output need to be text?** No → CLIP/ITM. Yes → LM/VLM.
2. **Does it run at query time?** Yes → ≤50 ms budget → CLIP. No → anything.
3. **Is the answer about one specific image?** Yes → VLM with that image in
   context. No (corpus question) → retrieval first, VLM second.

## Exercises

1. Apply §4's three questions to five real capstone queries (write them
   down); annotate which tool each routes to; check for any query where two
   tools compete and record the tiebreak.
2. Cost the v1→v2 upgrade: measure ITM rerank latency on your machine for
   K=10; compute the added per-query cost and the R@1 gain from the BLIP
   exercises; write the go/no-go.
3. Token-budget check: for a 4k-context VLM, compute how many retrieved
   images + snippets fit; write your demo's image cap.

## Pitfalls

- Picking VLM for indexing "because it's better" — it is better at *answering*, not indexing; the cost model (§2) is the refutation.
- Routing with CLIP zero-shot on domain jargon — route on *modality*, not content (the content comes from your indexes).
- Upgrade paths without triggers — "add VLM in week 13" is a date; "add VLM when rerank eval shows +2 R@1" is an engineering decision.

## Resources

- Your corpus eval harness (Week 07) — every decision above cites its numbers.
- SigLIP (Zhai et al. 2023) — the drop-in CLIP upgrade worth benchmarking before any VLM move.
