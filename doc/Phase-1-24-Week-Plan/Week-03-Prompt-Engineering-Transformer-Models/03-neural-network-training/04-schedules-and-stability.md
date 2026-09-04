# 03.4 — Schedules & Stability

> Subfolder index: [README.md](README.md) · Parent: [../03-neural-network-training.md](../03-neural-network-training.md)

---

## What you'll learn

- Warmup: why the first steps need a ramp
- Decay schedules: cosine, linear, and their effect on final quality
- Gradient clipping and the stability toolkit
- The failure-diagnosis table for training runs

## 1. Warmup — why the first steps are special

At step 0, Adam's moment estimates (m, v) are uninitialized garbage — a full-size step on garbage statistics is destructive. Warmup ramps the LR from 0 to base over the first N steps while the statistics stabilize:

```python
def lr_at(step, base_lr, warmup_steps, total_steps):
    if step < warmup_steps:
        return base_lr * step / max(warmup_steps, 1)          # linear warmup
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return base_lr * 0.5 * (1 + np.cos(np.pi * progress))      # cosine decay
```

The transformer-specific reason: attention logits at initialization are large and miscalibrated — the first gradients are enormous. Warmup rides them out. Every LLM training recipe (W16-03/04) includes it.

## 2. Decay schedules compared

| Schedule | Shape | Behavior |
|---|---|---|
| constant | flat | simple; late training bounces |
| cosine | smooth arc down | the modern default — settles cleanly |
| linear | straight down | equivalent-ish to cosine in practice |
| step | drops at milestones | legacy; hard to tune |

The schedule changes the *effective* LR trajectory, which changes which minimum you settle into. Two runs identical except schedule converge differently — the A/B in file 03-03's exercises demonstrates it.

## 3. Gradient clipping

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
# rescales the global gradient norm to ≤ 1.0 BEFORE the optimizer step
```

Clipping doesn't change the direction — only caps the magnitude when a bad batch produces a huge gradient. Order: `backward()` → `clip` → `step()`. Without it, one outlier batch can launch the weights into a bad region they never recover from.

## 4. The failure-diagnosis table

| Symptom | Likely cause | First check |
|---|---|---|
| loss → NaN within 100 steps | LR too high / overflow | halve LR; check softmax stability; clip |
| loss plateaus immediately | LR too low / underfitting | raise LR, check capacity, check data |
| loss drops then rises | overfitting | more data, regularization, early stop (W1-05) |
| train fine, eval garbage | leakage or distribution shift | W1-05 §3's audit |
| loss spiky but recovers | bad batches | gradient clipping + data audit |
| eval loss jumps after resume | optimizer state lost | save/load the full optimizer state |

The diagnosis order: data → LR/schedule → capacity → regularization. Most "broken training" is data or LR.

## Exercises

1. Warmup A/B: with vs without warmup on the transformer-scale toy (large init logits) — show the early divergence and the fix.
2. Schedule race: constant vs linear vs cosine on the same run — final loss and curve smoothness.
3. Clipping boundary: find the `max_norm` where training first stabilizes on a spiky dataset; verify gradients are rescaled, not zeroed.
4. The diagnosis drill: three prepared "broken" runs (high LR, leakage, dead ReLUs) — diagnose each from the curves and norms alone.
5. SLO for training: define your run's expected loss trajectory (from a good run) and alert when the actual deviates — the W15-02 monitoring discipline, training edition.

## Pitfalls

- **Warmup too short** — the first 100 steps do the damage before the ramp helps; scale warmup with batch size
- **Cosine to zero** — the LR ends at exactly 0; leave a floor if resuming
- **Clipping masking real problems** — clipping a persistently huge gradient hides a data bug; investigate first
- **Schedule changed mid-run** — the optimizer state (m/v) assumes the old trajectory; restart or re-warm
- **Comparing runs with different step counts** — schedule shapes differ; compare at equal *effective* training

## Resources

- W3-03 parent (optimizers), W16-03/04 (the consumers at scale) — composed here
- HF [TrainingArguments](https://huggingface.co/docs/transformers/main_classes/trainer#training-arguments) — `warmup_ratio`, `lr_scheduler_type`
- [Adam: A Method for Stochastic Optimization](https://arxiv.org/abs/1412.6980) — §2 bias correction and schedules
