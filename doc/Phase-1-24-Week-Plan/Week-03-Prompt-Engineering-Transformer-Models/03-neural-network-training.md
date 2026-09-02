# 03 — Neural Network Training: Weights, Backprop, Optimizers

> Week 3 index: [README.md](README.md)

**Session 2 topic:** *Neural Networks (ANNs): Weights, Biases, & Activation Functions. Training: Forward Pass, Backward Pass, Backpropagation and Optimizers.*

---

## What you'll learn

- What weights and biases physically are — and why you can't remove them
- Activation functions: which, why, and what breaks without them
- The forward pass as matrix math you can compute by hand
- Backpropagation as the chain rule, made concrete
- Optimizers: SGD → momentum → Adam, and why Adam is everyone's default

## 1. Weights and biases: the learnable memory

A single neuron computes `y = act(w·x + b)`:

```python
import numpy as np

x = np.array([1.0, 2.0])            # input: 2 features
w = np.array([0.5, -0.25])          # weights: how much each input matters
b = 0.1                             # bias: baseline, fires even when x = 0
z = w @ x + b                       # pre-activation: 0.5*1 + (-0.25)*2 + 0.1 = 0.1
```

- **Weights** = input importance. Training = searching for good weights.
- **Bias** = activation threshold. Without it, output is *forced* through the origin: `y=act(0)` whenever `x=0` — the network can't shift its decision boundary off zero. (Classic exam question: a line without `b` always passes through (0,0).)
- Scale of learning: GPT-3 = 175 *billion* of these numbers; a 0.5B model = 500 million. Same math, more of it.

