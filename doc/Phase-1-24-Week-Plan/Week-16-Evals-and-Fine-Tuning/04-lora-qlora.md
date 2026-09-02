# 04 — LoRA & QLoRA

> Week 16 index: [README.md](README.md)

**Session 2 topics:** *LoRA/QLoRA concepts; adapter config, target modules, rank/alpha. Single-GPU LoRA training & memory savings; evaluation parity checks.*

---

## What you'll learn

- The LoRA insight: fine-tuning as low-rank *delta*, not weight rewrites — with the math done by hand
- Adapter configuration: target modules, rank (r), alpha (α), dropout
- QLoRA: 4-bit base + adapters — single-GPU training of 7B+ models
- Evaluation parity checks between base and adapted models

## 1. The LoRA insight

Full fine-tuning updates a ΔW for every weight matrix W in the model. LoRA's claim (Hu et al., 2021): the *update* has low intrinsic rank — approximate it:

```
W' = W + ΔW,   ΔW ≈ B·A        A: (d × r), B: (r × d),  r << d
```

Parameter math, made concrete (768-d layer, r=8):

```
full ΔW:  768 × 768        = 589,824 params
LoRA:     (768×8) + (8×768) = 12,288 params       → 48× fewer
```

For a 7B model, r=8 on all attention + FFN projections ≈ **20–40M trainable params (~0.5%)**. Everything else stays frozen: no optimizer state for frozen weights (W15-03's memory math inverted), small checkpoints (tens of MB), swappable at serving (file 03's table).

`α` (alpha) scales the update: effective delta = `(α/r)·B·A`. Rule of thumb: keep `α = 2r` (or `α = r`) and tune `r` — higher r = more capacity, more memory, more overfit risk on small sets.

## 2. Target modules

Which weight matrices get adapters? The defaults:

| Target | Where | Why |
|---|---|---|
| `q_proj, k_proj, v_proj, o_proj` | attention (W3-04) | the classic LoRA targets |
| `gate_proj, up_proj, down_proj` | FFN (W3-04) | where much of the knowledge lives — bigger gains, more params |

Start: attention-only, r=8. If underfitting (W16-03's table): add FFN targets and/or raise r — measured against eval, not vibes.

## 3. Single-GPU LoRA training (PEFT + TRL)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

base = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(base)
ds = load_dataset("json", data_files="data/sft_train.jsonl", split="train")

model = AutoModelForCausalLM.from_pretrained(base, dtype="auto")

lora = LoraConfig(
    r=16, lora_alpha=32,                       # α = 2r convention
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)
model = get_peft_model(model, lora)
model.print_trainable_parameters()
# trainable params: 11M || all params: 494M || trainable%: 2.2

trainer = SFTTrainer(
    model=model,
    args=SFTConfig(output_dir="out/lora-v1", per_device_train_batch_size=4,
                   learning_rate=2e-4,          # 10× full-FT LR: adapters absorb it
                   num_train_epochs=3, lr_scheduler_type="cosine",
                   bf16=True, logging_steps=10,
                   eval_strategy="steps", eval_steps=20, save_strategy="steps"),
    train_dataset=ds, processing_class=tok,
)
trainer.train()
trainer.save_model("out/lora-v1/adapter")      # tens of MB — the deployable artifact
```

**QLoRA** adds one flag to the same recipe: load the base in 4-bit (`bnb_4bit_quant_type="nf4"` + precompute dtype), train adapters on top — 7B trains on a 16 GB GPU. The W15-03 quantization-vs-training split applies: QLoRA trains *adapters on a quantized base*; the base's 4-bit storage is a serving decision you already made (W2-05).

## 4. Evaluation parity checks

"Parity" = the fine-tuned model must not lose general capability while gaining the target behavior:

1. **Task eval** (the gain): your fine-tuning task's test set — did the specific behavior improve?
2. **General parity** (the non-regression): 20 general questions (reasoning, common knowledge, your W11-05 battery) — the adapted model must match base within noise
3. **Merged vs adapter serving check**: merge LoRA into the base (`merge_and_unload()`) and re-run — inference outputs must match the adapter-on-base run (float tolerance); catches merge-order bugs
4. **Template check** (W16-03): train and eval through the *same* chat template

```python
from peft import PeftModel

merged = base_model.merge_and_unload()         # adapter folded into weights
merged.save_pretrained("out/lora-v1/merged")   # serves like any model (W15-03)
```

## 5. The decision recap (W3-05, now with the mechanics known)

| Question | Answer now |
|---|---|
| Can LoRA teach new *facts*? | Poorly and temporarily — facts → RAG (W3-05), the failure mode is measured, not theoretical |
| Can LoRA teach *format/style*? | Yes — the sweet spot: your citation format, tone, JSON schemas |
| Rank/alpha first try? | r=16, α=32, attention+FFN — then sweep r ∈ {8, 32} on the eval set |
| One adapter per tenant? | Yes — that's the serving superpower (file 03 §5) |

## Exercises

1. Compute LoRA parameter count for Qwen2.5-0.5B at r=8, all four attention targets vs +FFN — verify with `print_trainable_parameters()`.
2. Train LoRA on your 200-row SFT set (file 03); run the task eval + the general-parity battery. Table: base vs LoRA on both.
3. Rank sweep: r ∈ {8, 32} on the same data — quality vs adapter size. Pick and justify.
4. QLoRA drill (GPU): same run with `bnb_4bit` base; measure memory (`torch.cuda.max_memory_allocated`) and quality delta.
5. Merge parity: merge the adapter; compare `merge_and_unload` outputs vs adapter-loaded outputs on 10 prompts (max logit diff). Any drift = a bug to find.

## Pitfalls

- **Target modules guessed** — model-specific names (`q_proj` vs `c_attn`); print the architecture and match (W3-04's layer names)
- **α/r confusion** — alpha scales the update; changing r without α changes the effective LR silently
- **Merged model ≠ adapter serving** — inference paths differ (merged runs fp16/fp32; adapter adds a live LoRA pass); parity-check both paths
- **Training on the eval set** — the leakage check (W16-02) before training, not after
- **Overfitting in 1 epoch at r=64** — capacity × small data = memorization; watch eval loss (W16-03's mid-training eval)

## Resources

- Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models* — the math (§4)
- Dettmers et al., *QLoRA* — 4-bit base + adapters (the single-GPU recipe)
- HF [PEFT docs](https://huggingface.co/docs/peft/index) + [TRL SFTTrainer](https://huggingface.co/docs/trl/index) — the implementation stack
- HF [LoRA blog](https://huggingface.co/blog/lora) — intuition-first walkthrough
- W3-03 (training loop), W16-03 (data/checkpoints), W15-03 (serving the merged/adapter model)
