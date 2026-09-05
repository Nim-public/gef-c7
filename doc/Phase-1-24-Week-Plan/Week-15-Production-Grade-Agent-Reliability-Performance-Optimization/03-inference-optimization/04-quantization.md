# Serving Quantization — AWQ/FP8 Trade-offs

**What you'll learn:** weight and KV quantization: AWQ (4-bit
weight-only) and FP8 (weights + KV) — the memory savings, the quality
cost, and the decision procedure.

## 1. The two families

| Scheme | What's quantized | Memory saving | Quality cost |
|---|---|---|---|
| AWQ (4-bit weight-only) | weights | ~3.5× vs fp16 weights | small, task-dependent |
| FP8 (e4m3) | weights + KV cache | ~2× (weights and KV) | small; KV in fp8 halves memory |
| GPTQ | weights (legacy) | ~3.5× | slightly worse than AWQ typically |

```python
llm = LLM(model="...-awq", quantization="awq")           # weight-only
llm = LLM(model="...", quantization="fp8", kv_cache_dtype="fp8")  # + KV
```

The memory math (file 01) prices both: AWQ shrinks the *weights*
footprint (more room for KV → bigger batches); FP8 also halves the
*KV* cache (double the sequences at the same context).

## 2. The quality measurement (the honest half)

| Test | Method | Pass bar |
|---|---|---|
| perplexity drift | wiki-text PPL, fp16 vs quantized | <3% |
| your eval set | the 15-case exact-match | no regression >1 case |
| retrieval spot-check | the parity queries | same top-1 on ≥4/5 |
| long-context probe | a 16k needle-in-haystack | found |

The quality cost is measured on *your* tasks — perplexity is the
sanity check; the eval set is the decision. AWQ on a 7B model usually
passes all four; FP8 KV rarely shows on short contexts and shows
occasionally on very long ones (the needle test is the sentinel).

## 3. The decision procedure

1. **Does it fit in fp16?** Yes → fp16 unless batching needs the room.
2. **Do you need bigger batches or longer context?** Yes → AWQ weights
   first (cheapest quality cost).
3. **Is KV the binding constraint?** Yes → FP8 KV (measure the needle
   test).
4. **Never quantize blind** — the four tests run before and after; the
   eval set's verdict is the decision.

| Setup | 24 GB card, 7B model | Sequences @ 4k |
|---|---|---|
| fp16 weights | ~14 GB weights | ~35 |
| AWQ weights (~4 GB) | ~4 GB weights | ~70 |
| AWQ + FP8 KV | ~4 GB + half KV | ~110 |

## Exercises

1. Compute §3's table for your card and model; fill in the sequences
   column from the KV formula.
2. Quality drill: run the four tests fp16 vs AWQ on your eval set; the
   regression (if any) is the cost.
3. FP8-KV drill: enable FP8 KV; rerun the long-context needle probe;
   the sentinel result is the KV decision.

## Pitfalls

- Quantizing without the quality tests — a silent regression on *your*
  tasks is the failure; perplexity alone is not the verdict.
- Comparing quantized throughput against fp16 *without* equal batch
  sizes — the memory savings exist to raise batch size; compare at the
  same served load.
- AWQ on a model with no prebuilt checkpoint — calibrating your own is
  a project; prefer prebuilt for the capstone.