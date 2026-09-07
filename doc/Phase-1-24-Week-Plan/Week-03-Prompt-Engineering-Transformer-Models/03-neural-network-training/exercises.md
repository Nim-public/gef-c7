# Exercises — Neural Network Training

> Subfolder index: [README.md](README.md) · Parent: [../03-neural-network-training.md](../03-neural-network-training.md)

Labs for this subfolder. Shared fixture: the sin-fitting task (file W3-03) and the Rosenbrock valley (file 02).

---

## E1 — Mechanics mastery (file 01)

1. Hand-compute a 2-layer forward pass for 2 inputs; verify against NumPy and PyTorch to 1e-6.
2. The collapse proof: train linear-stack vs ReLU-stack on `y=sin(3x)` — plot both; the linear one underfits visibly.
3. Parameter census: Qwen2.5-0.5B from its config — total params reconciled to ~494M within 1%.
4. Dead-neuron census: train with ReLU; count neurons that never activate across the training set; delete them and measure the loss change.

**Worked approach:** exercise 3's reconciliation is the memory-planning skill (W15-03) — the formula per layer type, summed, checked.

## E2 — Backprop forensics (file 02)

1. Hand-derive dL/dW2 and dL/dW1 for a batch of 2; verify against autograd to 1e-6.
2. The ReLU-gate drill: set one pre-activation to exactly 0; verify the gradient through it is 0 (subgradient).
3. Depth stress: 5/10/20 sigmoid layers — the layer-0/layer-N norm ratio table; watch it vanish.
4. Loss-derivative drill: derive dL/dz for MSE and cross-entropy (with softmax) — show why cross-entropy's gradient simplifies to (p − y).

**Worked approach:** exercise 4's simplification (softmax+CE → p−y) is why classification training is numerically stable — derive it once and it's permanent.

## E3 — The optimizer race (file 03)

1. Three optimizers on Rosenbrock: same init, 2000 steps — loss curves and contour trajectories; rank with reasons.
2. LR sweep per optimizer: find each divergence threshold; rank the stability ranges.
3. State-memory audit: instrument each optimizer to report state bytes — verify SGD=0, momentum=1×, Adam=2× per parameter.
4. AdamW vs Adam+L2: implement both; compare on a weight-decay-sensitive task.

**Worked approach:** exercise 2's divergence thresholds are the LR-safety evidence — the table that justifies your production LR choices (W16-03).

## E4 — Schedules and stability (file 04)

1. Warmup A/B: with vs without on large-init logits — early divergence shown and fixed.
2. Schedule race: constant/linear/cosine — final loss and smoothness at equal steps.
3. Clipping boundary: binary-search the `max_norm` where training stabilizes on a spiky loss; verify gradients are rescaled, not zeroed.
4. The diagnosis drill: three prepared broken runs (high LR, leakage, dead ReLUs) — diagnose each from curves and norms alone, no source peeking.

**Worked approach:** exercise 4's drill is the training-debugging skill in its purest form — the same skill that saves a W16-04 fine-tuning run at 3 a.m.

## Self-assessment

- Can you compute a forward pass and its gradients by hand for a 2-layer network?
- Can you diagnose a broken training run from its loss curve and gradient norms alone?
- Can you state each optimizer's state-memory cost and its stability range from memory?
