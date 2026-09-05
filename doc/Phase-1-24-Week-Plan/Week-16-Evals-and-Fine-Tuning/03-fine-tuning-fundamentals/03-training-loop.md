# The Training Loop — Args, Schedules, Checkpoints, Best-Pick

**What you'll learn:** the training run: the arguments that matter,
LR schedules, checkpoint cadence, and the best-pick rule — the eval
set picks the checkpoint, not the training loss.

## 1. The arguments that matter

```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="models/sft-run-01",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,     # effective batch 32
    learning_rate=2e-5,                # SFT: 1e-5..2e-5 typical
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    eval_strategy="steps",             # eval DURING training (file 04)
    eval_steps=25,
    save_strategy="steps",
    save_steps=25,
    load_best_model_at_end=True,       # best-pick by eval metric
    metric_for_best_model="eval_loss",  # or your task metric
    bf16=True,
    logging_steps=5,
)
```

| Arg | Typical | Rationale |
|---|---|---|
| epochs | 2–3 | more → memorization (file 04) |
| effective batch | 32 | 4 × 8 accumulation on small GPUs |
| LR | 1–2e-5 | SFT's known-good band for 7–8B |
| eval/save steps | 25 | enough checkpoints to pick from |
| `load_best_model_at_end` | True | best-pick by eval, not last |

The knobs are SFT's known-good starting band — the *scheduler* and the
*best-pick* are what make the run defensible: cosine decay with warmup,
and the checkpoint chosen by eval performance.

## 2. The run and its curve

```text
step 25: eval_loss 1.42  ↓
step 50: eval_loss 1.18  ↓
step 75: eval_loss 1.09  ↓
step 100: eval_loss 1.11 ← flattening
step 125: eval_loss 1.15 ← rising = overfitting (file 04)
```

The eval-during-training curve is the run's story — the best checkpoint
is the curve's minimum, and `load_best_model_at_end` picks it
automatically. The training loss keeps falling after eval loss rises:
that divergence *is* overfitting, visible in one chart.

## 3. The run's artifacts (what gets committed)

| Artifact | Content |
|---|---|
| the config | the TrainingArguments (JSON, committed) |
| the curve | the eval-loss chart |
| the best checkpoint | the model (or its adapter — file 04) |
| the eval results | the 15-case set on the best checkpoint |

The artifacts are the run's evidence — the same discipline as every
decision memo: the config, the curve, and the eval results are
committed together. A training run without them is unreproducible.

## 5. The training pin note (the run's manifest)

```markdown
# SFT run 01 (W16)
- data: SFT v1 (200 records, source mix 50/25/15/10)
- args: epochs 3, eff-batch 32, LR 2e-5 cosine, bf16
- eval: 15-case set every 25 steps; best-pick by eval loss
- best checkpoint: step 75 (eval loss 1.09)
- seed: 42 (config committed)
- artifacts: config JSON, curve PNG, eval results parquet
```

The pin note is the run's manifest — data version, args, eval cadence,
best-pick, seed, and the artifact trio. It is the W12 pin discipline
applied to training: the run is reproducible from the note.

## Exercises

1. Run the loop on your SFT data; produce the eval curve; the best-pick
   checkpoint chosen by eval loss.
2. LR drill: train at 1e-5 and 5e-5; compare curves; the high-LR run's
   divergence teaches the band's reason.
3. Artifact drill: commit the config/curve/eval trio; a teammate
   reproduces the run from the config alone (seed included).
4. Pin drill: write the note; the trio's hashes recorded.