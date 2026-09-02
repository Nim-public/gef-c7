# 03 — The GGUF/Quantization Ecosystem

> E6 index: [README.md](README.md)

**Core topics:** *GGUF conversion, K-quants, llama.cpp/Ollama serving, engine comparison (llama.cpp vs vLLM vs TGI vs TensorRT-LLM).*

---

## What you'll learn

- The GGUF format and the quantization alphabet (Q4_K_M, Q5_K_S, IQ…) decoded
- Converting/serving models locally: llama.cpp and Ollama
- Engine selection: llama.cpp vs vLLM (W15-03) vs TGI vs TensorRT-LLM
- A quality-vs-size measurement protocol (the W2-05 discipline, ecosystem edition)

## 1. GGUF — the local-serving format

GGUF (successor of GGML) is llama.cpp's single-file model format: weights + tokenizer + metadata in one file, quantized for CPU/mixed inference. Ollama's models *are* GGUFs.

```bash
# convert a HF model to GGUF (llama.cpp tooling)
python convert_hf_to_gguf.py Qwen2.5-0.5B-Instruct/ --outfile qwen05-f16.gguf
# quantize
llama-quantize qwen05-f16.gguf qwen05-Q4_K_M.gguf Q4_K_M
# serve
llama-server -m qwen05-Q4_K_M.gguf --port 8080       # OpenAI-compatible API
```

### The quantization alphabet, decoded

| Tag | Meaning | Size (7B) | Notes |
|---|---|---|---|
| Q8_0 | 8-bit | ~7.5 GB | near-lossless |
| **Q6_K** | 6-bit super-block | ~5.5 GB | sweet spot for quality/size |
| **Q4_K_M** | 4-bit mixed (important layers higher) | ~4.4 GB | the community default |
| Q4_0 | legacy 4-bit | ~4 GB | superseded by K-quants |
| IQ4_XS / IQ2_* | importance-matrix quants | 3–4 GB | newer, better at very low bits |
| F16 | none | ~14 GB | reference |

Selection rule: pick the largest quant that fits your RAM with ~1 GB headroom (context + buffers, W15-03's KV math); drop only after measuring quality on *your* eval (W2-05's rule, ecosystem edition).

## 2. llama.cpp and Ollama

- **llama.cpp**: the inference engine — CPU + GPU offload (`-ngl` layers), GGUF, OpenAI-compatible server (`llama-server`)
- **Ollama**: llama.cpp + model management + OpenAI-compatible API (W2-05) — the friendly wrapper; `ollama run qwen2.5:7b-instruct-q4_K_M` pulls a specific quant

Key llama.cpp knobs: `-ngl N` (layers to GPU), `--ctx-size` (context → memory), `--parallel N` (concurrent slots), `--flash-attn`. The memory budget = weights + KV (W15-03's math, GGUF edition).

## 3. Engine selection (the 2026 map)

| Engine | Best at | Hardware | API |
|---|---|---|---|
| **llama.cpp / Ollama** | local, CPU+mixed, laptops | any | OpenAI-compatible |
| **vLLM** (W15-03) | GPU throughput, continuous batching | CUDA | OpenAI-compatible |
| **SGLang** (W15-03) | shared prefixes, structured output speed | CUDA | OpenAI-compatible |
| **TGI** | HF-native serving | CUDA | own + OpenAI-ish |
| **TensorRT-LLM** | max NVIDIA throughput, compiled engines | NVIDIA | custom |
| **MLX** | Apple Silicon | M-series | python |

Decision rule: laptop/personal → llama.cpp/Ollama; production GPU serving with batching → vLLM/SGLang; Apple-only → MLX; NVIDIA-max → TensorRT-LLM. Your W15-04 router can front *any* of them — they all speak OpenAI-compatible dialects (the W2-05 portability argument, now across serving engines).

## 4. Quality measurement protocol (the discipline)

1. **Same prompts, same decoding** across quants (W15-03's freeze rule)
2. **Perplexity is not enough** — measure on *your* task eval (W4-05 harness / W11-06 cases) + a general-parity battery (W16-04's parity discipline)
3. **Report**: accuracy delta, tokens/s, memory, file size — the W2-05 table, per quant
4. **Perplexity spikes on specific inputs** (long code, rare tokens) — Q2/Q3 quants fail unevenly; sample-audit outputs (W12-04's spot-check)

## Exercises

1. Convert Qwen2.5-0.5B to F16 → Q8_0 → Q4_K_M; run your 25-question harness on each. Table: accuracy, size, tokens/s.
2. Context memory drill: llama-server at `--ctx-size` 2k vs 16k — measure RAM/GPU delta (W15-03's KV math, verified).
3. Engine A/B: same model via llama.cpp and vLLM (or Ollama) — tokens/s and p95 at 4 concurrency. Which engine for which traffic?
4. Perplexity vs task: report both perplexity and task accuracy for Q4_K_M — do they agree? (Where they disagree is why task evals rule.)
5. Write the serving matrix for your capstone: model × quant × engine per environment (dev laptop / CI / prod GPU), with the memory budget per row.

## Pitfalls

- **Q2/Q3 "it fits!" trap** — sub-3-bit quants degrade unevenly and fail unpredictably on domain text; measure per domain (W5-02's lesson)
- **Conversion-tool version drift** — llama.cpp's converter changes; record the tool commit with the artifact (W16-01 versioning)
- **Context size in Ollama defaults** — some defaults truncate context silently; set `num_ctx` explicitly (W4-02's truncation lesson)
- **CPU-only expectations** — tokens/s on CPU is single-digit; plan hardware for anything interactive (W15-04's routing table)
- **Forgetting the tokenizer in the artifact** — a weights file without its tokenizer/config is unrunnable; ship the full set

## Resources

- [llama.cpp](https://github.com/ggerganov/llama.cpp) — build, convert, quantize, server docs
- [GGML origin paper](https://arxiv.org/abs/2210.17323) + community quantization PRs — the quant math
- W15-03 (serving), W2-05 (quantization/SLMs), W15-04 (routing) — composed here
- Ollama [import docs](https://github.com/ollama/ollama/blob/main/docs/import.md) — custom GGUFs into Ollama
