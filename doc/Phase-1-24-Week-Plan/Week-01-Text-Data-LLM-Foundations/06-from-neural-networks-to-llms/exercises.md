# Exercises — From Neural Networks to LLMs

> Subfolder index: [README.md](README.md) · Parent: [../06-from-neural-networks-to-llms.md](../06-from-neural-networks-to-llms.md)

Labs for this subfolder. Shared fixture: the sin-fitting task from file 02 and the behavior grid from file 04.

---

## E1 — Mechanics without PyTorch (file 01)

1. Implement `Linear` and `ReLU` with NumPy only; verify against `torch.nn` on identical weights (allclose).
2. Build a 3-layer MLP forward pass in NumPy; count its parameters by hand and programmatically.
3. Collapse-theorem demo: train (a) linear-stack and (b) ReLU-stack on `y=sin(x)` — plot both fits; the linear stack fails visibly.

**Worked approach:** keep the same init seed across both variants; the only difference must be the activation.

## E2 — Training forensics (file 02)

1. Remove `opt.zero_grad()`; plot the loss for 100 steps — reproduce the accumulating-gradient explosion; fix and compare.
2. Gradient-norm monitor: log per-layer grad norms every 10 steps for a 20-layer sigmoid stack — produce the vanishing-gradient table.
3. Divergence hunt: on the sin task, sweep SGD LR ∈ {0.001, 0.05, 0.5, 5.0} — classify each as converging/oscillating/diverging.
4. Checkpoint round-trip: save model+optimizer+step; resume in a fresh process; assert the loss curve continues without a jump.

**Worked approach:** exercise 2's per-layer norm table is the diagnostic that later explains why LoRA targets attention projections (W16-04).

## E3 — Representation probes (file 03)

1. Contextual embedding proof: `"bank"` in 5 sentences — same-sense pairs higher cosine than cross-sense pairs. Table it.
2. Attention depth probe: render attention maps at 4 depths for the animal sentence; identify where coreference routing emerges.
3. Linear probe: 200 labeled sentences (2 classes) on frozen embeddings — report probe accuracy; then fine-tune the whole model briefly and compare.
4. Bias probe: profession↔gender association asymmetries in your chosen model — documented as a model-card note.

**Worked approach:** exercise 3's "probe vs fine-tune" comparison is the cleanest demonstration of what frozen representations already contain (W16-04's LoRA logic, inverted).

## E4 — Selection to deployment (file 04)

1. Complete the 24-cell behavior grid (4 question types × 2 models × 3 temperatures).
2. Card audit: for 3 candidate models, fill the 6-field card checklist; eliminate 2 with reasons.
3. Stopping-behavior measurement: tokens burned per model on the "stop after two sentences" prompt — table it.
4. Write the deployment contract: model id, revision, template, sampling settings, and the behavior-grid evidence attached.

**Worked approach:** exercise 4's contract is the artifact that makes the model selection auditable — the E8-01 manifest's `model` block, pre-filled.

## Self-assessment

- Can you explain the collapse theorem with a 3-line proof-by-construction?
- Can you name the four training-loop lines and the failure each prevents?
- Can you run a base-vs-instruct behavior grid and turn it into a deployment decision?
