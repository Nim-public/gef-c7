# Extension E1 — Advanced Fine-Tuning: DPO, RLHF & Distillation

> Extensions overview: [../README.md](../README.md)

**Builds on:** W16-04 (LoRA/QLoRA) · W3-05 (alignment theory)

**Practice build:** [05-practice-alignment-lab.md](05-practice-alignment-lab.md)

---

## Why this extension matters

W16-03/04 taught SFT. Production alignment goes further: **preference optimization** (DPO) teaches models *which of two answers is better* without a reward-model RL loop, **distillation** compresses frontier capability into cheap SLMs, and **embedder/reranker fine-tuning** adapts your retrieval stack (W4–5) to your domain. These are the techniques behind every production-aligned model — this week runs them hands-on.

## What you will be able to do after this week

- [ ] Format preference datasets and run DPO with TRL
- [ ] Explain the RLHF pipeline and where DPO replaces PPO (and what GRPO changes)
- [ ] Distill a frontier model's behavior into a small model and evaluate the trade
- [ ] Fine-tune your own embedder and cross-encoder reranker on domain pairs
- [ ] Verify alignment training with parity + preference evals (no regression)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-dpo-preference-optimization.md](01-dpo-preference-optimization.md) | DPO math + TRL DPOTrainer | 3–4 h |
| 2 | [02-rlhf-pipeline.md](02-rlhf-pipeline.md) | RM training, PPO vs DPO vs GRPO | 2–3 h |
| 3 | [03-distillation.md](03-distillation.md) | KD approaches, data generation, serving trade | 2–3 h |
| 4 | [04-embedding-reranker-finetuning.md](04-embedding-reranker-finetuning.md) | Domain embedder + cross-encoder training | 3 h |
| 5 | [05-practice-alignment-lab.md](05-practice-alignment-lab.md) | Alignment lab: DPO + eval + distill decision | 4 h |

## Environment setup

```powershell
pip install trl peft transformers datasets accelerate
pip install sentence-transformers       # file 04
# GPU strongly recommended for DPO (2 models in memory — see file 01 §4)
```

## Self-check before E2

1. In DPO's loss, what does β control — and what happens to a well-intentioned model at β→0?
2. Why can DPO skip the explicit reward model that PPO requires? (One sentence about the closed-form.)
3. Your distilled 1B model aces eval-set tasks but fails novel phrasings. What does that tell you about the distillation data?
4. Fine-tuned embedder: what metric proves it improved on *your* domain without losing general retrieval?
5. Which capstone component would you align first with DPO — and what preference pairs would you collect?
