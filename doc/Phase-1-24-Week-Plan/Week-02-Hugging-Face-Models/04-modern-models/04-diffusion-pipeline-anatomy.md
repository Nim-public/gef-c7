# 04.4 — Diffusion Pipeline Anatomy

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

---

## What you'll learn

- The component pipeline, printed and explained (W8-05's anatomy, hands-on)
- Deterministic generation: seeds, generators, and reproducibility
- The knob effects quantified: steps, guidance, negative prompts
- img2img and inpainting as variants of the same loop

## 1. The components, printed

```python
import torch
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", dtype=torch.float32)
print(pipe)
# Pipeline components:
#   feature_extractor: CLIPImageProcessor        (image preprocessing)
#   text_encoder: CLIPTextModel                  (prompt → 77×768 conditioning)
#   tokenizer: CLIPTokenizer                     (prompt → tokens)
#   unet: UNet2DConditionModel                   (the denoiser, ~860M)
#   scheduler: PNDMScheduler                     (the step rules)
#   vae: AutoencoderKL                           (image ↔ latent, ~84M)
#   safety_checker: StableDiffusionSafetyChecker (NSFW filter)
```

The data flow (W8-05's §3):

```
prompt ─► tokenizer ─► text_encoder ─► 77×768 conditioning ─┐
                                                             ▼ (cross-attention)
random latent (64×64×4) ─► U-Net denoise × N steps ─► latent ─► VAE decoder ─► image
```

## 2. Deterministic generation

```python
gen = torch.Generator("cpu").manual_seed(42)
img = pipe("a golden retriever reading a book", num_inference_steps=30,
           guidance_scale=7.5, generator=gen).images[0]
```

Same seed + same prompt + same components = identical image. The A/B experiments (W8-05's guidance sweep) are only valid with fixed generators — the W15-03 determinism discipline applied to images. Changing the scheduler changes the noise trajectory even at the same seed — pin the scheduler too when comparing.

## 3. The knobs, quantified

| Knob | Range | Effect | Failure mode |
|---|---|---|---|
| `num_inference_steps` | 10–50 | refinement iterations | <20: artifacts; >50: wasted compute |
| `guidance_scale` | 1–20 | prompt adherence | >15: oversaturated, burned colors |
| `negative_prompt` | avoid-list | steers away | over-negation warps composition |
| `strength` (img2img) | 0–1 | how much of the input survives | low = near-copy, high = new image |

The negative prompt is a second prompt the guidance *pushes away from* — "blurry, watermark, text, extra fingers" encodes the common failure modes.

## 4. img2img and inpainting

```python
# img2img: start the denoising from a noised version of an input image
out = pipe(prompt, image=input_image, strength=0.6, ...).images[0]
# strength 0.2 → minor restyle; 0.8 → mostly new image guided by composition

# inpainting: mask-aware generation inside a region
pipe_inpaint = AutoPipelineForInpainting.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5-inpainting", dtype=torch.float32)
out = pipe_inpaint(prompt, image=base, mask_image=mask, ...).images[0]
```

Both are the same reverse process with a different starting latent — img2img starts from `noise-mix(original)`, inpainting keeps unmasked latents fixed at every step. The conditioning story (W8-05 §3) is identical.

## Exercises

1. Component census: `print(pipe)` — for each component, record parameter count (reconcile ~860M U-Net, ~123M text encoder, ~84M VAE) and its role.
2. Guidance sweep with fixed seed: guidance ∈ {1.5, 4, 7.5, 15} — one grid image; annotate the quality/adherence trade-off per row.
3. Steps-vs-quality: 10/20/30/50 steps at fixed seed — perceptual ranking + time per image; find the knee.
4. img2img strength sweep: 0.2/0.4/0.6/0.8 on the same input — the composition-preservation curve.
5. Prompt A/B: minimal prompt vs structured prompt ("subject, style, lighting, quality") — 3 seeds each; judge which structure wins consistently.

## Pitfalls

- **fp16 dtype on CPU** — crashes/misleading; fp32 on CPU or GPU (W2-04's note)
- **Changing the scheduler mid-comparison** — schedulers define the noise trajectory; pin for fair A/Bs
- **Seed sharing across different models** — the same seed ≠ the same noise layout across architectures; per-model seeds
- **Safety checker removal without policy** — a documented decision (W2-04's licensing note)
- **Committed generated images** — outputs are large and reproducible; store prompts + seeds + configs instead (W7-01's manifest rule)

## Resources

- [Diffusers docs](https://huggingface.co/docs/diffusers/index) — pipelines, schedulers, optimization
- Rombach et al., *Latent Diffusion* (W8-05's source) — §3 architecture
- [Stable Diffusion prompt book](https://stablediffusion.fr/guides/prompts-book) (open community) — prompt structure patterns
- W8-05 (the architecture) — this file's parent concept
