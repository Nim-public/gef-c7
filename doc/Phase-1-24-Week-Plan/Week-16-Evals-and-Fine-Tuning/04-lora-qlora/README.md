# Deep-Dive: LoRA & QLoRA

Parent overview: [`../04-lora-qlora.md`](../04-lora-qlora.md)

Parameter-efficient fine-tuning: the LoRA low-rank delta, the adapter
config (targets, r, alpha, dropout), QLoRA's 4-bit base training on one
GPU, and the parity checks between merged and adapter serving.

## File map

| File | What it covers |
|---|---|
| [`01-lora-math.md`](01-lora-math.md) | Low-rank delta, parameter counting |
| [`02-adapter-config.md`](02-adapter-config.md) | Targets, r, alpha, dropout |
| [`03-qlora.md`](03-qlora.md) | 4-bit base training on one GPU |
| [`04-parity-checks.md`](04-parity-checks.md) | Merged vs adapter serving |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-lora-math.md` — the math that explains the savings.
2. `02-adapter-config.md` — the knobs and their effects.
3. `03-qlora.md` — the single-GPU reality.
4. `04-parity-checks.md` — prove merged ≡ adapter.

## Prerequisites

- [`../03-fine-tuning-fundamentals/`](../03-fine-tuning-fundamentals/)
  — the SFT data, loop, and diagnosis this efficiency layer wraps.