# 05 — Diffusion Architectures

> Week 8 index: [README.md](README.md)

**Session 2 topic:** *Diffusion (architecture-level understanding — usage was covered in Week 2).*

---

## What you'll learn

- The forward (noising) and reverse (denoising) processes — what "diffusion" actually computes
- The training objective (predict the noise) and why it's stable
- Latent diffusion: the VAE + U-Net/DiT + text-conditioning stack that makes 512² generation affordable
- How text conditioning enters (cross-attention — file 03's fusion, again)
- The component anatomy of a `diffusers` pipeline you already ran

## 1. Two processes

**Forward (training only)** — progressively add Gaussian noise until the image is pure noise:

```
x_0 (image) → x_1 → x_2 → … → x_T (noise)
q(x_t | x_{t-1}) = N( x_t ; √(1−β_t)·x_{t-1} , β_t·I )      β_t: small noise schedule
```

Closed-form shortcut lets you jump to any `t` directly — so training samples random `(x_0, t)` pairs cheaply.

**Reverse (generation)** — a network learns to *denoise one step*:

```
x_T → x_{T-1} → … → x_0        p_θ(x_{t-1} | x_t) — the U-Net/DiT predicts the noise ε
```

**Training objective** is remarkably simple: at random `t`, add noise to get `x_t`, ask the network to predict that noise, MSE loss against it. No adversary (GANs), no unstable game — just regression. That stability is why diffusion took over generation.

The generation loop you ran in W2-04 (`num_inference_steps=25`) is this reverse chain, stepped 25 times, with the text embedding steering every step.

## 2. Latent diffusion — the affordability trick

Denoising in pixel space (512×512×3) at every step is expensive. **Latent diffusion** compresses first:

```
image x ──[VAE encoder]──► z (64×64×4 latent) ──[diffusion happens HERE]──► z' ──[VAE decoder]──► image
```

The **VAE** (variational autoencoder) is a two-part autoencoder trained to compress images ~48× (512·512·3 → 64·64·4) while staying decodable. All the expensive denoising happens in that small latent. This one design choice is why a laptop can generate images at all.

## 3. The full pipeline anatomy

```python
import torch
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", dtype=torch.float16)
print(pipe)                    # the anatomy, printed
```

Components (every text-to-image system since 2022 is some arrangement of these):

| Component | Role | Notes |
|---|---|---|
| **Text encoder** (CLIP text tower) | prompt → 77×768 conditioning embeddings | the semantic steering signal |
| **VAE encoder/decoder** | image ↔ latent | compression boundary (§2) |
| **U-Net** (or **DiT** transformer) | predicts noise ε at each step | the trained denoiser; cross-attention to text |
| **Scheduler** | the noise schedule + step size rule (DDIM, Euler…) | `num_inference_steps`, determinism via `generator` |
| **Safety checker** (optional) | NSFW filter | can be disabled — note the responsibility |

**Text conditioning via cross-attention** (file 03, again): inside the U-Net, every block runs cross-attention where the *image latents* are queries and the *prompt embeddings* are keys/values. `guidance_scale` then amplifies the text signal at sampling time — high values trade diversity for prompt adherence (the knob you swept in W2-04, now explained).

### Variants worth naming

- **img2img**: start the reverse chain from a *noised real image* (strength knob = how much of the original survives)
- **inpainting**: mask-aware denoising of a region
- **ControlNet**: inject spatial conditioning (edges, pose) as extra attention branches
- **SDXL/Flux/DiT-class**: bigger backbones; transformer (DiT) replacing U-Net — same recipe, different denoiser architecture

## 4. Reading a generation as engineering

```python
gen = torch.Generator("cpu").manual_seed(42)
img = pipe("a product photo of a mechanical keyboard, studio lighting",
           negative_prompt="blurry, watermark, text",
           num_inference_steps=30, guidance_scale=7.5, generator=gen).images[0]
```

| Knob | Effect | Failure when abused |
|---|---|---|
| `num_inference_steps` ↓ | faster, coarser | <20 visible artifacts |
| `guidance_scale` ↑ | sticks to prompt | oversaturated, burned-in artifacts |
| `negative_prompt` | steer away from features | over-negation warps composition |
| `seed` fixed | reproducible generation | — (evals need this) |
| prompt structure | "subject, style, lighting, quality" | long comma-soup ≠ better |

## Exercises

1. Forward process by hand: `x0 = ones(8,8)`; add noise for `β=0.01..0.5` in 10 steps (closed form `√(ᾱ)x0 + √(1-ᾱ)ε`); plot the trajectory. Where does structure die?
2. One-step denoiser toy: train a tiny CNN to predict the noise added to 8×8 digit-like patches (MSE). Sample with 5 steps. You've built micro-diffusion.
3. Component surgery: `print(pipe)` — identify the CLIP text encoder's dim, VAE latent shape, U-Net cross-attention dims. Reconcile with the table.
4. Guidance sweep: same prompt+seed at `guidance_scale` 1.5 / 7.5 / 15. Relate the results to the cross-attention mechanism (file 03).
5. Latent math: verify the ~48× compression (512·512·3 bytes → 64·64·4 floats) and compute the attention-cost reduction implied by denoising in latent space.

## Pitfalls

- **fp16 expectations on CPU** (W2-04's note) — latent diffusion in fp32 CPU ≈ minutes/image; plan demos on GPU/Spaces
- **Seedless evals** — unseeded generation makes "improvements" unfalsifiable; fix seeds in every comparison
- **Confusing the VAE with the denoiser** — the VAE is compression, *not* generative; all conditioning happens in latent space
- **Safety-checker removal as a "fix"** — it's a policy decision, document it like the license (W2-04)
- **Treating prompts as code** — diffusion prompts have their own grammar (subject/style/lighting); porting LLM prompt rules verbatim doesn't transfer

## Resources

- Ho et al., *Denoising Diffusion Probabilistic Models* (DDPM, 2020) — §2 + Algorithm 1 are enough
- Rombach et al., *High-Resolution Image Synthesis with Latent Diffusion Models* — §3 (the architecture of §3 here)
- [The Annotated Diffusion Model](https://huggingface.co/blog/annotated-diffusion) (HF blog) — the DDPM paper as runnable code
- [Diffusers docs](https://huggingface.co/docs/diffusers/index) — pipelines, schedulers, conceptual guides
- 3Blue1Brown & Welch Labs diffusion visualizations — intuition-first versions of §1
