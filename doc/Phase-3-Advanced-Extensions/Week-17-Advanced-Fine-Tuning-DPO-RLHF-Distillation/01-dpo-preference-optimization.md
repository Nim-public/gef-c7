# 01 — DPO: Direct Preference Optimization

> E1 index: [README.md](README.md)

**Core topic:** *DPO — alignment without RL. Math, datasets, TRL DPOTrainer.*

---

## What you'll learn

- The DPO objective and why it removes the reward model + RL loop
- Preference dataset formats (TRL's)
- Running DPO with LoRA on a single GPU
- β, label smoothing, and the failure modes of preference training

## 1. From RLHF to DPO — the idea

RLHF (W1-07/W16 recap): train a **reward model** on preference pairs, then PPO-optimize the policy against it while KL-penalizing drift from the reference model. Two models + an unstable RL loop.

**DPO's insight** (Rafailov et al., 2023): the reward-model + KL-constrained-RL problem has a closed-form solution — the optimal reward is expressible directly from policy probabilities. Substituting it back gives a simple *classification-style loss* on preference pairs:

```
L_DPO = -log σ( β·[ log π_θ(chosen|x)/π_ref(chosen|x)  −  log π_θ(rejected|x)/π_ref(rejected|x) ] )
```

Intuition: raise the *relative* log-probability of the chosen response vs the rejected one, **relative to the frozen reference model** (π_ref = your SFT base, unchanged). No reward model, no RL rollouts — one supervised loss.

What β does: the sharpness of the preference. β high → large updates for small preference gaps (aggressive); β→0 → the loss stops distinguishing chosen/rejected (model drifts toward maximizing the ratio — degradation). Typical: β ∈ [0.05, 0.3].

## 2. Preference datasets (TRL formats)

```python
# Explicit prompt (recommended)
{"prompt": [{"role": "user", "content": "Explain RAG briefly."}],
 "chosen":  [{"role": "assistant", "content": "RAG retrieves documents, then generates a grounded answer..."}],
 "rejected":[{"role": "assistant", "content": "RAG is a model architecture used in databases..."}]}
```

```python
from datasets import load_dataset
from trl import DPOConfig, DPOTrainer

ds = load_dataset("json", data_files="data/preferences.jsonl", split="train")
# must contain: prompt (str or messages), chosen (messages), rejected (messages)
```

Where do pairs come from? Your capstone already produces them:

- W9-05 👍/👎 logs → chosen = 👍 answer, rejected = 👎 answer (same question!)
- Two model outputs on the same question (frontier vs SLM, W15-04's router logs)
- Synthetic: one good answer + a deliberately flawed one (missing citation, wrong number — W16-02 Pattern C)

**Quality rule:** chosen and rejected must differ in *the property you're teaching* and match otherwise — otherwise DPO learns the noise.

## 3. DPOTrainer (with LoRA, single GPU)

```python
from peft import LoraConfig

peft_config = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)

cfg = DPOConfig(
    output_dir="out/dpo-v1",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=5e-6,                 # DPO LRs are small (5e-7..5e-6 for 7B; smaller models higher)
    beta=0.1,
    max_length=1024, max_prompt_length=512,
    num_train_epochs=1,                 # 1–3 epochs; preference data overfits fast
    logging_steps=10, eval_strategy="steps", eval_steps=50,
    bf16=True,
)

trainer = DPOTrainer(
    model="Qwen/Qwen2.5-0.5B-Instruct",  # or a model object + ref_model=None (PEFT auto-uses base)
    args=cfg,
    train_dataset=ds,
    peft_config=peft_config,
)
trainer.train()
trainer.save_model("out/dpo-v1/adapter")
```

Notes that matter:

- **π_ref handling**: with PEFT adapters, TRL uses the frozen base as the reference automatically (no second copy in memory — that's why LoRA-DPO fits single GPU)
- Metrics to watch: `rewards/chosen` ↑, `rewards/rejected` ↓, `rewards/margins` ↑, and **`rewards/accuracies`** (fraction of pairs ranked correctly — your training accuracy)
- Overfitting signature: margins explode while eval accuracy falls — stop, lower LR/epochs

## 4. Variants worth knowing (the config knobs)

| Variant | Fix for | TRL `loss_type` |
|---|---|---|
| **IPO** | DPO overfits/over-optimizes on small data | `"ipo"` |
| **robust DPO (cDPO)** | noisy preference labels (some pairs mislabeled) | `"robust"` + `label_smoothing=0.1` |
| **KTO** | unpaired data (just good/bad examples, not pairs) | separate `KTOTrainer` |
| **ORPO** | combines SFT + preference in one stage (no ref model) | separate `ORPOTrainer` |

Practical defaults for a first run: `loss_type="sigmoid"` (vanilla DPO), β=0.1, 1 epoch — then diagnose with the margin plots.

## 5. Evaluating the aligned model (parity again)

W16-04's checklist, preference edition:

1. **Preference win-rate**: for 30 held-out pairs, does the adapted model's answer get chosen over the SFT model's by a judge (W5-05 discipline: pinned, separate-family judge)?
2. **General parity**: your W11-05 battery — DPO famously degrades general ability ("alignment tax") if β/LR too aggressive
3. **Trajectory metrics**: tool-use and routing behavior unchanged (W10-04)

## Exercises

1. Build 50 preference pairs from your W9/W12 logs (chosen/rejected per question); train DPO; plot `rewards/margins` and `accuracies` per step.
2. β sweep {0.05, 0.1, 0.3}: win-rate vs general-parity battery. Pick an operating point.
3. Label-noise drill: flip 15% of chosen/rejected; rerun with `loss_type="robust", label_smoothing=0.1` vs vanilla — compare degradation.
4. KTO experiment: convert pairs to unpaired good/bad labels; run `KTOTrainer` — is unpaired data sufficient for your style task?
5. Write the "what DPO did to my agent" report: constitution adherence, citation rate, tool routing before/after (your W10-04 harness).

## Pitfalls

- **No reference-model discipline** — π_ref must be the *pre-DPO SFT model*; using the wrong ref invalidates the loss
- **Pairs that differ in length only** — DPO learns verbosity; keep chosen/rejected content-parallel
- **Too many epochs** — preference data memorizes in 1–3 epochs; watch eval margin collapse
- **β extremes** — β→0 collapses, β→∞ barely moves; sweep on the margin plots
- **Judging with the trained model** — W5-05's self-preference rule; separate judge

## Resources

- Rafailov et al., *Direct Preference Optimization* (2023) — §4 (the closed form)
- [TRL DPOTrainer docs](https://huggingface.co/docs/trl/dpo_trainer) — dataset formats, config
- Azar et al., *IPO* · Ethayarajh et al., *KTO* — the variants
- HF Alignment Handbook repo — full RLHF/DPO recipes end to end
