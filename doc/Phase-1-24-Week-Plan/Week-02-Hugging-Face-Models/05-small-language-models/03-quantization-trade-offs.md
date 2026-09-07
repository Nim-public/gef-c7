# 05.3 — Quantization Trade-offs

> Subfolder index: [README.md](README.md) · Parent: [../05-small-language-models.md](../05-small-language-models.md)

---

## What you'll learn

- The quant formats: GGUF K-quants vs bitsandbytes NF4 vs FP8 — what each does
- The quality measurement protocol (your eval, per quant)
- The memory/quality/latency trade-off table, filled with your numbers

## 1. The formats

| Format | Bits/weight | Mechanism | Where |
|---|---|---|---|
| **GGUF Q8_0** | 8 | block-wise scale+min | llama.cpp/Ollama |
| **GGUF Q4_K_M** | ~4.5 | K-quant blocks, mixed precision per layer | llama.cpp/Ollama |
| **GGUF IQ2/IQ3** | 2–3 | importance-matrix quants | very small RAM |
| **bitsandbytes NF4** | 4 | normal-float quantization | transformers/PEFT (QLoRA) |
| **AWQ** | 4 | activation-aware, per-channel | vLLM serving |
| **GPTQ** | 4 | second-order optimized | vLLM/exllama |
| **FP8** | 8 | hardware-native | H100-class GPUs (W15-03) |

The K-quant insight: not all layers are equal — Q4_K_M keeps attention and embeddings at higher precision while compressing FFN blocks. The `_M` (mixed) variants spend bits where they matter.

## 2. The quality measurement (your eval, per quant)

```python
# same eval set, same prompts, one variable: the quant
QUANTS = ["fp16", "Q8_0", "Q6_K", "Q4_K_M", "Q3_K_M"]
# run your 40-case harness (W2-06) per quant via Ollama/vLLM
# report: accuracy, tokens/s, memory, file size — the full table
```

Expected pattern (measured across the community): Q8 ≈ fp16 (±0.5%); Q4_K_M ≈ −1–3% on hard tasks; Q3+ visibly degrades on reasoning. **The trap:** quality loss is *non-uniform* — reasoning and rare knowledge degrade first, style and formatting survive longest (W16-02's synthetic-data caveat applies: your eval must include the hard classes).

## 3. The trade-off table (fill with your numbers)

| Quant | File size (7B) | Memory (7B) | Tokens/s | Task accuracy | Verdict |
|---|---|---|---|---|---|
| fp16 | 14 GB | ~16 GB |  |  |  |
| Q8_0 | 7.5 GB | ~9 GB |  |  |  |
| Q4_K_M | 4.4 GB | ~6 GB |  |  |  |
| Q3_K_M | 3.3 GB | ~4.5 GB |  |  |  |

## 4. Choosing (the decision tree)

```
Fits at fp16/Q8 and quality matters most?  → fp16/Q8_0
Tight RAM, quality floor acceptable?       → Q4_K_M (the default)
Extremely tight (3 GB for 7B)?             → IQ3/Q2 — verify heavily (W16-02)
Training adapters (QLoRA)?                 → NF4 bitsandbytes on the base
Serving at scale on GPU?                   → AWQ/FP8 in vLLM (W15-03)
```

## Exercises

1. The table: fill §3 for a 7B model (or 1.5B on CPU) — accuracy on your harness, memory, tokens/s per quant.
2. The degradation map: for Q4_K_M, find *which task classes* degrade (run your eval slices — W16-01's slices, per quant).
3. Layer-precision experiment: llama.cpp `--tensor-type` (or a mixed GGUF) keeping attention in Q8, FFN in Q4 — measure the delta.
4. The break-even: quantization saving vs an API call for the same task — at what usage does Q4_K_M self-hosting win? (W2-05 §4's model with quant numbers.)
5. Write the serving policy: which quant per environment (dev/staging/prod) with the quality evidence attached (W16-01's versioning).

## Pitfalls

- **Evals without the hard classes** — quantization degrades reasoning/rare-knowledge first; your eval must include those slices
- **Comparing quants across different base revisions** — the base model moved between builds; pin everything (W2-01)
- **Memory math ignoring KV cache** — the cache grows with context regardless of weight quant; budget separately (W15-03)
- **One quant for all environments** — dev on Q4 is fine; prod quality gates may need Q6/Q8 — the environment ladder (E8-01) applies
- **Trusting community benchmarks** — different prompts, different tokenizers, different tasks; your harness is the referee

## Resources

- [llama.cpp quantization README](https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md) — the quant types
- [bitsandbytes](https://huggingface.co/docs/bitsandbytes/index) — NF4/FP4 for transformers
- Dettmers et al., *QLoRA* — the 4-bit training paper (file W16-04)
- W15-03 (serving), W2-05 (SLMs), W16-04 (LoRA) — composed here
