# 03 — Fine-Tuning Fundamentals

> Week 16 index: [README.md](README.md)

**Session 2 topics:** *Data/labeling, tokenization, loaders; training loops; checkpoints. Overfitting/regularization, LR schedules, eval during train. Serving implications of full FT vs adapters.*

---

## What you'll learn

- The fine-tuning pipeline end to end: data → labeling → tokenization → loaders → training loop → checkpoints → eval
- Overfitting/regularization in the LLM context, with LR schedules and mid-training eval
- Serving implications: full fine-tune vs adapters (the W3-05 lever, engineering edition)
- When fine-tuning is justified at all (the W3-05 decision procedure, revisited with evidence)

## 1. Data: the 80% of fine-tuning

Full fine-tuning changes all weights; **data quality dominates architecture choice**. The pipeline:

```python
# 1. Format: instruction-tuning JSONL (W1-04's format, chat-message style)
{"messages": [
    {"role": "system", "content": "You are the capstone assistant."},
    {"role": "user", "content": "What is the refund timeline?"},
    {"role": "assistant", "content": "Refunds complete in 5 business days [handbook §4.2]."}]}

# 2. Labeling sources (best first):
#    - human-written gold answers (your W5-05 references)
#    - verified pipeline outputs (W16-02 Pattern D — citation+grounding passed)
#    - frontier-model drafts, human-edited
```

| Property | Rule |
|---|---|
| Volume | format/style tasks: 500–5,000 rows; capability tasks: much more (and usually wrong lever, W3-05) |
| Consistency | one style guide; contradictions teach the model to hedge |
| Dedup/leakage | near-dup split check (W16-02 §3) *before* training |
| Masking | train only on assistant tokens (frameworks do this via `response_template`) |
| Distribution | match deployment input mix (W16-02's weighted grid) |

## 2. Tokenization & loaders

```python
from transformers import AutoTokenizer
from datasets import load_dataset

tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
ds = load_dataset("json", data_files="data/sft_train.jsonl", split="train")

def format(example):
    msgs = tok.apply_chat_template(example["messages"], tokenize=False)   # W1-01's template!
    return tok(msgs, truncation=True, max_length=1024)

ds = ds.map(format, remove_columns=ds.column_names)
```

- **Chat template** tokens delimit turns (W1-01) — training data must match the *serving* template exactly, or the model learns a format you never deploy
- `max_length` = prompt + response; truncation drops the *answer end* — audit truncation rate
- Labels mask non-assistant tokens (`-100` in the label field) so the loss counts only assistant output — the frameworks' `DataCollatorForCompletionOnlyLM` / TRL equivalents

## 3. The training loop (yours, from W3-03, at LLM scale)

The loop is identical — forward, loss, backward, step — with orchestration around it:

```python
from transformers import Trainer, TrainingArguments

args = TrainingArguments(
    output_dir="out/sft-v1",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,          # effective batch 32 on small GPUs
    learning_rate=2e-5,                     # LLM FT range ~1e-5..5e-5 (file 03-W3 rule)
    num_train_epochs=3,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=10,
    eval_strategy="steps", eval_steps=100,  # eval DURING train (this week's topic)
    save_strategy="steps", save_steps=100,  # checkpoints = resumability + best-pick
    bf16=True,                              # GPU; drop for CPU toy runs
    load_best_model_at_end=True, metric_for_best_model="eval_loss",
)
```

**Checkpoints** are not optional hygiene: mid-training eval picks the best point (loss curves bottom then *rise* — overfitting), and every checkpoint is a resumable, versioned artifact (W13-06's persistence idea, at training scale). Retention: keep the best + last, not all.

## 4. Overfitting, regularization, schedules

| Phenomenon | Symptom | Remedy |
|---|---|---|
| **Overfitting** | train loss ↓, eval loss ↑ | fewer epochs, more data, weight decay, lower LR |
| **Catastrophic forgetting** | new task ✓, old abilities ✗ | mix general data (5–20%) into the set; LoRA (file 04) |
| **Loss spikes** | sudden divergence | lower LR, gradient clipping (`max_grad_norm`), smaller batch |
| **Underfitting** | both losses high | more epochs, higher LR, more capacity (LoRA rank ↑) |

**LR schedules**: warmup (ramp from 0 — stabilizes early steps) then decay (cosine/linear — refine at the end). The schedule is part of the recipe: two runs identical except schedule behave differently (W3-03's optimizer exercises, now with the schedule knob).

**Eval during training**: a small held-out set evaluated every N steps → `load_best_model_at_end` picks the checkpoint by *eval*, not train, loss. This is the W1-05 train/val/test discipline, automated.

## 5. Serving implications: full FT vs adapters

| | Full fine-tune | LoRA/adapter (file 04) |
|---|---|---|
| trainable params | 100% (0.5B–7B+) | 0.1–2% (rank r matrices) |
| artifact | full model weights | tens of MB adapter |
| serving | one model per variant | **swap adapters on one base** (multi-tenant!) |
| training memory | weights + optimizer state (AdamW ×3) | adapters only |
| risk | catastrophic forgetting, expensive rollback | merge confusion, rank limits |
| rollback | re-deploy old weights | drop the adapter |

The serving insight (and why adapters won in industry): N fine-tuned variants = N full copies vs one base + N hot-swappable adapters — the difference between an ops project and a config change. Rollback = unloading the adapter.

## Exercises

1. Build a 200-row SFT set from your W16-02 distillation prep (§1); report truncation rate at `max_length=1024` and fix the outliers.
2. Verify label masking: tokenize one example, decode the `-100`-masked label positions — confirm only assistant tokens train.
3. Train Qwen2.5-0.5B on 200 rows (full FT on CPU is slow — 50 rows is fine for the *pattern*): plot train+eval loss per 20 steps; identify the overfitting point.
4. Regularization A/B: rerun with `weight_decay=0.1` + `warmup_ratio=0.1`; compare eval-loss curves.
5. Write the serving-implication paragraph for your capstone: what would full FT cost to serve vs adapters, and what does your W15-04 router do with two adapters?

## Pitfalls

- **Training on eval data** — leakage via near-duplicates (W16-02); split with embedding dedup first
- **Chat-template mismatch** — training template ≠ deployment template = quality loss invisible in training metrics
- **Too many epochs** — LLM SFT overfits in 1–3 epochs typically; "more epochs" is not more better
- **Forgetting `gradient_accumulation_steps`** — effective batch matters for LR; mismatched batch/LR pairs diverge
- **No mid-training eval** — best checkpoint ≠ last checkpoint; `load_best_model_at_end` exists for a reason
- **Full FT without data volume** — 200 rows × 7B params = forgetting, not improvement (file 04's LoRA is the fix)

## Resources

- Hugging Face [TRL](https://huggingface.co/docs/trl/index) (SFTTrainer) + [PEFT](https://huggingface.co/docs/peft/index) — the libraries for files 03/04
- Karpathy, *nanoGPT / Zero to Hero* — the loop you already know, at training scale
- W3-03 (optimizers/schedules), W3-05 (when to fine-tune), W16-02 (data generation) — the pipeline pieces
- Géron, *Hands-On ML* ch. 11 + HF [training arguments reference](https://huggingface.co/docs/transformers/main_classes/trainer) — the knobs
