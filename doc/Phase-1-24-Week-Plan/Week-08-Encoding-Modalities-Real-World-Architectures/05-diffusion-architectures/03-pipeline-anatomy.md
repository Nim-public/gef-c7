# Pipeline Anatomy — Components, Knobs, Safety Checker, Memory

**What you'll learn:** the actual object you will run (`StableDiffusionPipeline`)
taken apart: every component, every knob you will touch, the safety checker
you will likely disable (and why that matters), and the memory math.

## 1. The components, by name

```python
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
print(pipe)          # six components:
# text_encoder   CLIPTextModel            prompt → 77×768
# tokenizer      CLIPTokenizer            prompt → ids
# vae            AutoencoderKL            latents ↔ pixels
# unet           UNet2DConditionModel     the denoiser (~860M)
# scheduler      PNDMScheduler            the t/w noise schedule
# safety_checker StableDiffusionSafetyChecker  NSFW gate
# feature_extractor (for the checker)
```

Memory (fp16): U-Net 1.7 GB, VAE 0.16, text encoder 0.24, checker 1.2
(fp32!) — the safety checker is often the *second largest* component.

## 2. The knobs, from most- to least-used

| Knob | Default | Effect | When to change |
|---|---|---|---|
| `num_inference_steps` | 50 | quality vs time | 20–30 for drafts, 50 final |
| `guidance_scale` | 7.5 | prompt adherence | 5–8; >12 over-saturates |
| `generator` | None | seed | always, for reproducibility |
| `negative_prompt` | None | what to avoid | always: "blurry, watermark, text" |
| `height/width` | 512 | resolution | multiples of 8 (VAE factor) |
| `strength` (img2img) | 0.8 | how much to change | 0.3–0.6 for edits |

```python
gen = torch.Generator("cpu").manual_seed(42)
out = pipe("an architecture diagram of a RAG system, clean lines",
           negative_prompt="blurry, watermark, text artifacts",
           num_inference_steps=30, guidance_scale=7.0, generator=gen)
out.images[0].save("reports/gen-diagram.png")
```

## 3. The safety checker: an engineering decision, not a toggle

`pipe.run_safety_checker` — when it fires, it swaps a black image and logs.
Three honest facts: (1) it is a CLIP-based classifier with known false
positives on benign images (art, skin tones); (2) it doubles memory (fp32);
(3) for a *public* capstone demo, keeping it is the correct default even
with its false positives — the failure mode (a black image at your demo) is
cheaper than the alternative. If you disable it for memory, do it
deliberately and write the reason in the repo:

```python
pipe.safety_checker = None          # memory-only; documented in README
pipe.requires_safety_checker = False
```

## 4. Memory math for your machine

| Setup | VRAM/RAM | How |
|---|---|---|
| fp16, full | ~4 GB | default |
| fp16 + attention slicing | ~2.5 GB | `pipe.enable_attention_slicing()` |
| fp16 + VAE tiling | ~2 GB | `pipe.enable_vae_slicing()` |
| CPU, fp32 | ~8 GB, ~2–4 min/image | your laptop reality |

CPU reality check for the capstone: generation is a *demo garnish*, not a
pipeline component — one 30-step image per demo, pre-generated with a
committed seed (file 04) beats on-demand generation every time.

## Exercises

1. Component inventory: load the pipeline, print every component's param
   count; identify which component your `enable_*` memory flags actually
   affect.
2. Knob sweep: 5 prompts × steps {10, 20, 50} × guidance {5, 7.5}; build the
   3×3 quality/time grid in `reports/diffusion-knobs.md` (save 4 images).
3. Safety-checker cost: measure load time and RAM with and without the
   checker; write the one-paragraph tradeoff for your repo README.

## Pitfalls

- `torch_dtype=torch.float32` by accident (no arg) — 2× memory for nothing.
- Resolutions not divisible by 8 — the VAE silently crops or errors; 8 is the downsample factor (512/64).
- Sweeping guidance without fixed seeds — you are comparing noise draws, not knobs; the generator arg is not optional in experiments.

## Resources

- diffusers docs (`StableDiffusionPipeline` API, memory flags).
- SD1.5 model card — component list and intended-use notes.
