# KV Cache — Prefill and Decode Memory Math

**What you'll learn:** the KV cache memory formula — the number every
serving decision (batch size, context length, quantization) rests on —
computed by hand for models you actually use.

## 1. The formula

```text
KV bytes = 2 (K and V) × layers × kv_heads × head_dim × tokens
           × bytes_per_element × batch_size
```

For a model with grouped-query attention (GQA), `kv_heads` is *not* the
full attention-head count — it is the smaller KV-head count (e.g.,
Llama-3-8B: 32 query heads, 8 KV heads).

```python
def kv_bytes(layers: int, kv_heads: int, head_dim: int, tokens: int,
             bytes_per_el: int = 2, batch: int = 1) -> int:
    return 2 * layers * kv_heads * head_dim * tokens * bytes_per_el * batch

# Llama-3-8B: 32 layers, 8 kv_heads, 128 head_dim, fp16
print(kv_bytes(32, 8, 128, 4096))            # 268 MB per sequence @ 4k ctx
print(kv_bytes(32, 8, 128, 4096, batch=32))  # 8.6 GB for a 32-batch
```

| Model | Layers | KV heads | head_dim | KV @ 4k ctx (fp16) |
|---|---|---|---|---|
| Llama-3-8B | 32 | 8 | 128 | ~268 MB/seq |
| Mistral-7B | 32 | 8 | 128 | ~268 MB/seq |
| Llama-3-70B (GQA-8) | 80 | 8 | 128 | ~671 MB/seq |

## 2. Prefill vs decode

| Phase | What happens | Compute | Memory |
|---|---|---|---|
| prefill | process the whole prompt at once | compute-bound | KV grows to prompt length |
| decode | one token at a time | memory-bandwidth-bound | KV grows +1 token/step |

Two consequences that shape everything: (1) **prefill is
compute-bound** — long prompts cost FLOPs once; (2) **decode is
memory-bandwidth-bound** — every generated token reads the entire KV
cache. This is why batching works (§2): decode is latency-bound per
sequence but throughput-rich across sequences.

## 3. The serving math that follows

| Decision | The KV number that decides |
|---|---|
| max batch size | free VRAM ÷ per-sequence KV |
| max context | free VRAM ÷ (batch × per-token KV) |
| quantize KV to fp8 | doubles sequences (bytes_per_el 2→1) |
| prefix caching | shared prefixes pay their KV once |

```python
def max_batch(free_vram_gb: float, kv_per_seq_gb: float,
              weights_gb: float, overhead_gb: float = 2.0) -> int:
    return int((free_vram_gb - weights_gb - overhead_gb) / kv_per_seq_gb)

print(max_batch(80, 0.268, 16))    # ~230 sequences on an 80GB card
```

## Exercises

1. Compute the KV cache for Llama-3-70B at 32k context, fp16, batch 1;
   then fp8 KV — the halving is the quantization argument.
2. Context-cost drill: from the W12 token math, compute the KV cost of
   your 15-case eval (input + output tokens) on one model — the serving
   bill, derived from first principles.
3. Batch drill: given a 24 GB card with a 7B model (14 GB weights), what
   batch fits at 4k context? Then at 16k? The context/batch trade, in
   numbers.

## Pitfalls

- Using full attention-head count for `kv_heads` on GQA models — 8× the
  real memory; check the config.
- Forgetting batch size in the formula — per-sequence vs total is the
  batch decision's whole point.
- Ignoring prefill when batch-serving — one long prompt delays every
  sequence in its batch (the continuous-batching fix, file 02).