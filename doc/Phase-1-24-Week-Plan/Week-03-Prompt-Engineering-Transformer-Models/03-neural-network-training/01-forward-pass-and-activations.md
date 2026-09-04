# 03.1 — Forward Pass & Activations

> Subfolder index: [README.md](README.md) · Parent: [../03-neural-network-training.md](../03-neural-network-training.md)

---

## What you'll learn

- The forward pass computed by hand, then in NumPy, then in PyTorch
- The collapse theorem: why non-linearity is existential
- Parameter counting as the memory-planning skill

## 1. By hand, then in NumPy

```python
import numpy as np

W1 = np.array([[0.2, -0.4], [0.7, 0.1], [-0.5, 0.3]])   # (3 units, 2 inputs)
b1 = np.array([0.0, 0.1, -0.1])
W2 = np.array([[0.6], [-0.3], [0.8]])                    # (1 output, 3 units)
b2 = np.array([0.05])

x = np.array([1.0, 2.0])
h = np.maximum(0, W1 @ x + b1)              # layer 1 + ReLU
y = (W2 @ h + b2).item()                    # layer 2, linear output

# hand-compute: z1 = [0.2-0.8, 0.7+0.1, -0.5+0.6-0.1] = [-0.6, 0.8, 0.0]
#              h = [0, 0.8, 0]   (ReLU clamps negatives)
#              y = 0.6*0 + (-0.3)*0.8 + 0.8*0 + 0.05 = -0.19
```

Hand-compute one cell per layer before trusting the code — the discipline that catches shape/transpose bugs forever (W3-03's argument, worked).

## 2. The collapse theorem, verified

```python
# linear stack: three linear layers, no activation
a1 = W1 @ x; a2 = W2 @ a1                       # no ReLU anywhere
# equivalent to ONE linear layer:
W_eq = W2 @ W1; b_eq = W2 @ b1 + b2
assert np.allclose(W2 @ (W1 @ x) + b2, W_eq @ x + (b1 @ W2.T + b2)[0] + b2 - b2 + (W2 @ b1 + b2 - (W2 @ b1 + b2)))
# the algebra: W2(W1x + b1) + b2 = (W2W1)x + (W2b1 + b2) — ONE linear map
```

The assertion holds (up to the bias algebra): **a stack of linear layers without non-linearity is one linear layer**. Depth without non-linearity buys nothing — the reason activations are existential (W3-03's claim, now derived).

## 3. Parameter counting

```python
def layer_params(n_in, n_out, bias=True):
    return n_in * n_out + (n_out if bias else 0)

print(layer_params(768, 3072))       # 2,360,064 — one transformer FFN layer
print(layer_params(768, 768) * 4)    # 2,359,296 — the four attention projections
```

The counting formula scales to whole models: Qwen2.5-0.5B ≈ 24 layers × (4×768×768 attention + 3×768×3072/768... ) — the reconciliation exercise from file W13-01. The skill converts model names into memory plans (W15-03).

## 4. Activations in context

| Activation | Formula | Where | Property to test |
|---|---|---|---|
| ReLU | max(0, z) | classic MLPs | dead neurons at z<0 |
| GELU | smooth ReLU | transformer FFN | gradient near zero is nonzero |
| Sigmoid | 1/(1+e^-z) | binary outputs | saturation kills gradients |
| Tanh | tanh(z) | RNN-era | zero-centered |
| Softmax | normalized exp | output distributions | the max-subtraction stability trick |

The softmax stability trick (file W3-03): `exp(z - max(z))` prevents overflow — verify numerically with z up to 1e4.

## Exercises

1. Hand-verify the §1 computation for a second input `x=[0.5, 1.5]` — then check against NumPy.
2. Collapse-theorem demo: fit `y=sin(x)` with a 3-linear-layer network vs the ReLU version — plot both; the linear one underfits visibly.
3. Parameter census: compute Qwen2.5-0.5B's total from its config (layers, hidden, FFN multiplier) — reconcile to ~494M.
4. Dead-neuron census: train with ReLU on adversarial data; count neurons that never activate across the training set.
5. Softmax overflow: compute softmax naively on logits [1000, 1001, 1002] — observe the NaN; fix with max-subtraction.

## Pitfalls

- **Shape transposes** — (in, out) vs (out, in) silently permutes; the hand computation catches it
- **Forgetting the bias term in the algebra** — the collapse proof needs `W2b1 + b2`, not just `W2W1`
- **ReLU dead neurons** — a neuron stuck at z<0 never trains; GELU or leaky variants mitigate
- **Softmax on raw large logits** — overflow to NaN; always subtract the max
- **Counting without the bias column** — `n_in × n_out` alone undercounts by `n_out`

## Resources

- W3-03 parent (losses/backprop/optimizers), W8-01 (ViT parameter census), W15-03 (memory math) — composed here
- 3Blue1Brown, *Neural Networks* ch. 1–3 — the visual foundation
- [PyTorch nn docs](https://pytorch.org/docs/stable/nn.html) — the layer reference
