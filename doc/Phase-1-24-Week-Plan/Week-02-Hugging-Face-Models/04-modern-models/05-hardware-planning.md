# 04.5 — Hardware Planning

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

---

## What you'll learn

- The memory math for every model class you've touched
- The tier-routing table: what runs where
- Cost modeling across tiers (the E8-03 forecast, hardware edition)

## 1. The memory math (every model, one formula)

```
weights_gb ≈ params × bytes_per_param
fp32: ×4   fp16/bf16: ×2   int8: ×1   4-bit: ×0.5
+ KV cache (generation): context × layers × 2 × hidden × bytes   ← grows per token
+ activations/overhead: ~20–30%
```

| Model | Params | fp16 GB | int8 GB | 4-bit GB |
|---|---|---|---|---|
| DistilBERT | 66M | 0.13 | 0.07 | — |
| MiniLM | 22M | 0.04 | 0.02 | — |
| Qwen2.5-0.5B | 494M | 1.0 | 0.5 | 0.3 |
| Qwen2.5-7B | 7.6B | 15 | 7.6 | 4.5 |
| SD 1.5 | ~1B | 2.5 | 1.2 | 0.8 |
| Whisper-medium | 769M | 1.5 | 0.8 | 0.5 |

Plus the **KV cache** at generation time: `context_tokens × layers × 2 × hidden × bytes_per_kv` — the reason long contexts are memory-bound (W15-03's serving math, model-agnostic).

## 2. The tier-routing table (your stack, complete)

| Workload | Tier | Your stack |
|---|---|---|
| embeddings, encoders, rerankers | CPU, any laptop | sentence-transformers (W5-02) |
| sentiment/NER classification | CPU, any laptop | pipelines (W2-02) |
| summarization/QA/translation | CPU or small GPU | BART/opus pipelines (W2-03) |
| 0.5–1B generation | laptop CPU/GPU | pipeline/Ollama (W2-05) |
| 7B generation | workstation GPU / API | vLLM/Ollama (W15-03) |
| diffusion images | GPU preferred | diffusers (W2-04) |
| Whisper large | GPU or batch offline | pipeline (file 02) |

The routing principle (W15-04): the *task* picks the model class; the *hardware* picks the size; the *router* sends each request to the right tier.

## 3. Cost modeling across tiers

| Tier | Fixed cost | Marginal cost/1k queries | Notes |
|---|---|---|---|
| CPU laptop (yours) | sunk | ~0 | no concurrency |
| CPU server | ~$30/mo | ~0 | concurrency limited |
| GPU server (T4) | ~$300/mo | ~0 | batching helps (W15-03) |
| API (4o-mini) | none | ~$0.15/1k | scales infinitely |
| API (4o) | none | ~$2.50/1k | quality ceiling |

Break-even (E8-03's forecast): at 1M queries/day, API = ~$150–2,500/day vs a $300/mo GPU server — hardware pays for itself in days *if utilization is high*. Under 10k/day, the API is cheaper than the electricity.

## 4. The sizing worksheet (per deployment)

```markdown
## Deployment sizing — <feature>
- Model: <id> (<params>, <precision>)
- Weights: <X GB>   KV cache @ <context>: <Y GB>   Overhead: <Z GB>
- Total VRAM/RAM: <T GB>  → hardware tier: <tier>
- Expected concurrency: <N> → memory × N (batched KV)
- Throughput target: <tokens/s>  → measured: <actual>
- Marginal cost/query: <$>
```

## Exercises

1. Memory audit: for each model in your capstone stack (W2–W14), compute the fp16/int8/4-bit memory — one table, verify one row empirically with `psutil`.
2. Concurrency test: run your classifier at 1/4/16 concurrent requests (threads) — throughput and p95 latency; find the saturation point.
3. KV-cache sizing: for Qwen2.5-0.5B at 4k context, compute the KV bytes per the formula; measure actual with `torch.cuda.max_memory_allocated` (or RAM) — reconcile.
4. Tier cost model: your capstone's traffic mix → cheapest hardware plan meeting the SLA; write it as the deployment budget line (E8-03).
5. The routing table final: complete the W15-04 routing table with hardware tiers per model — the deployment section of your capstone README.

## Pitfalls

- **fp16 on CPU** — unsupported/slow; fp32 or GPU (W2-04's recurring note)
- **KV cache forgotten at high context** — the cache grows per concurrent sequence; batched long-context serving multiplies it
- **Ignoring activation memory during training** — training needs weights + grads + optimizer + activations (W3-03); inference needs much less
- **One tier for all traffic** — the router (W15-04) exists because the mix is heterogeneous; route by task class
- **Sizing from the model card alone** — the card says weights; the deployment adds KV + runtime overhead — measure (file 01's audit discipline)

## Resources

- W15-03 (serving math), W2-04/05 (model tiers), W16-03/04 (training memory) — composed here
- [vLLM throughput docs](https://docs.vllm.ai/) — the measured throughput references
- [MLA/quantization guides](https://huggingface.co/docs/transformers/quantization) — the compression options
