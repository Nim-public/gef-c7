# 07 — LLM Concepts & Demos: Deep Dive

> Parent topic: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md) · Week 1 index: [../../README.md](../../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-chat-completions-anatomy.md](01-chat-completions-anatomy.md) | Request/response anatomy, usage accounting | 3 h |
| 2 | [02-multi-turn-and-context.md](02-multi-turn-and-context.md) | History management, trimming, session cost | 3 h |
| 3 | [03-sampling-and-logprobs.md](03-sampling-and-logprobs.md) | Temperature/top_p, logprob applications | 3 h |
| 4 | [04-alignment-and-generation.md](04-alignment-and-generation.md) | Autoregressive loop, streaming, alignment stages | 2 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — the request/response objects field by field, usage → cost reconciliation
- **02** — multi-turn state as *your* code: trimming, summarizing, re-injection, per-session cost curves
- **03** — sampling parameters as distribution shapes; logprobs for confidence, classification, routing
- **04** — the token loop made visible, streaming, and where pre-training/SFT/RLHF show up in behavior
- **exercises.md** — labs including the cost-ledger seed and the truncation-aware prompting utility
