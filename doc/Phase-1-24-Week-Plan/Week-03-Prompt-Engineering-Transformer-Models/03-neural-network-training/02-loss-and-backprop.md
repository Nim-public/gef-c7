# 03.2 — Loss & Backprop

> Subfolder index: [README.md](README.md) · Parent: [../03-neural-network-training.md](../03-neural-network-training.md)

---

## What you'll learn

- The losses (MSE, cross-entropy) with hand-computed values
- Backpropagation as the chain rule through your own 2-layer network — every gradient derived by hand
- Autograd verification: your hand-derived gradients vs PyTorch's
- The three failure signatures in gradient norms

## 1. The losses by hand

```python
# MSE (regression): mean of squared errors
pred, true = 2.0, 1.5
mse = (pred - true) ** 2                    # 0.25

# cross-entropy (classification): -log(p_true_class)
probs = [0.66, 0.24, 0.10]                  # from softmax([2.0, 1.0, 0.1])
ce_correct = -np.log(0.66)                  # 0.416 — confident AND correct
ce_wrong    = -np.log(0.10)                 # 2.303 — confident AND wrong (punished hard)
```

The asymmetry is the teaching point: cross-entropy punishes confident errors logarithmically harder — the property that makes gradient descent fix confident mistakes first.

## 2. Backprop by hand (your 2-layer network)

Network: `h = relu(W1x + b1)`, `ŷ = W2h + b2`, loss `L = (ŷ − y)²`. For one sample:

```python
# forward (file 01 §1):
# z1 = W1x + b1 = [-0.6, 0.8, 0.0];  h = relu(z1) = [0, 0.8, 0]
# z2 = W2h + b2 = -0.19;             L = (ŷ - y)² = (−0.19 − y)²

# backward — the chain rule, stage by stage:
# dL/dŷ = 2(ŷ − y)
# dL/dW2[i] = dL/dŷ · h[i]             (ŷ = W2·h + b2 → ∂ŷ/∂W2[i] = h[i])
# dL/dh[i]  = dL/dŷ · W2[i]            (only where h[i] > 0 — ReLU gate!)
# dL/dW1[i,j] = dL/dh[i] · x[j]        (through the ReLU: zero where z1 ≤ 0)
```

The ReLU gate is the key subtlety: where `z1 ≤ 0`, the gradient through that neuron is **exactly zero** — the "dead neuron" mechanism (file 01 §4) and the reason gradients vanish through saturated layers.

## 3. Autograd verification

```python
import torch, torch.nn as nn

model = nn.Sequential(nn.Linear(2, 3), nn.ReLU(), nn.Linear(3, 1))
# copy your hand-computed W1/W2 into the model:
with torch.no_grad():
    model[0].weight.copy_(torch.tensor(W1)); model[0].bias.copy_(torch.tensor(b1))
    model[2].weight.copy_(torch.tensor(W2.T)); model[2].bias.copy_(torch.tensor(b2))

x = torch.tensor([[1.0, 2.0]]); y = torch.tensor([[1.5]])
loss = nn.MSELoss()(model(x), y)
loss.backward()

print(model[0].weight.grad)     # compare against your hand-derived dL/dW1
print(model[2].weight.grad)     # and dL/dW2
```

If your hand-derived gradients match autograd's to 1e-6, you understand backprop. If they don't — find which chain-rule stage you got wrong (W1-05's verification discipline, mechanistic edition).

## 4. The gradient-norm failure signatures

```python
# per-layer gradient norms during training:
norms = {name: p.grad.norm().item() for name, p in model.named_parameters()}
```

| Signature | Meaning | Fix |
|---|---|---|
| early-layer norms ≪ late-layer norms | vanishing gradients | ReLU/GELU, residuals, better init |
| norms spiking 100× step-over-step | exploding gradients | gradient clipping (`max_grad_norm=1.0`) |
| all norms zero | dead network / detached graph | check the graph, the loss, `requires_grad` |
| one layer's norms ≫ others | LR mismatch for that layer | per-layer LRs or re-architect |

These signatures are the diagnosis table for every training run you'll ever debug (W16-03/04 included).

## Exercises

1. Hand-derive dL/dW2 and dL/dW1 for your network with TWO samples (batch of 2) — verify the averaging.
2. The ReLU gate: set one z1 exactly to 0 — compute the gradient through that neuron by hand; compare with autograd.
3. Depth stress: 5/10/20 sigmoid layers — plot the layer-0/layer-N gradient norm ratio; watch it vanish.
4. Clipping demo: inject a huge gradient; show `clip_grad_norm_` rescaling and the training stability difference.
5. The dead-neuron autopsy: find a ReLU neuron with zero activations across the entire training set; delete it and compare the loss.

## Pitfalls

- **`zero_grad` omitted** — gradients accumulate (W3-03's classic); the loss curve looks like learning but isn't
- **Hand-derivation with the wrong loss derivative** — `dL/dŷ = 2(ŷ−y)` for MSE (with the 2), not `(ŷ−y)`
- **Forgetting the ReLU mask in the backward pass** — the gradient is zero where the pre-activation was negative
- **Detached tensors** — `.detach()`/`torch.no_grad()` in the middle of the graph silently cuts backprop
- **Comparing gradient norms across different losses** — MSE and CE norms aren't comparable; normalize per-task

## Resources

- W3-03 parent, W16-03 (training at scale), E10-02 (gradient inspection as probing) — composed here
- 3Blue1Brown, *Backpropagation* — the visual chain rule
- Karpathy, *micrograd* — backprop built from scratch in ~100 lines
