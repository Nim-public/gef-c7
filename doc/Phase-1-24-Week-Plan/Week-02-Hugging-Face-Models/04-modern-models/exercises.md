# Exercises — Modern Models

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

Labs for this subfolder. Shared fixture: 10 capstone-adjacent images, 2 audio clips, and your W11-06 model comparison prompts.

---

## E1 — CLIP failure catalog (file 01)

1. Zero-shot sweep: 10 images × 5 labels — full confusion analysis; classify each error as counting/negation/fine-grained/composition.
2. Ensemble A/B: 1 vs 5 templates on the hardest images — flip rate measured.
3. Region embeddings: crop with W20-01 detection; embed regions — mini region-retrieval demo over 20 images.

**Worked approach:** the failure catalog is the W20-01 routing justification — each failure class names the model that fixes it (detection/OCR/VLM).

## E2 — Whisper production readiness (file 02)

1. Tier benchmark: tiny/base/small on a 5-minute recording — WER vs your transcription + real-time factor; pick the volume tier.
2. Hallucination drill: silence and room-tone tests — fabricated content per configuration; VAD-trim fix verified.
3. Timestamp accuracy: 20 word stamps vs manual marking — the offset distribution that decides E5-01's merge tolerance.

**Worked approach:** exercise 2's fabricated-sentences finding is the scariest — measure it before Whisper outputs enter any corpus (E5-01's VAD rule).

## E3 — Local model comparison (file 03)

1. Size-scaling study: 360M/0.5B/1.7B on your 10 prompts — instruction-following and factual scoring per size.
2. Template audit: 3 families' chat templates rendered and diffed; the structural differences table.
3. Sampling parity: pipeline greedy vs Ollama temperature=0 — output diffs quantified (quantization + template effects).

**Worked approach:** exercise 3's diff analysis is the portability evidence — what survives the serving-path migration and what doesn't (W2-05 §3's table, verified).

## E4 — Diffusion determinism (file 04)

1. Component census: parameter counts per pipeline component; the data-flow diagram annotated with shapes.
2. Guidance×steps grid: 4×4 sweep at fixed seed — the quality map with your annotations.
3. img2img strength curve: composition preservation vs creativity per strength value.

**Worked approach:** exercise 2's grid demonstrates the determinism contract — same seed, reproducible grid; the same discipline W16-01 demands of evals.

## E5 — The deployment sizing pack (file 05)

1. Memory audit table: every model in your capstone stack — params, fp16/int8/4-bit memory, measured vs computed.
2. Concurrency benchmark: your classifier at 1/4/16 concurrent — saturation point found.
3. Tier cost model: your traffic mix → the cheapest SLA-compliant hardware plan; the deployment budget line.

**Worked approach:** exercise 1's table (computed vs measured) is the skill check — if your math is off by 2×, find the missing term (KV cache, overhead) before trusting any other number.

## Self-assessment

- Can you predict, for any model, its memory need at a given precision and context — and verify it?
- Can you name the CLIP failure classes and the model that fixes each?
- Can you state the Whisper hallucination mechanism and its mitigation from memory?
