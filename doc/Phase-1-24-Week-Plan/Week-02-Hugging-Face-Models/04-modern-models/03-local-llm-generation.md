# 04.3 — Local LLM Generation

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

---

## What you'll learn

- Chat templates as the token-level contract (W1-01/W1-07 applied locally)
- Generation controls on local models — and their parity with API models
- Comparing local models systematically (the behavior grid, W8-04 edition)
- The serving-path contrast: pipeline vs Ollama vs API (W2-05's table, deepened)

## 1. Chat templates — the local contract

```python
from transformers import pipeline

llm = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")

messages = [
    {"role": "system", "content": "Answer in one short paragraph."},
    {"role": "user", "content": "Explain vector databases to a DBA."},
]
out = llm(messages, max_new_tokens=120, temperature=0.3)
print(out[0]["generated_text"][-1]["content"])       # last message = the reply
```

The `messages` list is rendered through the model's **chat template** — inspect the raw rendering to see exactly what the model reads:

```python
rendered = llm.tokenizer.apply_chat_template(messages, tokenize=False)
print(rendered)
# <|im_start|>system\nAnswer in one short paragraph.<|im_end|>\n
# <|im_start|>user\nExplain vector databases...<|im_end|>\n
# <|im_start|>assistant\n
```

The template differences between families (Qwen's `<|im_start|>`, Llama's `[INST]`, Mistral's `[INST]/[/INST]`) are why a prompt tuned on one model underperforms on another — the *semantics* of the delimiters were trained per model.

## 2. Generation controls (parity with the API)

| Control | Local | API parity (W1-07) |
|---|---|---|
| `max_new_tokens` | output cap | `max_completion_tokens` |
| `temperature` / `top_p` / `top_k` | sampling | same semantics |
| `repetition_penalty` | penalizes repeats | not exposed (use frequency penalties) |
| `do_sample=False` | greedy | temperature=0 equivalent |
| `stop_strings` | stop sequences | `stop` |

The stop-token detail: generation ends when the model emits its EOS/turn-end token — the pipeline handles it when given `messages`, but raw `tokenizer(text)` prompts keep generating past the turn (base-model behavior, W8-04's grid).

## 3. The comparison lab (local models, same prompts)

```python
CANDIDATES = {
    "smollm2-360m": "HuggingFaceTB/SmolLM2-360M-Instruct",
    "qwen-0.5b": "Qwen/Qwen2.5-0.5B-Instruct",
    "smollm2-1.7b": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
}

for name, mid in CANDIDATES.items():
    pipe = pipeline("text-generation", model=mid)
    out = pipe([{"role": "user", "content": PROMPT}], max_new_tokens=150)
    print(f"=== {name} ===\n{out[0]['generated_text'][-1]['content']}\n")
```

What differs between sizes (the W2-05 behavior grid, on your prompts): instruction adherence, factual accuracy, format compliance, and the coherence of longer outputs. The comparison is the W2-05 §1 table with your own data.

## 4. The serving-path contrast (pipeline vs Ollama vs API)

| Path | Setup | Latency | Throughput | Control |
|---|---|---|---|---|
| `transformers.pipeline` | zero | slow (no batching, no KV mgmt) | 1 request | full (weights visible) |
| **Ollama** (W2-05) | one install | fast | good | quantized GGUFs |
| **vLLM** (W15-03) | GPU server | fastest | best | engine-level tuning |
| **API** | none | network round-trip | provider-managed | none (provider's) |

The pipeline path is for *learning and experiments*; Ollama for personal production; vLLM/API for scale. All three speak the same message format at the application layer (W2-05's endpoint compatibility) — which is why your capstone's abstraction layer matters.

## Exercises

1. Template audit: render the same `messages` through 3 model families' templates — tabulate the structural differences (delimiters, system placement, newlines).
2. Size-scaling study: same 10 prompts through 360M/0.5B/1.7B — score instruction-following and factual accuracy; plot quality vs size.
3. Sampling parity: greedy on pipeline vs `temperature=0` via Ollama — same model, same output? (Quantify any drift — quantization and template differences explain it.)
4. Repetition control: force a long generation with `repetition_penalty` ∈ {1.0, 1.1, 1.2} — find the loop threshold and the quality cost.
5. Serving migration: port one pipeline call to Ollama's OpenAI-compatible endpoint — diff the outputs; document what the portability buys (W2-05 §3).

## Pitfalls

- **max_new_tokens unbounded** — a rambling local model eats RAM and patience; cap everything
- **Base model via pipeline with messages** — the template is ignored on base models (no trained turn tokens); use instruct variants
- **Quantized quality assumptions** — Ollama defaults are 4-bit; the pipeline fp16 output differs (W2-05 §3's trade)
- **`temperature` with `do_sample=False`** — sampling params are ignored in greedy mode; the API parity isn't exact
- **KV-cache memory on long generations** — local RAM fills with context; W15-03's KV math applies to your laptop

## Resources

- HF [text generation strategies](https://huggingface.co/docs/transformers/generation_strategies) — the generation controls
- Qwen2.5 / SmolLM2 model cards — template conventions per family
- W2-05 (SLMs), W8-04 (base vs instruct), W1-07 (the API contract) — composed here
