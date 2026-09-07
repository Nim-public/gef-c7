# 05.2 — Gradient Descent From Scratch

> Subfolder index: [README.md](README.md) · Parent: [../05-ml-fundamentals.md](../05-ml-fundamentals.md)

---

## What you'll learn

- The loss surface: what gradient descent actually walks on
- Learning-rate behavior: divergence, oscillation, convergence — produced and diagnosed
- Momentum, Adam, and schedules — reproduced on toy problems
- The connection to every training loop in the program (W16-03/04)

## 1. The loss surface, visualized

```python
import numpy as np
import matplotlib.pyplot as plt

def loss(w): return (w - 3) ** 2 + 1          # convex bowl
def grad(w): return 2 * (w - 3)

w, lr, path = 0.0, 0.3, [0.0]
for _ in range(20):
    w = w - lr * grad(w)
    path.append(w)

ws = np.linspace(-1, 5, 100)
plt.plot(ws, loss(ws)); plt.plot(path, loss(np.array(path)), "o-")
plt.title("gradient descent on a bowl"); plt.savefig("gd.png")
```

Observations to make: steps shrink as the gradient shrinks near the minimum; a larger `lr` overshoots and oscillates; `lr = 1.1` (past the stability boundary for this curvature) diverges. **The stability boundary is `lr < 2/L`** where L is the max curvature — the reason LLMs need tiny LRs (their curvature is enormous).

## 2. On two parameters (the real shape of the problem)

```python
def loss2(w): w = np.asarray(w); return np.sum((w - 3) ** 2) + 10 * (w[1] - w[0] ** 2) ** 2
def grad2(w):
    g = np.zeros(2)
    g[0] = -40 * w[0] * (w[1] - w[0] ** 2) - 2 * (3 - w[0])
    g[1] = 20 * (w[1] - w[0] ** 2)
    return g
```

This is Rosenbrock's valley — the classic hard surface: steep walls, flat floor. Run SGD, SGD+momentum, and Adam on it; visualize the paths. The lesson: **plain SGD zigzags across the valley; momentum smooths it; Adam adapts per-coordinate.** This is exactly why Adam became the default for transformers (W3-03's claim, now demonstrated).

## 3. The optimizers, implemented

```python
def sgd(w, g, state, lr):        return w - lr * g, {}
def momentum(w, g, state, lr, beta=0.9):
    state["v"] = beta * state.get("v", 0) + g
    return w - lr * state["v"], state
def adam(w, g, state, lr, b1=0.9, b2=0.999, eps=1e-8):
    state["m"] = b1 * state.get("m", 0) + (1 - b1) * g
    state["v"] = b2 * state.get("v", 0) + (1 - b2) * g * g
    m_hat = state["m"] / (1 - b1 ** (state.get("t", 0) + 1))
    v_hat = state["v"] / (1 - b2 ** (state.get("t", 0) + 1))
    state["t"] = state.get("t", 0) + 1
    return w - lr * m_hat / (np.sqrt(v_hat) + eps), state
```

~15 lines each — the optimizers are *this* small. Run all three on the valley (§2) with the same start and LR; plot the three paths on the contour. The differences you'll see are the entire W3-03 §5 argument, visualized.

## 4. Schedules — warmup and decay

```python
def schedule(step, total, warmup=50, base=0.01):
    if step < warmup: return base * step / warmup          # linear warmup
    progress = (step - warmup) / (total - warmup)
    return base * 0.5 * (1 + np.cos(np.pi * progress))     # cosine decay
```

Why warmup: at step 0 the optimizer's adaptive statistics (Adam's m/v) are garbage — a full LR step on garbage stats is destructive. Ramp up while they stabilize. Why decay: late in training, large steps bounce around the minimum instead of settling.

## Exercises

1. Divergence hunting: on the bowl, find the smallest LR that diverges; verify it matches the `2/L` stability bound.
2. The three optimizers on Rosenbrock: same init, 2000 steps — plot the three loss curves and the three trajectories on the contour. Rank them and explain.
3. Schedule A/B: constant LR vs warmup+cosine on the valley — final loss and path smoothness.
4. Mini-batch noise: sample 8 of 64 points per step (stochastic gradient) — compare path noise vs full-batch; explain why noise can *help* escape poor minima (W16-03's regularizations, preview).
5. Rebuild the W3-03 sin-curve experiment with your own optimizer implementations — replace `torch.optim.Adam` with your `adam()` function and reproduce the result.

## Pitfalls

- **Adam state memory** — 2 extra floats per parameter (W3-03); on 7B params that's ~56 GB of optimizer state — the reason 8-bit optimizers and LoRA exist
- **Warmup skipped on transformers** — early divergence that looks like "the model is broken"
- **Comparing optimizers at different step counts** — same total steps or same compute budget, never one epoch vs ten
- **Momentum state as a global** — per-parameter (W10-02's state-scoping rule, optimizer edition)
- **Cosine without warmup** — the first steps still use garbage adaptive statistics

## Resources

- W3-03 (the parent mechanics), W16-03/04 (training at scale) — the surrounding chapters
- Ruder, *An Overview of Gradient Descent Optimization Algorithms* — the survey behind §3
- [distill.pub](https://distill.pub) — Why Momentum Really Works (visualization-first)
