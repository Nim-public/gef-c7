# Week 16 — Evals and Fine-Tuning

> Full schedule: [GEF-C7-Final-Schedule.md](../../GEF-C7-Final-Schedule.md)

**Sessions:** Sat 26 Dec, 6:30–9:30 PM IST (Session 1) · Sun 27 Dec, 6:30–9:30 PM IST (Session 2) · Office Hours Thu 31 Dec, 7–8 PM IST · *note the earlier 6:30 PM start*

**Weekly task:** [05-capstone-task-llamaindex-retrieval.md](05-capstone-task-llamaindex-retrieval.md) · **Capstone prep:** [06-capstone-prep-demo-day.md](06-capstone-prep-demo-day.md)

---

## Why this week matters

The final course week closes both open threads. **Evals:** your RAG metrics (W5) get revised, extended with cloud platforms, and formalized into a dataset/versioning strategy — the discipline that makes every W17–24 capstone decision falsifiable. **Fine-tuning:** the last unexplored lever from W3-05's table — data, training loops, LoRA/QLoRA — with the W3-03 training loop you already know at its center. And the **LlamaIndex task** adds the final retrieval framework to your capstone before the capstone phase begins.

## What you will be able to do after this week

- [ ] Run the four Ragas metrics confidently and diagnose pipelines from them (W5-05, revised and extended)
- [ ] Design an evaluation strategy: offline vs online, LLM-as-judge calibration, dataset/versioning
- [ ] Generate synthetic eval/training data and validate it
- [ ] Explain the fine-tuning pipeline: data → tokenization → loaders → training loop → checkpoints
- [ ] Diagnose overfitting; apply regularization, LR schedules, and mid-training eval
- [ ] Reason about serving implications: full fine-tune vs adapters
- [ ] Configure and run single-GPU LoRA/QLoRA; verify evaluation parity
- [ ] Integrate LlamaIndex retrieval into the capstone (the formal task)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-eval-strategy-ragas.md](01-eval-strategy-ragas.md) | Ragas revision, cloud evals, offline/online, versioning | 3 h |
| 2 | [02-synthetic-data.md](02-synthetic-data.md) | Generating + validating synthetic eval/training data | 2 h |
| 3 | [03-fine-tuning-fundamentals.md](03-fine-tuning-fundamentals.md) | Data, tokenization, loaders, loops, checkpoints, overfitting | 3–4 h |
| 4 | [04-lora-qlora.md](04-lora-qlora.md) | LoRA/QLoRA math + single-GPU training + parity checks | 3–4 h |
| 5 | [05-capstone-task-llamaindex-retrieval.md](05-capstone-task-llamaindex-retrieval.md) | LlamaIndex retrieval system (formal task) | 3–4 h |
| 6 | [06-capstone-prep-demo-day.md](06-capstone-prep-demo-day.md) | W17–24 readiness + demo-day checklist | 1–2 h |

## Environment setup

```powershell
pip install ragas datasets llama-index llama-index-embeddings-huggingface
pip install peft trl transformers datasets accelerate bitsandbytes   # fine-tuning (GPU recommended)
pip install torch --index-url https://download.pytorch.org/whl/cpu   # CPU fallback for concepts
```

## Self-check before the capstone phase

1. Faithfulness 0.95, context recall 0.4 — what's broken, and which single W4–6 artifact do you fix first?
2. Your fine-tuned model beats base on your eval set but you trained on 60% of that set. What's the claim worth?
3. LoRA rank 8 vs 64: parameter count for a 7B model's attention layers, memory, and expected quality trade?
4. Why does "full fine-tune the facts" rot while "RAG the facts" doesn't (W3-05)? State the mechanism.
5. Your capstone demo is in 8 weeks. What is the *one* metric you'd put on the demo-day slide, and what evidence backs it?
