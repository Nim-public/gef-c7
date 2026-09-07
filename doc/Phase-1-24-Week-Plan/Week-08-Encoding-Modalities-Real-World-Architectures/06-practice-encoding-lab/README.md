# Deep-Dive: Practice — Cross-Modal Encoding Lab

Parent deliverable spec: [`../06-practice-encoding-lab.md`](../06-practice-encoding-lab.md)

The parent defines experiments A–E and the encoder decision note. This
subfolder is the build guide: each experiment as a runnable lab with
acceptance criteria, and the decision note as a template you can fill with
your own numbers.

## File map

| File | What it covers |
|---|---|
| [`01-geometry-lab.md`](01-geometry-lab.md) | ResNet vs ViT embedding geometry on your domain |
| [`02-clip-matrix-lab.md`](01-geometry-lab.md) | CLIP matrix + retrieval metrics on your pairs |
| [`03-fusion-ablation-lab.md`](03-fusion-ablation-lab.md) | Missing-modality robustness on a real head |
| [`04-encoder-decision-note.md`](04-encoder-decision-note.md) | The capstone integration memo, with template |
| [`exercises.md`](exercises.md) | Stretch tasks and the self-review rubric |

## Lab order (each lab feeds the decision note)

1. `01-geometry-lab.md` — pick the image encoder.
2. `02-clip-matrix-lab.md` — measure cross-modal retrieval, the capstone core.
3. `03-fusion-ablation-lab.md` — stress the fusion you chose in file 03.
4. `04-encoder-decision-note.md` — write the numbers down, decide, move on.

## Prerequisites

- [`../01-encoding-text-images/`](../01-encoding-text-images/) — encoders + token math.
- [`../04-clip-blip-architectures/`](../04-clip-blip-architectures/) — the CLIP matrix.
- [`../03-modality-fusion/01-early-fusion.md`](../03-modality-fusion/01-early-fusion.md)
  — the ablation harness.