**Params count check** (connects to Week 2's memory math):

```python
def layer_params(n_in, n_out):
    return n_in * n_out + n_out        # weights + biases

layer_params(768, 3072)                # one transformer FFN layer ≈ 2.36M
```

## 2. Activation functions

Without non-linear activations, a stack of linear layers *is* one linear layer — depth would buy you nothing:

```python
W1 @ (W2 @ x) == (W1 @ W2) @ x        # collapse! one matrix
```

| Activation | Formula / range | Where you meet it |
|---|---|---|
| ReLU | `max(0, z)` | classic MLPs; dead-neuron risk |
| GELU | smooth ReLU variant | **inside transformers (default)** |
| Sigmoid | `1/(1+e^-z)` → (0,1) | binary output / gates |
| Tanh | (−1,1) | RNNs, older nets |
| Softmax | vector → probabilities summing to 1 | **final layer of classifiers & LLM output** |

```python
def softmax(z):
    e = np.exp(z - z.max())           # subtract max: the stability trick everyone must know
    return e / e.sum()

softmax(np.array([2.0, 1.0, 0.1]))    # [0.66, 0.24, 0.09] — next-token probabilities!
```

## 3. Forward pass — by hand

A 2-layer MLP on one input, computed literally:

```python
import numpy as np

W1 = np.array([[0.2, -0.4], [0.7, 0.1], [-0.5, 0.3]])   # (3 units, 2 inputs)
b1 = np.array([0.0, 0.1, -0.1])
W2 = np.array([[0.6], [-0.3], [0.8]])                    # (1 output, 3 units)
b2 = np.array([0.05])

def relu(z): return np.maximum(0, z)

x = np.array([1.0, 2.0])
h = relu(W1 @ x + b1)               # forward: layer 1
y_hat = (W2 @ h + b2).item()        # forward: layer 2 (linear output for regression)

print(h, y_hat)
```

Batched real code replaces the loops with one matrix multiply — that parallelism is also *why* transformers (Week file 04) scale.

## 4. Loss, then backward pass

Learning needs a scalar wrongness number. For regression: `MSE = mean((y_hat - y)²)`. For classification/next-token: **cross-entropy** — compare softmax probabilities against the true class.

```python
def cross_entropy(probs, true_idx):
    return -np.log(probs[true_idx] + 1e-12)

cross_entropy(softmax(np.array([2.0, 1.0, 0.1])), 0)   # ~0.41 — confident & correct
cross_entropy(softmax(np.array([2.0, 1.0, 0.1])), 2)   # ~2.25 — confident & wrong (punished hard)
```

**Backpropagation** = the chain rule applied through the computation graph, giving `∂loss/∂w` for *every* weight in one sweep (reusing intermediate results). Chain rule on our network:

```
loss ─► ŷ ─► z2 ─► h ─► z1 ─► x
∂L/∂W2 = ∂L/∂ŷ · ∂ŷ/∂z2 · ∂z2/∂W2      # output layer
∂L/∂W1 = ∂L/∂z2 · ∂z2/∂h · ∂h/∂z1 · ∂z1/∂W1   # same intermediate values, reused
```

Nobody writes this by hand for real models — autograd does it. Your job is to *trust it less blindly* by watching it once:

```python
import torch, torch.nn as nn

model = nn.Sequential(nn.Linear(2, 3), nn.ReLU(), nn.Linear(3, 1))
x = torch.tensor([[1.0, 2.0]])
y = torch.tensor([[1.5]])

pred = model(x)                    # forward
loss = nn.MSELoss()(pred, y)
loss.backward()                    # every ∂loss/∂param filled in

for name, p in model.named_parameters():
    print(name, p.grad)            # the backprop result, per tensor
```

Two classic failure modes you'll diagnose by *these gradients*:

- **Vanishing gradients**: products of many small numbers → early layers learn ~nothing (why ReLU/GELU and residual connections exist)
- **Exploding gradients**: opposite; fixed by gradient clipping (clip_grad_norm_ — you'll see it in every training script, Week 16)

## 5. Optimizers: how the step is taken

Gradient says *direction*; the optimizer decides *step size and momentum*.

### SGD — pure gradient descent

```python
w ← w − lr · ∂L/∂w
```

Simple, works, but slow in ravines (valleys with steep walls, flat floor) and sensitive to `lr`.

### Momentum — remember velocity

```python
v ← β·v + ∂L/∂w ;  w ← w − lr·v        # β ≈ 0.9
```

Averages recent gradients: accelerates along consistent directions, damps oscillation across them. Like a heavy ball rolling instead of a blind step.

### Adam — per-parameter adaptive learning rates (the default)

Keeps a running mean (`m`) and variance (`v`) of gradients per parameter, updates each with its own effective step:

```python
m ← β1·m + (1−β1)·g
v ← β2·v + (1−β2)·g²
w ← w − lr·m̂/(√v̂ + ε)          # β1=0.9, β2=0.999, ε=1e-8
```

Why it won: gradients in transformers vary wildly across parameters (embedding layers vs attention); Adam normalizes per-parameter, so one `lr` works broadly. Nearly every model in this program — the 0.5B toy and GPT-class — is trained with Adam or a variant (AdamW adds proper weight decay).

The trade you'll feel in Week 16: AdamW's state costs 2 extra floats per parameter — for a 7B model that's ~56 GB of optimizer state. Hence tricks like 8-bit optimizers and LoRA (only training tiny adapter weights).

### Learning rate — the hyperparameter

Too high: loss oscillates/diverges. Too low: eternal training. Practice: warmup then decay — Week 16's fine-tuning recipes all do this. Rule of thumb: 1e-3 for small MLPs (Adam), 1e-5…5e-5 for fine-tuning LLMs.

## 6. Watch it all work end-to-end

```python
import torch, torch.nn as nn

X = torch.linspace(-1, 1, 64).unsqueeze(1)
y = torch.sin(3 * X)

model = nn.Sequential(nn.Linear(1, 64), nn.Tanh(), nn.Linear(64, 1))
opt = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(2000):
    pred = model(X)
    loss = nn.MSELoss()(pred, y)
    opt.zero_grad(); loss.backward(); opt.step()
    if epoch % 400 == 0:
        print(f"epoch {epoch:4d}  loss {loss.item():.5f}")
```

Swap Adam ↔ SGD (try lr 0.01 and 0.5) and watch each behave. You've now personally executed: forward → loss → backward → optimizer, the loop that trains every model in this program.

## Exercises

1. Hand-compute the forward pass above for `x=[1,2]`; verify against NumPy. Then change `b1` to zeros — does the output change? Why did layer 1's bias still matter?
2. Prove the linear-collapse claim: build `nn.Linear→nn.Linear→nn.Linear` (no activation) on any data; fit `y=sin(x)`. Best achievable loss vs the activated net?
3. Train the sin-curve model with SGD lr=0.5, SGD lr=0.001, Adam lr=0.01 — same epochs. Plot/compare losses; explain each outcome.
4. Add `y = y + 0.1*torch.randn_like(y)` noise. Which optimizer setup generalizes best? (Connects to Week 1 overfitting.)
5. Print gradients before/after `loss.backward()` for `b2`. Then set `lr=0` — what changes and what doesn't?

## Pitfalls

- **Forgetting `opt.zero_grad()`** — gradients accumulate across steps; the most common silent training bug in existence
- **Softmax without max-subtraction** — `exp(1000)` overflows; always stabilize
- **SGD + bad lr on transformers** — divergence looks like "model is broken"; it's usually the optimizer
- **Judging by train loss only** — Week 1's overfitting lesson applies identically here
- **Expecting AdamW defaults to fit on small GPUs** — optimizer state memory is real; measure with `torch.cuda.max_memory_allocated()`

## Resources

- 3Blue1Brown, *Backpropagation* + *Gradient descent* episodes (the visual intuition)
- Karpathy, *micrograd* video — autograd + backprop built from scratch in ~100 lines
- PyTorch: [Optimization tutorial](https://pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- Ruder, *An overview of gradient descent optimization algorithms* — SGD→momentum→Adam in one post
