# Forward and Reverse Processes — Noise Schedules by Hand

**What you'll learn:** the diffusion sandwich — destroy an image with a
schedule you can compute, learn to invert it one step at a time — with every
formula evaluated on numbers you choose.

## 1. The forward process is closed-form

At step t, the noisy image is a *direct* interpolation with the original:

```text
x_t = √(ᾱ_t) · x_0 + √(1 − ᾱ_t) · ε        ε ~ N(0, I)
```

where `ᾱ_t = Π (1 − β_i)`. No simulation needed — any x_t is one line:

```python
import numpy as np

betas = np.linspace(1e-4, 0.02, 1000)            # linear schedule
alphas = 1 - betas
alpha_bar = np.cumprod(alphas)                    # ᾱ_t

def forward(x0: np.ndarray, t: int, rng: np.random.Generator) -> np.ndarray:
    ab = alpha_bar[t]
    noise = rng.standard_normal(x0.shape)
    return np.sqrt(ab) * x0 + np.sqrt(1 - ab) * noise

x0 = np.full((4, 4), 0.5, dtype=np.float32)       # uniform gray image
rng = np.random.default_rng(42)
for t in [0, 250, 500, 999]:
    xt = forward(x0, t, rng)
    print(f"t={t:4d}  mean={xt.mean():+.3f}  std={xt.std():.3f}")
# t→999: mean → 0, std → 1  (pure noise — the schedule's endpoint)
```

Check the endpoints by hand: `ᾱ_0 ≈ 0.9999` → x₀ ≈ itself; `ᾱ_999 ≈ 0.4e-4`... 
actually for the linear schedule `ᾱ_999 ≈ 4e-5` — the signal coefficient
`√ᾱ ≈ 0.006` — effectively gone. That is the schedule's job: a controlled
destruction path from image to noise.

## 2. Schedules: the dial everyone underestimates

| Schedule | β growth | ᾱ at t=500 | Character |
|---|---|---|---|
| linear | constant | ~0.29 | the DDPM default |
| cosine (Nichol-Dhariwal) | gentle start/end | ~0.41 | more signal mid-way, better FID |
| sqrt-linear | fast early | — | papers' experiments |

```python
def cosine_alpha_bar(t: np.ndarray, s: float = 0.008) -> np.ndarray:
    f = ((t / len(betas)) + s) / (1 + s)
    return (np.cos(f * np.pi / 2) ** 2) / (np.cos(s * np.pi / 2) ** 2)

print(alpha_bar[500].round(4), cosine_alpha_bar(np.array([500]))[0].round(4))
# 0.4867 vs ~0.5 — similar mid, but the cosine tail keeps ᾱ from collapsing
# into numerically-zero territory (it is clamped to 0.999⁻¹ per step)
```

The practical consequence: at the *same* step count, cosine schedules
preserve more signal late — which is why they win at few-step inference
(see file 04's step sweeps).

## 3. The reverse process: one learned step, repeated

The network `ε_θ(x_t, t)` predicts *the noise that was added*; the step is:

```text
x_{t-1} = 1/√α_t · (x_t − (1−α_t)/√(1−ᾱ_t) · ε_θ(x_t, t)) + σ_t·z
```

```python
def reverse_step_manual(xt, eps_pred, t, z=None):
    a, ab = alphas[t], alpha_bar[t]
    mean = (xt - (1 - a) / np.sqrt(1 - ab) * eps_pred) / np.sqrt(a)
    return mean if t == 0 or z is None else mean + np.sqrt(betas[t]) * z
```

Read it as a *denoising gradient step*: subtract the predicted-noise
component, rescale toward the cleaner distribution, add exactly the right
amount of fresh noise (the stochasticity term — remove it and sampling
collapses to mode-seeking).

The training objective is the reason this works: the network is trained to
recover `ε` from `x_t` at *every* t simultaneously — one model, 1000
denoising skills.

## Exercises

1. Endpoint check: compute `√ᾱ_999` for linear and cosine; verify the
   linear signal coefficient < 0.01 and explain what that means for x_999.
2. Schedule swap: generate x_500 with both schedules on your x0; compute
   per-pixel correlation with x0 — cosine must correlate higher.
3. Implement `reverse_step_manual` and drive it 1000 steps with a *fake*
   `ε_pred = x_t's actual noise` (cheat mode): the reconstruction should
   recover x0 almost exactly — proof that the step algebra is right.

## Pitfalls

- Confusing `α_t` (1−β), `ᾱ_t` (cumprod), and `√ᾱ` — every formula uses a different one; write all three on one line before deriving.
- Recomputing `np.cumprod` per step in loops — precompute the schedule array once (it is a constant).
- Sampling noise *inside* the schedule loop with a fresh RNG — breaks seed determinism (file 04); one generator, threaded through.

## Resources

- Ho et al. 2020 (DDPM) §4 — the training objective and the step equation.
- Nichol & Dhariwal 2021 §3.1 (cosine schedule and the clamping).
