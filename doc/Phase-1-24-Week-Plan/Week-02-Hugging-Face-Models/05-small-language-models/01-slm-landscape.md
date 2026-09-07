# 05.1 — The SLM Landscape

> Subfolder index: [README.md](README.md) · Parent: [../05-small-language-models.md](../05-small-language-models.md)

---

## What you'll learn

- The family map: capability per parameter count
- License classes across the families
- The benchmark interpretation for small models (E10-01 applied)

## 1. The family map (2026 state)

| Family | Sizes | License | Character |
|---|---|---|---|
| **Qwen2.5** | 0.5B–72B | Apache-2.0 | strong multilingual + code; the workhorse |
| **Llama 3.2/3.1** | 1B–405B | Llama license | ecosystem default; gated acceptance |
| **Phi-3.5/4** | 3.8B–14B | MIT | textbook-trained reasoning per param |
| **Gemma 2/3** | 2B–27B | Gemma terms | Google; solid, well-integrated |
| **SmolLM2** | 135M–1.7B | Apache-2.0 | fully open; great for tinkering |
| **Mistral** | 7B+ (Apache for some) | Apache | efficient, European option |

Capability-per-parameter is the metric that matters: Phi-3.5-mini (3.8B) rivals 7B models on reasoning benchmarks; Qwen-0.5B outperforms many 1B models on multilingual tasks. **The benchmark caveat (E10-01) applies doubly to SLMs** — leaderboard deltas are noise at this scale; your eval set is the signal.

## 2. License classes across families

| License | Commercial | Fine-tune | Redistribute weights | Notes |
|---|---|---|---|---|
| Apache-2.0 (Qwen, SmolLM, Mistral) | ✅ | ✅ | ✅ | the safe default |
| MIT (Phi) | ✅ | ✅ | ✅ | minimal |
| Llama Community | conditional | ✅ | ✅ <700M MAU | naming/branding terms |
| Gemma | conditional | ✅ | ✅ with terms | gated acceptance |
| Research-only | ❌ | varies | varies | exclude from capstone |

The fine-tuning column matters for W17: adapters trained on Apache-2.0 bases inherit the freedom; Llama-license adapters carry the naming/branding terms forward.

## 3. Capability-per-size patterns (with your eval as the test)

| Size | Reliable at | Unreliable at |
|---|---|---|
| 0.1–0.5B | short classification, extraction, simple rewrites | multi-step reasoning, long context |
| 1–2B | the above + summarization, simple JSON, light tool use | complex multi-constraint tasks |
| 3–4B | the above + solid tool calling, code snippets | nuanced judgment, long documents |
| 7B+ | most single-domain tasks | frontier reasoning, niche knowledge |

The pattern to internalize: each size step buys reliability on *harder instruction shapes*, not proportionally more knowledge. The W2-02 sanity protocol (negation, sarcasm, mixed intent) predicts where each size fails.

## 4. Choosing within a family

The family-consistent ladder (Qwen example): 0.5B → 1.5B → 3B → 7B — same template, same tokenizer, same data recipe, scaled. Benefits: a router (W15-04) can move between sizes with minimal prompt changes; fine-tuning recipes transfer. Cross-family routing works too (OpenAI-compatible endpoints, W2-05) but loses template/tokenizer consistency.

## Exercises

1. Family survey: for 3 families, tabulate the smallest model that handles each of your 5 capstone prompts acceptably — the capability-per-size curve for *your* tasks.
2. License matrix: for each family, the license terms for (a) internal use, (b) commercial product, (c) publishing fine-tuned weights.
3. Benchmark audit: pick 2 leaderboard entries for a 3B-class model — run the E10-01 checklist (contamination, scaffolding, task relevance).
4. Template consistency check: same prompt through Qwen-0.5B and Qwen-7B — how much prompt adjustment does the size step need?
5. The ladder design: define your router's size ladder (W15-04) — which size per traffic class, with the evidence from exercise 1.

## Pitfalls

- **Leaderboard worship at small scale** — 1-point MMLU deltas are noise; your 40-case eval decides
- **License assumptions across family versions** — terms changed between Llama versions; check per release
- **Ignoring the tokenizer switch at family boundaries** — different families = different tokenizers = different costs (W1-01.5)
- **Smallest-model maximalism** — below the reliability floor, retries and escalations cost more than the bigger model (W15-04's escalation economics)

## Resources

- Model cards per family (Qwen/Phi/Gemma/SmolLM) — the license and capability sources
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) — shortlist generator
- W2-05 parent, W15-04 (routing), E10-01 (benchmark literacy) — composed here
