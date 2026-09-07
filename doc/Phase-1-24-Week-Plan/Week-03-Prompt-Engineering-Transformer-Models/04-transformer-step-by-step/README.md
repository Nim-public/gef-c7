# 04 — Transformer Step-by-Step: Deep Dive

> Parent topic: [../04-transformer-step-by-step.md](../04-transformer-step-by-step.md) · Week 3 index: [../README.md](../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-embeddings-and-attention-by-hand.md](01-embeddings-and-attention-by-hand.md) | Q/K/V on 4 tokens, computed by hand | 4 h |
| 2 | [02-the-attention-function.md](02-the-attention-function.md) | The ~15-line implementation, causal masking | 3 h |
| 3 | [03-the-transformer-block.md](03-the-transformer-block.md) | Multi-head, FFN, residuals, the full block | 3 h |
| 4 | [04-tracing-a-real-model.md](04-tracing-a-real-model.md) | Qwen internals: shapes, counts, reconciliation | 2 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — the attention computation on a 4-token sentence, every number derived
- **02** — the runnable attention function with masking; the Q=K ablations
- **03** — from attention to the full block: multi-head, FFN, residuals, layer norm
- **04** — reading Qwen2.5-0.5B's architecture print and reconciling its parameters
- **exercises.md** — labs including the ablations and the prediction-probe
