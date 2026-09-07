# 06.2 — The Training Loop, Traced

> Subfolder index: [README.md](README.md) · Parent: [../06-from-neural-networks-to-llms.md](../06-from-neural-networks-to-llms.md)

---

## What you'll learn

- Every line of the training loop — forward, loss, backward, step — with what each does to memory and gradients
- Gradient inspection as a debugging tool
- The three classic failure modes: divergence, vanishing, exploding

## 1. The four lines, one by one

```python
import torch, torch.nn as nn

model = nn.Sequential(nn.Linear(1, 32), nn.ReLU(), nn.Linear(32, 1))
loss_fn = nn.MSELoss()
opt = torch.optim.Adam(model.parameters(), lr=0.01)

X = torch.linspace(-1, 1, 64).unsqueeze(1)
y = torch.sin(3 * X)

for step in range(500):
    pred = model(X)                       # 1. FORWARD: compute f(x;θ) through every layer
    loss = loss_fn(pred, y)               # 2. LOSS: scalar wrongness
    opt.zero_grad()                       # 3a. CLEAR: gradients accumulate by default!
    loss.backward()                       # 3b. BACKWARD: ∂loss/∂θ for every parameter
    opt.step()                            # 4. STEP: θ ← θ − lr·∇
```

Line-by-line:

| Line | What happens | What breaks if wrong |
|---|---|---|
| `model(X)` | tensors flow forward through every layer | — |
| `loss_fn(...)` | reduces predictions to one scalar | wrong loss = wrong task |
| `opt.zero_grad()` | resets `.grad` buffers | **gradients accumulate across steps** — the classic silent bug |
| `loss.backward()` | backprop computes all gradients | — |
| `opt.step()` | updates θ using gradients | without it, nothing learns |

## 2. Gradient inspection

```python
for name, p in model.named_parameters():
    if p.grad is not None:
        print(f"{name:20s} grad_norm={p.grad.norm():.5f}")
# weight norms shrink/grow per layer — vanishing (→0) vs exploding (→∞) visible here
```

Watch the gradient norms *per layer* during training: layer-0 norms collapsing relative to layer-N norms = vanishing gradients; sudden 100× jumps = exploding (clip with `torch.nn.utils.clip_grad_norm_`).

## 3. The three failure modes, reproduced

```python
# 1. DIVERGENCE — LR too high:
opt = torch.optim.SGD(model.parameters(), lr=5.0)     # loss oscillates, then NaN

# 2. VANISHING — deep sigmoid stack:
deep = nn.Sequential(*[nn.Sequential(nn.Linear(16, 16), nn.Sigmoid()) for _ in range(20)], nn.Linear(16, 1))
# layer-0 gradients ~1e-15 relative to last layer

# 3. EXPLODING — no clipping on a recurrent-ish graph:
# fix: torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
```

Each failure has a signature in the gradient norms — which is why file 06.1's gradient-inspection skill comes first.

## 4. The checkpoint (state you can resume)

```python
torch.save({"model": model.state_dict(),
            "opt": opt.state_dict(),
            "step": step}, "ckpt.pt")
# resume:
ck = torch.load("ckpt.pt"); model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"])
```

Model + optimizer + step = the minimum resumable state (W13-06's checkpointing idea, training edition). Forgetting the optimizer state restarts Adam's moment estimates — visible as a loss jump after resume.

## Exercises

1. Trace one training step: print every tensor's shape and norm through forward and backward for a 2-layer model.
2. Zero-grad bug: remove `opt.zero_grad()`; plot the loss — reproduce the accumulating-gradient failure, then fix.
3. Depth stress: 20 sigmoid layers vs 20 ReLU layers vs 20 ReLU+residual — compare layer-0 gradient norms (the vanishing-gradient measurement).
4. Clip experiment: train with `clip_grad_norm_(model.parameters(), 1.0)` vs unclipped on a spiky loss — compare stability.
5. Checkpoint round-trip: save at step 300, restore in a fresh process, continue training — verify the loss curve continues seamlessly (no jump).

## Pitfalls

- **`zero_grad` forgotten** — gradients accumulate; the most common silent training bug (W3-03)
- **Optimizer state lost on resume** — Adam restarts from scratch mid-training; save `opt.state_dict()` with every checkpoint
- **`model.eval()` forgotten at inference** — dropout/batchnorm change behavior silently
- **Loss on the wrong axis** — averaging over batch vs summing changes the effective LR
- **Device mismatches** — model on GPU, batch on CPU → cryptic errors; `.to(device)` discipline

## Resources

- W3-03 (optimizers), W16-03 (SFT training loop), W13-06 (checkpointing) — the surrounding machinery
- PyTorch [optimization tutorial](https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/) — Karpathy's debugging checklist (§1's failures map to its steps)
