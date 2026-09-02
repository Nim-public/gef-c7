# 05 — Small Language Models (SLMs)

> Week 2 index: [README.md](README.md)

**Session 2 topic:** *Small Language Models.*

---

## What you'll learn

- What qualifies as an SLM and why the program trains you to default to them
- The current small-model landscape and how to choose
- Running SLMs locally: transformers, and the Ollama/LM Studio option
- When SLM wins vs API — a decision table you'll reuse in the capstone

## 1. What is an SLM?

No hard boundary — practically: **≤ ~4B parameters, runnable on a laptop or a single small GPU.**

| Class | Params | Runs on | Examples |
|---|---|---|---|
| Tiny | 0.1–0.5B | any laptop CPU | SmolLM2-360M, Qwen2.5-0.5B |
| Small | 1–4B | laptop CPU/GPU, phones | Llama-3.2-1B/3B, Phi-3.5-mini, Gemma-2-2b, Qwen2.5-1.5B/3B |
| Mid | 7–14B | workstation GPU | Llama-3.1-8B, Qwen2.5-7B |
| Frontier | 70B+ / API | datacenter / cloud | GPT-class, Claude-class |

**Why the program pushes SLMs:**

1. **Cost** — self-hosted CPU inference is free; tokens cost $0
2. **Latency** — no network round-trip; 10–50 ms first-token locally
3. **Privacy** — data never leaves your machine (capstone with company data)
4. **Determinism/uptime** — no rate limits, no provider outages, no silent model updates
5. **Education** — you can fine-tune, quantize, and *inspect* them (Weeks 16+)

Frontier models still win on raw capability — the skill is picking the *smallest model that passes your eval*, not the biggest model that fits your ego.

## 2. The landscape (check the Hub for current leaders)

- **Qwen2.5** (Apache-2.0): 0.5B/1.5B/3B/7B… — strong multilingual + coding
- **Llama 3.2** (Llama license): 1B/3B — the ecosystem default
- **Phi-3.5-mini** (MIT): 3.8B — punchy reasoning per param, textbook-trained
- **Gemma 2** (gated): 2B/9B — solid, good HF integration
- **SmolLM2** (Apache-2.0): 135M/360M/1.7B — pure open source, great for tinkering

Choosing checklist (same as file 01, plus): benchmark *on your task* (MMLU ≠ your domain), context window (SLMs: 4k–128k), and community tooling (fine-tuning recipes exist for Llama/Qwen families).

## 3. Running them locally

### Transformers (what you already know)

```python
from transformers import pipeline

pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-1.7B-Instruct")
print(pipe([{"role": "user", "content": "Define RAG in one sentence."}],
           max_new_tokens=60)[0]["generated_text"][-1]["content"])
```

### Ollama — the 5-minute local server

Download from [ollama.com](https://ollama.com), then:

```powershell
ollama pull llama3.2:1b
ollama run llama3.2:1b "Define RAG in one sentence."
```

OpenAI-compatible endpoint at `http://localhost:11434/v1` — so **your Week 1 API code works unchanged**:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
print(client.chat.completions.create(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "Define RAG in one sentence."}],
).choices[0].message.content)
```

This endpoint-compatibility is why good applications are written **model-agnostic**: local SLM for dev, API for prod — same code path. (LM Studio is the GUI alternative with a model browser.)

### Quantization in one paragraph

Weights stored at 4-bit instead of 16-bit shrink 4× with small quality loss — a 4B model in ~2.5 GB runs where the fp16 version can't. You'll meet the machinery (GGUF, bitsandbytes) in Week 16's fine-tuning unit; for now, know that Ollama's default pulls are quantized GGUFs, which is *why they're small*.

## 4. SLM vs API — the decision table

| Situation | Pick |
|---|---|
| High-volume simple tasks (classify, extract, route) | **SLM/local** |
| PII or confidential data (no egress allowed) | **SLM/local** |
| Offline/edge deployment | **SLM/local** |
| Prototype on a laptop tonight | **SLM/local** |
| Complex multi-step reasoning, long context | API |
| Need best-possible quality for a demo | API |
| Unknown edge cases in user input | API (or SLM + confidence fallback, Week 11's human-in-the-loop) |

Production pattern you'll build in the capstone: **SLM first, escalate to API when confidence is low** (logprobs from file W1-07 give you the confidence signal).

## Exercises

1. Run the same 10-question mini-eval (5 factual, 3 summarization, 2 classification prompts) on `SmolLM2-360M-Instruct`, `Qwen2.5-0.5B-Instruct`, and an API model. Score pass/fail. Where's the cliff?
2. Latency: time first-token for Ollama-1B vs API (median of 10). Include network vs no-network in your reasoning.
3. Privacy test: take one synthetic PII ticket, run it through the local model only; write the data-handling note for your capstone scope doc (Week 1 file 08).
4. Cost model: 1M classifications/day at 300 tokens each — price API vs an idle 4-core server. When does hardware pay for itself?
5. Swap the model behind your Week 2 Gradio demo (file 02) from a pipeline to the Ollama endpoint. What changed in the code? (Answer: almost nothing — that's the point.)

## Pitfalls

- **Benchmark tourism** — a model that tops MMLU may be terrible at your ticket-routing task; always eval on your data
- **RAM underestimation** — model + KV cache + activations; leave 30% headroom
- **Assuming quantization is free** — 4-bit costs 1–3% accuracy typically; validate
- **Local ≠ free in time** — you're now the ops team: model updates, disk, uptime
- **Hard-coding provider SDKs** — keep the OpenAI-compatible abstraction so swapping models is a config change

## Resources

- [Ollama library](https://ollama.com/library) — browsable local models
- HF [SmolLM2 blog](https://huggingface.co/blog/smollm2) — training small models well
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) + task-specific leaderboards
- [llama.cpp](https://github.com/ggerganov/llama.cpp) — the inference engine under most local tools
