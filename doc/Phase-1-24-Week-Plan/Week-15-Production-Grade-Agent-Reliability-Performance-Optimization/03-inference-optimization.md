# 03 — Inference Optimization: vLLM, Batching, KV Cache

> Week 15 index: [README.md](README.md)

**Session 2 topics:** *Inference engines & knobs: vLLM/SGLang, continuous batching, KV cache.*

---

## What you'll learn

- Why a framework's `pipeline` (W2) can't serve production — and what serving engines fix
- The KV cache: what it is, why it's both the biggest win and the biggest memory consumer
- Continuous batching vs static batching
- vLLM/SGLang: serving your model with an OpenAI-compatible API and the knobs that matter
- Quantization at serving time

## 1. The serving problem

Week 2's `pipeline()` runs one request at a time, re-prefills the whole prompt each call, and leaves the GPU idle between token generations. At production volume (p95 SLA, N concurrent users) that leaves 5–10× throughput on the table. Serving engines fix three things:

| Problem | Engine fix |
|---|---|
| serial requests | **continuous batching** — new requests join mid-batch as others finish |
| re-computing prompt keys/values every call | **KV cache** — attention intermediates kept and reused |
| idle GPU during the sequential decode of others | same batching + **paged KV memory** (vLLM's PagedAttention) |

## 2. KV cache — the concept you must own

Attention (W3-04) computes Q·Kᵀ against *previous* tokens. During generation, previous tokens' keys/values never change — so caches:

```
prefill:  process the whole prompt once → store K,V per layer/token  (compute-heavy, 1 pass)
decode:   each new token attends to the cached K,V → 1 new K,V appended  (memory-heavy per token)
```

Consequences you can now derive:

- **Prompt reuse is cheap to serve** — the same long system prompt across requests hits the cache (prompt caching, file 04)
- **KV memory grows with context × batch** — this is why long-context serving is memory-bound, and why quantizing *weights* (W2-05) isn't enough; KV cache quantization exists too
- **Batching mixes prefill and decode work** — hence the scheduler's importance

## 3. vLLM / SGLang — serving your models

```powershell
pip install vllm          # Linux/CUDA; on Windows use WSL2 or a server
```

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct --max-model-len 8192 --gpu-memory-utilization 0.9
# → OpenAI-compatible server on :8000/v1
```

Your entire capstone client (W1-07) works unchanged — `base_url="http://localhost:8000/v1"` (the W2-05 Ollama pattern, productionized):

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
```

Knobs that matter (and their W3-05/Ollama analogs):

| Knob | Effect |
|---|---|
| `--max-model-len` | context ceiling → KV memory ceiling; set to what you *use* |
| `--gpu-memory-utilization` | KV cache headroom vs other tenants |
| `--max-num-seqs` | concurrent sequences in a batch |
| `--quantization awq/gptq/fp8` | weight compression → more KV room (accuracy check!) |
| `--enable-prefix-caching` | reuse KV across requests sharing a prefix (file 04) |

**SGLang** adds RadixAttention (prefix-tree KV sharing — even better for shared long prompts) and fast structured-output decoding. Rule of thumb: vLLM for broad OpenAI-compatible serving, SGLang when shared prefixes dominate (agents with long stable constitutions — your exact case, file 04).

## 4. Continuous batching — the throughput math

Static batching: a batch of 8 waits for its slowest member. Continuous: the scheduler admits/drops sequences per token step, so a 30-token answer doesn't block a 2000-token one. Practical result (published vLLM numbers, order-of-magnitude): 5–20× throughput vs naive loops at similar p50 latency — with p95 *slightly* higher under saturation (queuing).

Your W10-04/15-01 metrics close the loop: measure tokens/s and p95 before/after — the *same* eval harness, now against a served endpoint instead of a pipeline call.

## 5. Quantization at serving

- **Weights**: AWQ/GPTQ/FP8 — 4–8 bit weights, big memory savings, ~1–3% quality cost (validate on your eval set, W2-05)
- **KV cache**: FP8/e4m3 KV — doubles effective context capacity; near-lossless for most workloads
- The serving-time split from W16's *training-time* LoRA: serving quantization changes weights' *storage*, LoRA changes the *function* — different tools, different risks

## Exercises

1. Serve Qwen2.5-7B (or 1.5B on smaller hardware) with vLLM/WSL or Ollama; benchmark tokens/s and p95 first-token at 1, 4, 16 concurrent clients. Plot.
2. Prefix-cache experiment: same 2k-token system prompt across 20 requests with `--enable-prefix-caching` on/off — measure p95 TTFT (time-to-first-token) delta.
3. Quantization parity: fp16 vs AWQ-4bit on your 25-question eval (W4-05 harness) — score both, report the delta and the memory delta.
4. `max-model-len` right-sizing: profile your actual prompt+output token p99 (W10-05's accounting) and set the smallest safe value; compare KV memory headroom.
5. Burst test: 50 concurrent short requests — measure throughput and p95; identify the scheduler knob that moves each.

## Pitfalls

- **vLLM on Windows** — no native support; WSL2/Docker/Linux, or Ollama (which is itself a serving engine, just less tunable)
- **`--max-model-len` at max** — KV cache sized to the ceiling whether used or not; right-size (ex. 4)
- **Quantizing without re-evaluating** — 4-bit is usually fine; "usually" is not a deployment argument (W2-05)
- **Ignoring `Retry-After` at the new layer** — the serving engine has its own limits; the W15-01 client retries still apply
- **Benchmarking with different request mixes** — throughput depends on prompt/output length distribution; freeze the mix when comparing engines

## Resources

- [vLLM docs](https://docs.vllm.ai/) — serving, PagedAttention paper link, quantization guides
- [SGLang docs](https://docs.sglang.ai/) — RadixAttention (prefix sharing) + structured output speedups
- Kwon et al., *Efficient Memory Management for LLM Serving with PagedAttention* — the vLLM paper (§1–3)
- W2-05 (quantization), W3-03 (attention math), W11-05 (traces) — the foundations measured here
