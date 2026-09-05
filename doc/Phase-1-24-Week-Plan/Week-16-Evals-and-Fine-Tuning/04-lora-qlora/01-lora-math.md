# LoRA Math — Low-Rank Delta, Parameter Counting

**What you'll learn:** the LoRA idea: instead of updating all weights
(W + ΔW), learn a low-rank factorization (ΔW = B·A) — the math, the
parameter counts, and why 100× fewer trained parameters works.

## 1. The delta decomposition

```text
full fine-tune:  W' = W + ΔW           ΔW has W's shape: d × k
LoRA:            W' = W + B·A          B: d × r,  A: r × k,  r << min(d,k)
```

```python
def lora_params(d: int, k: int, r: int) -> int:
    return d * r + r * k           # B and A

def full_params(d: int, k: int) -> int:
    return d * k

# one 4096×4096 attention projection, r=16:
print(lora_params(4096, 4096, 16))    # 131,072
print(full_params(4096, 4096))        # 16,777,216  → 128× fewer
```

| Quantity | Full | LoRA r=16 | Ratio |
|---|---|---|---|
| one 4096×4096 projection | 16.8M | 131k | 128× |
| all attention+MLP projections (7B model) | ~7B | ~40M (r=16) | ~175× |

The rank r is the expressiveness dial: r=8 covers simple style/format
adaptation, r=16–64 covers domain behavior. The 7B model's trainable
count drops from 7B to ~40M — which is why QLoRA fits on one GPU.

## 2. The init (why training starts stable)

```python
A = randn(r, k) * 0.01     # small random
B = zeros(d, r)            # zero
# ΔW = B·A = 0 at start → the model begins exactly as pretrained
```

B starts at zero, so the initial delta is zero — fine-tuning begins
from the pretrained behavior and moves away only as B and A learn.
This is LoRA's stability property: no catastrophic early drift.

## 3. The alpha scaling (the effective LR knob)

```python
# effective update: ΔW = (alpha/r) · B·A
# alpha/r = 2 with r=16, alpha=32 — the common starting point
```

| r | alpha (typical) | effective scale |
|---|---|---|
| 8 | 16 | 2 |
| 16 | 32 | 2 |
| 32 | 64 | 2 |

`alpha/r` rescales the delta independently of r — so raising r without
raising alpha *shrinks* the effective update. The convention
`alpha = 2r` keeps the scale constant while you tune capacity.

## 5. Which projections to target (the capacity allocation)

| Module set | Trainable (7B, r=16) | Learns |
|---|---|---|
| attention only (q,k,v,o) | ~13M | style, format, tone |
| + MLP (gate/up/down) | ~40M | domain behavior, vocabulary |
| + embeddings/lm_head | huge | rarely worth it |

The target table connects the math to the config decision (file 02):
the LoRA delta's *placement* decides what the adapter can learn. The
0.62% headline (40M of 6.7B) comes from attention+MLP — the standard
behavior fine-tune.

## 7. The LoRA pin note (the math's manifest)

**Task:** extend `reports/sdk-versions.md` with the LoRA math block:
the target projections, their dims, the r/alpha values, and the
parameter counts (trainable vs total) — the math's record.

**Worked approach:** the pin note is the math's artifact — the counts
verified against `print_trainable_parameters`, and the zero-init
property verified by the drill.

**Pass criterion:** note committed; the counts match the runtime's
report.

## 6. The multi-adapter trick (one base, many behaviors)

```python
# adapters share the frozen base — hot-swap per request:
# base (6.7B, fp16) = 14 GB
# adapter A (citations style) = 80 MB
# adapter B (terse voice)     = 80 MB
# adapter C (refusal-heavy)   = 80 MB
```

The multi-adapter trick is LoRA's deployment superpower: one frozen
base serves N behaviors by swapping 80 MB adapters — the W11
multi-tenant pattern made trivial. The parity checks (file 04) verify
each swap.

## 7. The LoRA pin note (the math's manifest)

**Task:** extend `reports/sdk-versions.md` with the LoRA math block:
the target projections, their dims, the r/alpha values, and the
parameter counts (trainable vs total) — the math's record.

**Worked approach:** the pin note is the math's artifact — the counts
verified against `print_trainable_parameters`, and the zero-init
property verified by the drill.

**Pass criterion:** note committed; the counts match the runtime's
report.

## Exercises

1. Compute the parameter counts for r ∈ {8, 16, 32, 64} on your target
   model's projections; plot the capacity/params curve.
2. Init drill: verify the zero-init property — before training, the
   LoRA model's outputs must equal the base model's exactly.
3. Alpha drill: fix r=16, sweep alpha ∈ {8, 16, 32, 64}; the effective
   scale's effect on the eval curve is the knob's lesson.
4. Target-table drill: fill §5's counts for your model; the allocation
   decision (attention-only vs +MLP) is data for file 02.