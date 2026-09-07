# 06.1 — Neural Network Mechanics

> Subfolder index: [README.md](README.md) · Parent: [../06-from-neural-networks-to-llms.md](../06-from-neural-networks-to-llms.md)

---

## What you'll learn

- The neuron computation and layer stacking — implemented with NumPy, not imported
- Activation functions and the collapse theorem (why non-linearity is existential)
- Parameter counting as a skill (the memory-planning prerequisite)

## 1. The neuron, computed by hand

```python
import numpy as np

x = np.array([1.0, 2.0])               # input: 2 features
w = np.array([0.5, -0.25])             # weights: input importance
b = 0.1                                # bias: the firing threshold

z = w @ x + b                          # pre-activation: 0.5*1 + (-0.25)*2 + 0.1 = 0.1
a = np.maximum(0, z)                   # ReLU activation: max(0, z)
```

- **Weights** = how much each input matters. Training = searching for good weights.
- **Bias** = shifts the firing threshold off zero. Without `b`, the neuron's output is forced through the origin: `act(0)` whenever `x=0` — it cannot represent "activate only when input exceeds a threshold *away from zero*".
- **Activation** = non-linearity. Without it, stacked layers collapse: `W2 @ (W1 @ x) == (W2 @ W1) @ x` — a 50-layer linear network computes the same thing as one layer.

## 2. The collapse theorem, verified

```python
W1 = np.random.rand(4, 3); W2 = np.random.rand(4, 4)
x = np.random.rand(3)
# no activation between them:
assert np.allclose(W2 @ (W1 @ x), (W2 @ W1) @ x)      # True — depth buys nothing
# with ReLU between them:
h = np.maximum(0, W1 @ x)
# W2 @ relu(W1 @ x) is NOT a linear function of x anymore
```

Run both and see: the activated network can fit curves the linear stack cannot (W16-03's sin-curve experiment). This single experiment is why non-linear activations exist.

## 3. Parameter counting (the memory-planning skill)

```python
def layer_params(n_in, n_out, bias=True):
    return n_in * n_out + (n_out if bias else 0)

print(layer_params(768, 3072))          # 2,360,064 — one transformer FFN layer
print(layer_params(768, 768))           # 590,592 — one attention projection
```

Apply it to a real model: Qwen2.5-0.5B has 24 layers, each with 4 attention projections + 3 FFN projections. Reconcile the arithmetic to ~494M total parameters (W8-01's exercise) — the skill that converts "0.5B model" into "needs ~1 GB fp16 + KV cache" (W15-03).

## 4. Activation functions in context

| Activation | Formula | Where | Why |
|---|---|---|---|
| ReLU | max(0, z) | classic MLPs | simple, sparse; dead-neuron risk |
| **GELU** | smooth ReLU variant | transformer FFN | better gradients near zero |
| Sigmoid | 1/(1+e^−z) ∈ (0,1) | binary outputs, gates | saturates → vanishing gradients |
| Tanh | (−1, 1) | RNNs | zero-centered |
| **Softmax** | e^z/Σe^z → probabilities | model output layer | converts logits to distribution |

Softmax stability trick (W3-03): subtract the max before exponentiating — `exp(1000)` overflows; `exp(1000−max)` doesn't. Every LLM's output distribution passes through softmax.

## Exercises

1. Build a 3-layer MLP with NumPy only (weights, ReLU, forward) — verify against PyTorch's identical layers.
2. Collapse-theorem demo: train a linear 3-layer network and an activated one on `y=sin(x)` — plot both fits.
3. Parameter census: count every parameter in Qwen2.5-0.5B's config-driven architecture; reconcile to the published ~494M.
4. Softmax stability: compute softmax on logits with and without max-subtraction for values up to 1e4 — show the overflow and the fix.
5. Activation zoo: swap ReLU→GELU→tanh in the sin-fitter; compare convergence speed and final loss.

## Pitfalls

- **Bias omitted** — the network can't shift decision boundaries off zero (W3-03's argument)
- **Sigmoid in hidden layers** — saturation kills gradients; GELU/ReLU for hidden, sigmoid only at outputs
- **Softmax without max-subtraction** — numerical overflow on large logits
- **Confusing weight shape conventions** — (in, out) vs (out, in) transposes everything silently
- **Assuming depth helps linearly** — depth only helps with non-linearity between layers

## Resources

- 3Blue1Brown, *Neural Networks* series — the visual foundation
- W3-03 (training), W3-04 (transformer), W15-03 (serving memory) — the connected chapters
- [PyTorch nn docs](https://pytorch.org/docs/stable/nn.html) — Linear, activations, and their defaults
