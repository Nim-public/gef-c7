# 01 — Speculative Decoding

> E6 index: [README.md](README.md)

**Core topic:** *Draft/target speculative decoding — 2–3× generation speedup with provably identical outputs.*

---

## What you'll learn

- The draft-verify loop and why outputs are *provably* identical to target-only sampling
- Acceptance-rate math: what makes a speedup (and what makes it a slowdown)
- vLLM/Ollama speculative flags and how to benchmark properly

## 1. The mechanism

A small **draft model** (0.5B) rapidly proposes k tokens; the **target model** (7B) verifies all k in *one* forward pass (parallel!), accepting tokens it agrees with and resampling the first disagreement:

```
draft:  t1 t2 t3 t4 t5            (cheap, sequential, fast)
target: verify all 5 in ONE pass  (expensive, parallel)
        accept t1 t2 t3, reject t4, resample → continue
```

**The guarantee**: the target accepts/rejects with its own probabilities — a rejection resamples from exactly the distribution target-only decoding would have produced. Identical output distribution, guaranteed (this is the property that separates speculative decoding from draft-only shortcuts).

## 2. The speed math (derive before you deploy)

Per generated token:
- target-only: 1 target forward pass
- speculative: (1/k target passes amortized per accepted block) + k draft passes

Speedup ≈ `k_eff / (1 + c·k)` where `k_eff` = accepted tokens per block and `c` = draft/target cost ratio (~1/10 for 0.5B vs 7B). With acceptance ~0.7 and k=4: `k_eff ≈ 2.4` → ~2× speedup. The variables:

- **Acceptance rate ↑** = speedup ↑ (draft must be *similar* to target — same family/tokenizer, e.g., Qwen2.5-0.5B drafting for Qwen2.5-7B)
- **k too high** → wasted draft passes after a rejection (diminishing)
- **Cheap target or expensive draft** → slowdown (the failure mode)

Workloads that accept well: code (structured, predictable), boilerplate, template-ish answers. Workloads that accept poorly: high-temperature creative generation, heavy reasoning branches.

## 3. Running it

**vLLM** (W15-03's server, one flag):

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --speculative-model Qwen/Qwen2.5-0.5B-Instruct \
  --num-speculative-tokens 4
```

**Ollama**: recent versions support draft models in the Modelfile. **HF**: `assistant_model` on `generate()`:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
target = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
draft  = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

inputs = tok("Write a JSON config for a payment service", return_tensors="pt")
out = target.generate(**inputs, assistant_model=draft,
                      max_new_tokens=300, do_sample=False)
print(tok.decode(out[0]))
```

## 4. Benchmarking honestly (the W15-05 discipline)

| Metric | Definition |
|---|---|
| tokens/s | generated tokens ÷ wall time |
| acceptance rate | accepted ÷ drafted tokens (engine-reported) |
| output parity | same prompt+seed → identical text vs target-only (greedy) |
| quality | eval-set scores unchanged (they must be — that's the theorem; verify anyway) |

Freeze: same hardware, same request mix (W15-03's rule), greedy decoding for the parity check (sampling parity is distributional, not literal).

## Exercises

1. Benchmark speculative vs target-only on 3 workloads: code JSON (high acceptance), creative prose (low), summarization (medium). Tokens/s table + acceptance rates.
2. Acceptance math: with measured acceptance 0.65 and k=4, compute expected tokens/s speedup for c=0.1. Verify against your benchmark.
3. k sweep: `num-speculative-tokens` ∈ {2, 4, 8} — find the optimum for your workload and explain the shape.
4. Parity check: 10 prompts greedy, speculative vs target-only — assert identical strings. Any diff = a config bug (temperature not 0? draft mismatch?).
5. Router note (W15-04): speculative decoding makes the *frontier* path cheaper — does it change your router's crossover point? Recompute.

## Pitfalls

- **Draft/target tokenizer mismatch** — different vocab = broken speculation; same model family is the safe default
- **Benchmarking with sampling on** — parity requires greedy; sampled runs differ by design (not a bug — but not a parity test either)
- **k set once, never tuned** — the optimum is workload-dependent; sweep per traffic class
- **Speculating on already-fast paths** — short outputs (tool-call JSONs, file 22-02) may not amortize; measure per class
- **Assuming the theorem covers system prompts** — speculation applies to generation; the prefill (prompt processing) still costs what it costs (W15-03)

## Resources

- Leviathan et al., *Fast Inference from Transformers via Speculative Decoding* — the original paper + acceptance math (§2.2)
- Chen et al., *Accelerating LLM Decoding with Speculative Sampling* — the sampling-correct version
- vLLM [speculative decoding docs](https://docs.vllm.ai/en/latest/features/spec_decode.html) — flags and metrics
- HF [assistant generation](https://huggingface.co/blog/assisted-generation) — the `assistant_model` pattern
