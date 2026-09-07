# Deep-Dive: Inference Optimization

Parent overview: [`../03-inference-optimization.md`](../03-inference-optimization.md)

Serving-side optimization: KV cache memory math, continuous batching
throughput mechanics, vLLM/SGLang serving knobs, and quantization
trade-offs (AWQ/FP8). Self-hosting knowledge that also explains what
your *hosted* provider is doing under the hood.

## File map

| File | What it covers |
|---|---|
| [`01-kv-cache.md`](01-kv-cache.md) | Prefill/decode memory math |
| [`02-continuous-batching.md`](02-continuous-batching.md) | Throughput mechanics |
| [`03-vllm-serving.md`](03-vllm-serving.md) | Knobs and benchmarks |
| [`04-quantization.md`](04-quantization.md) | AWQ/FP8 trade-offs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-kv-cache.md` — the memory math every serving decision rests on.
2. `02-continuous-batching.md` — why batching changes everything.
3. `03-vllm-serving.md` — the knobs you will tune.
4. `04-quantization.md` — memory vs quality, quantified.

## Prerequisites

- [`../../Week-08-Encoding-Modalities-Real-World-Architectures/01-encoding-text-images/03-vit-patch-tokens.md`](../../Week-08-Encoding-Modalities-Real-World-Architectures/01-encoding-text-images/03-vit-patch-tokens.md)
  — the token math.
- [`../../Week-13-Building-AI-Agents-with-LangGraph/01-langgraph-foundations/`](../../Week-13-Building-AI-Agents-with-LangGraph/01-langgraph-foundations/)
  — the loop whose serving costs this explains.