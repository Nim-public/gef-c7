# 05.2 — Running SLMs Locally

> Subfolder index: [README.md](README.md) · Parent: [../05-small-language-models.md](../05-small-language-models.md)

---

## What you'll learn

- The three local paths hands-on: transformers, Ollama, LM Studio
- The endpoint-compatibility argument, demonstrated
- Context, memory, and concurrency management for local serving

## 1. Transformers (the experiment path)

```python
from transformers import pipeline

pipe = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
out = pipe([{"role": "user", "content": "Define RAG in one sentence."}],
           max_new_tokens=60, do_sample=True, temperature=0.7)
print(out[0]["generated_text"][-1]["content"])
```

Full control, slowest option, no quantization by default — the path for experiments and fine-tuning (W16-04).

## 2. Ollama (the production-local path)

```powershell
ollama pull llama3.2:1b
ollama run llama3.2:1b "Define RAG in one sentence."
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "Define RAG in one sentence."}])
```

What Ollama gives you: GGUF quantized models (W22-03), model management (`ollama list/rm/cp`), a local **OpenAI-compatible endpoint** — meaning your W1-07 API code runs unchanged with only a `base_url` change. The portability argument (W2-05 §3): dev on Ollama, prod on the API, same code path.

Ollama knobs worth knowing: `num_ctx` (context window — defaults are conservative, W4-02's truncation trap), `temperature/top_p` per request, and model variants (`llama3.2:1b-instruct-q4_K_M` — the quant tag from file W22-03).

## 3. LM Studio (the GUI path)

Same runtime class as Ollama (llama.cpp-based) with a model browser and a local server UI. Useful for exploring quants without the CLI, and for testing chat templates visually. Same OpenAI-compatible endpoint on `localhost:1234/v1`.

## 4. Local serving management

| Concern | Practice |
|---|---|
| memory | model + KV cache + runtime — budget with headroom (W15-03's math) |
| context | `num_ctx`/`max-model-len` set to what you *use* |
| concurrency | Ollama handles serial well; parallel needs `OLLAMA_NUM_PARALLEL` |
| updates | pin model tags (`llama3.2:1b` ≠ next month's rebuild) |
| multi-user | queue or scale out — a laptop serves one user well |

The W15-05 hardening rules apply to local serving identically: budgets, retries, observability — the endpoint being local doesn't exempt the discipline.

## Exercises

1. Side-by-side: the same 10 prompts through transformers-pipeline, Ollama, and LM Studio (same quant) — output diffs and latency table.
2. Context stress: set `num_ctx` to 2k and send a 3k-token prompt — observe truncation behavior; then right-size and verify.
3. Quantization A/B: fp16 pipeline vs Ollama 4-bit on your 40-case eval (W2-06) — quality delta measured (W22-03's protocol).
4. Concurrency probe: 5 parallel requests via Ollama — throughput and queueing behavior; compare with the API's concurrency (W2-02 ex. 3).
5. Portability proof: swap `base_url` between Ollama and the real API in your W14-05 assistant — what breaks? (Answer should be nothing — that's the compatibility dividend.)

## Pitfalls

- **Model tag drift** — `ollama pull llama3.2` without a tag moves silently; pin tags in the manifest (E8-01)
- **RAM underestimation** — model + KV + runtime; leave 30% headroom (W2-05's rule)
- **Local ≠ free of discipline** — budgets, retries, and observability apply (W15's rules); the endpoint being local doesn't remove the failure modes
- **Parallel requests on serial backends** — llama.cpp queues by default; timeouts on concurrent load
- **Hardcoded absolute model paths** — relative to your Ollama model store; use registry names

## Resources

- [Ollama docs](https://ollama.com/) + [OpenAI compatibility notes](https://ollama.com/blog/openai-compatibility)
- W2-05 parent, W15-01/05 (the reliability/optimization layers), W1-07 (the endpoint contract) — composed here
