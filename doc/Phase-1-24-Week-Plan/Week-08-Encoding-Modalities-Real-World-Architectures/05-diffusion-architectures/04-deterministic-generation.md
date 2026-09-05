# Deterministic Generation — Seeds, Steps, Guidance Sweeps

**What you'll learn:** turn generation from slot machine into instrument:
seed discipline, the step/quality curve, and sweep methodology that produces
committable artifacts instead of screenshots.

## 1. Seed discipline — three rules

```python
import torch

def seeded_generator(seed: int, device: str = "cpu") -> torch.Generator:
    g = torch.Generator(device)          # device-bound: cpu gen ≠ cuda gen
    g.manual_seed(seed)
    return g
```

1. **One generator per run**, passed explicitly — the pipeline's default
   RNG is unseeded global state.
2. **Device-bound**: `Generator("cpu")` and `Generator("cuda")` with the
   same seed produce *different* draws; record device with the seed.
3. **Log the full tuple** (seed, device, steps, guidance, size, model) —
   a seed alone does not reproduce anything:

```python
RUN = {"seed": 42, "device": "cpu", "steps": 30, "guidance": 7.0,
       "size": [512, 512], "model": "runwayml/stable-diffusion-v1-5",
       "scheduler": "PNDM"}
```

## 2. The step/quality curve, measured not assumed

```python
from diffusers import StableDiffusionPipeline
import time, pandas as pd

pipe = StableDiffusionPipeline.from_pretrained(RUN["model"], torch_dtype=torch.float32)
rows = []
for steps in [10, 20, 30, 50]:
    t0 = time.perf_counter()
    img = pipe("a clean architecture diagram", num_inference_steps=steps,
               guidance_scale=7.0, generator=seeded_generator(42)).images[0]
    rows.append({"steps": steps, "sec": round(time.perf_counter() - t0, 1)})
    img.save(f"reports/gen-steps-{steps}.png")
print(pd.DataFrame(rows))
```

Expected shape: quality rises steeply 10→30, flattens by 50; time is
linear in steps. The capstone default (30) is the knee — 50 buys little
and costs 67% more.

## 3. Guidance sweeps with fixed seeds

The honest sweep changes *one* knob: same seed, same steps, guidance ∈
{3, 5, 7.5, 10}. What you will see: at 3, loose prompt adherence; at 7.5,
balanced; at 10, saturated contrast and collapsed diversity. Record as a
contact sheet (the Week-07 determinism file's `contact_sheet` — reuse it),
with the run-tuple in the filename:

```text
reports/gen-sweep-g3.0-s42.png … gen-sweep-g10.0-s42.png
```

## 4. Generation as a pipeline step (when you actually need it)

| Use case | Determinism level | Implementation |
|---|---|---|
| demo slide images | byte-exact | pre-generate, commit the PNG, keep the run tuple |
| corpus augmentation (synthetic data) | seeded per unit | seed = hash(unit_id) |
| creative demo ("generate an image of X") | none | fine — say so in the demo script |

```python
import hashlib

def unit_seed(unit_id: str) -> int:
    return int(hashlib.sha256(unit_id.encode()).hexdigest()[:8], 16)
```

Seed-from-unit-id makes synthetic augmentation *reproducible per corpus
unit* — the same discipline as every cache key in this program.

## Exercises

1. Reproduce-or-fail: with a logged run tuple, regenerate an image and hash
   both PNGs; they must match byte-for-byte on the same device/dtype. Then
   switch dtype fp32→fp16 and observe the hash break — document that dtype
   is part of the tuple.
2. Step-curve lab: run the §2 script; plot the time column; view the four
   images side by side and write where *you* see the knee.
3. Augmentation seed drill: build seeds for 10 unit_ids via `unit_seed`;
   regenerate twice and confirm per-unit determinism.

## Pitfalls

- Seeding via `torch.manual_seed` globally — other library calls (dataloader
  shuffles) consume the same stream; scoped generators only.
- Sweeping two knobs at once (steps AND guidance) — the 2-D grid is 9× the cost
  and unattributable; one knob per sweep.
- Treating GPU vs CPU generation as interchangeable for reproduction — same
  seed, different kernels, different pixels; log the device.

## Resources

- diffusers `torch.Generator` docs; the reproducibility note in the diffusers docs.
- Your Week-07 determinism file — `seed_everything` and `contact_sheet` reuse.
