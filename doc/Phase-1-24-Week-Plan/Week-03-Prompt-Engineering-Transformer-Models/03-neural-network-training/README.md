# 03 — Neural Network Training: Deep Dive

> Parent topic: [../03-neural-network-training.md](../03-neural-network-training.md) · Week 3 index: [../README.md](../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-forward-pass-and-activations.md](01-forward-pass-and-activations.md) | Neurons, layers, activations, by-hand forward | 3 h |
| 2 | [02-loss-and-backprop.md](02-loss-and-backprop.md) | Losses, chain rule, autograd verification | 3 h |
| 3 | [03-optimizers.md](03-optimizers.md) | SGD→momentum→Adam, implemented and raced | 3 h |
| 4 | [04-schedules-and-stability.md](04-schedules-and-stability.md) | Warmup, decay, clipping, failure diagnosis | 2 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — the forward pass computed by hand; the collapse theorem verified; parameter counting
- **02** — losses (MSE/cross-entropy), backprop as the chain rule, autograd verification, the three failure modes
- **03** — the optimizers implemented in ~15 lines each and raced on the same surface
- **04** — LR schedules, warmup, gradient clipping, and the failure-diagnosis table
- **exercises.md** — labs including the optimizer race and the divergence hunt
