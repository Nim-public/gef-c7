# Deep-Dive: Diffusion Architectures

Parent overview: [`../05-diffusion-architectures.md`](../05-diffusion-architectures.md)

Diffusion is the only *generation* architecture in the core program, so this
subfolder builds it from the math you can verify: noise schedules computed
by hand, the latent-diffusion cost trick, a pipeline disassembled into its
components, and the determinism controls that make generation a reproducible
engineering artifact.

## File map

| File | What it covers |
|---|---|
| [`01-forward-reverse.md`](01-forward-reverse.md) | Forward/reverse processes, noise schedules by hand |
| [`02-latent-diffusion.md`](02-latent-diffusion.md) | VAE, U-Net/DiT, cross-attention conditioning |
| [`03-pipeline-anatomy.md`](03-pipeline-anatomy.md) | Components, knobs, safety checker, memory |
| [`04-deterministic-generation.md`](04-deterministic-generation.md) | Seeds, steps, guidance sweeps — reproducibility |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-forward-reverse.md` — the two processes and the schedule.
2. `02-latent-diffusion.md` — why pixels are the wrong workspace.
3. `03-pipeline-anatomy.md` — the code you will actually run.
4. `04-deterministic-generation.md` — turn generation into an experiment.

## Prerequisites

- [`../01-encoding-text-images/02-cnn-mechanics.md`](../01-encoding-text-images/02-cnn-mechanics.md)
  — the U-Net's building blocks.
- Week 03 (attention) — the conditioning mechanism.
