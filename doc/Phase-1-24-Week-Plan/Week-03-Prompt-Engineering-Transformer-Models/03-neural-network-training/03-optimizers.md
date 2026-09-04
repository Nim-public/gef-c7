# 03.3 — Optimizers

> Subfolder index: [README.md](README.md) · Parent: [../03-neural-network-training.md](../03-neural-network-training.md)

---

## What you'll learn

- SGD, momentum, and Adam — implemented in ~15 lines each
- The optimizer race on the same surface, same budget
- State memory: what each optimizer stores and what it costs

## 1. The three, implemented

```python
import numpy as np

class SGD:
    def __init__(self, lr): self.lr = lr
    def step(self, w, g, state): return w - self.lr * g

class Momentum:
    def __init__(self, lr, beta=0.9): self.lr, self.beta = lr, beta
    def step(self, w, g, state):
        state["v"] = self.beta * state.get("v", 0) + g
        return w - self.lr * state["v"]

class Adam:
    def __init__(self, lr, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, b1, b2, eps
    def step(self, w, g, state, t=1):
        state["m"] = self.b1 * state.get("m", 0) + (1 - self.b1) * g
        state["v"] = self.b2 * state.get("v", 0) + (1 - self.b2) * g * g
        m_hat = state["m"] / (1 - self.b1 ** t)
        v_hat = state["v"] / (1 - self.b2 ** t)
        return w - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

The mechanics:

- **SGD** — the gradient is the whole step. Simple, but the same LR must fit every curvature.
- **Momentum** — an exponentially-weighted average of recent gradients: accelerates along consistent directions, damps oscillation.
- **Adam** — per-parameter adaptive scaling: divides by the running RMS of gradients, so parameters with large gradients take relatively smaller steps. One LR works across wildly different parameter scales — the property transformers need.

## 2. The race (same surface, same budget)

```python
# the Rosenbrock valley from file 02 (W3-03's §2):
results = {}
for name, opt in [("sgd", SGD(0.001)), ("momentum", Momentum(0.001)), ("adam", Adam(0.02))]:
    w, state, path = np.array([-1.5, 2.0]), {}, []
    for t in range(1, 2001):
        g = grad2(w)
        w = opt.step(w, g, state, t)
        path.append(loss2(w))
    results[name] = path
```

Expected outcome on Rosenbrock: SGD@0.001 crawls; momentum@0.001 improves; Adam converges. SGD@0.01 oscillates; @0.05 diverges. The plot of three paths on the contour is the entire §5 argument, visualized.

## 3. State memory — the optimizer's price

| Optimizer | State per parameter | 7B model cost |
|---|---|---|
| SGD | 0 | 0 |
| Momentum | 1 float (v) | 28 GB (fp32) |
| **Adam** | 2 floats (m, v) + master weights | ~56 GB |
| 8-bit Adam | ~1 float | ~14 GB |

AdamW adds proper weight decay (decoupled — decay applies to weights directly, not through the gradient). The W16-03/04 consequence: LoRA exists partly because Adam state on 7B params is prohibitive — training 0.5% of parameters shrinks the optimizer state proportionally.

## 4. The failure signatures (from W3-03's table)

| Signature | Cause | Fix |
|---|---|---|
| loss oscillates between two values | LR too high for the curvature | lower LR, add momentum |
| loss explodes to NaN | LR way too high / overflow | clip gradients, lower LR, check softmax stability |
| loss plateaus high | underfitting or LR too low | raise LR, train longer, more capacity |
| late-training jump after resume | optimizer state not saved | save `opt.state_dict()` with checkpoints |

## Exercises

1. The race: three optimizers, same init and budget — plot loss curves and trajectories on the Rosenbrock contour.
2. LR sweep per optimizer: find each optimizer's divergence threshold; rank them by stability range.
3. State audit: instrument each optimizer to report total state memory — verify the SGD=0, momentum=1×, Adam=2× claim.
4. The noise experiment: mini-batch gradients (sample 8 of 64 points) — does stochastic noise improve the final loss vs full-batch? (W16-03's generalization preview.)
5. Implement AdamW: decouple weight decay from the gradient path (`w -= lr·(m_hat/(√v̂+ε) + wd·w)`) — compare against L2-in-gradient Adam.

## Pitfalls

- **State dict not per-parameter** — Adam's m/v are per-parameter tensors; one scalar breaks adaptivity
- **Bias correction skipped** — early steps are biased toward 0 without the (1−β^t) correction
- **The same LR for SGD and Adam** — Adam's effective steps are ~lr-sized; SGD needs the sweep
- **Weight decay through the gradient in Adam** — coupling decay with adaptive scaling misbehaves; AdamW decouples it
- **Forgetting `t` in the bias correction** — the correction uses the *current* step, which must be tracked

## Resources

- W3-03 parent (the mechanics), W16-03/04 (the consumers) — composed here
- Ruder, *An Overview of Gradient Descent Optimization Algorithms* — SGD→Adam in one survey
- Loshchilov & Hutter, *Decoupled Weight Decay Regularization* (AdamW) — the fix
