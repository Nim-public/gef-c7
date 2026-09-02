# Extension E6 — Advanced Inference & Decoding

> Extensions overview: [../README.md](../README.md)

**Builds on:** W15-03 (serving) · W16-03 (training loop) · W14-01 (structured output)

**Practice build:** [04-practice-decoding-lab.md](04-practice-decoding-lab.md)

---

## Why this extension matters

W15-03 covered serving *engines*; this week covers serving *techniques* that change what generation costs and guarantees: **speculative decoding** (generate 2–3× faster with identical outputs), **grammar-constrained decoding** (Outlines — JSON/schema adherence as a *guarantee*, not a prompt hope), and the **GGUF/local quantization ecosystem** that makes all of it run on modest hardware.

## What you will be able to do after this week

- [ ] Explain speculative decoding (draft/target verification) and measure its speedup
- [ ] Guarantee JSON/regex outputs with grammar-constrained decoding (Outlines)
- [ ] Convert models to GGUF; choose quantization formats (Q4_K_M etc.) knowingly
- [ ] Benchmark constrained vs free decoding: quality, speed, parse-failure rate

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-speculative-decoding.md](01-speculative-decoding.md) | Draft/target verification, acceptance rates | 2–3 h |
| 2 | [02-grammar-constrained-decoding.md](02-grammar-constrained-decoding.md) | Outlines: schema-as-grammar, guaranteed JSON | 2–3 h |
| 3 | [03-gguf-quantization-ecosystem.md](03-gguf-quantization-ecosystem.md) | Conversion, K-quants, llama.cpp, engine comparison | 2–3 h |
| 4 | [04-practice-decoding-lab.md](04-practice-decoding-lab.md) | Constrained-decoding benchmark lab (practice) | 3 h |

## Environment setup

```powershell
pip install outlines transformers accelerate
# optional: ollama (GGUF serving), llama-cpp-python
```

## Self-check before E7

1. Speculative decoding claims identical outputs to target-only decoding — why is that *guaranteed* (what does the target model do with each draft token)?
2. With grammar-constrained decoding, your JSON is always parseable. Name one quality problem it can *still* have.
3. Q4_K_M vs Q8_0: size, expected quality delta, and the model size where you'd choose each.
4. Your agent needs a guaranteed enum output per step. Free decoding with retry vs grammar-constrained — cost/latency/reliability trade?
5. Where in your capstone would speculative decoding help most — long structured answers or short tool-call JSONs? (Derive from the acceptance-rate math.)
