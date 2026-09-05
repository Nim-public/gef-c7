# Latent Diffusion — VAE, U-Net/DiT, Cross-Attention Conditioning

**What you'll learn:** the affordability trick that made diffusion practical:
run diffusion in a compressed latent space, condition via cross-attention,
and the two backbone families (U-Net, DiT) that do the denoising.

## 1. The VAE compression, measured

```python
from diffusers import AutoencoderKL
import torch

vae = AutoencoderKL.from_pretrained("runwayml/stable-diffusion-v1-5", subfolder="vae")
img = torch.rand(1, 3, 512, 512)
with torch.no_grad():
    latents = vae.encode(img).latent_dist.sample() * vae.config.scaling_factor
print(latents.shape)      # (1, 4, 64, 64) — 48× fewer numbers than (3, 512, 512)
```

Compression 3·512·512 = 786k → 4·64·64 = 16k floats: **48× fewer**. Every
denoising step now costs 1/48th. The quality price is small because the VAE
keeps perceptual structure and discards high-frequency detail the U-Net
never needed. Decode with `vae.decode(latents / vae.config.scaling_factor)`.

## 2. The U-Net: multi-scale denoiser

The U-Net (from the CNN file's hourglass) downsamples then upsamples with
skip connections — at 4 scales for SD1.5:

| Scale | Resolution | Blocks | Role |
|---|---|---|---|
| 0 | 64² | 2 res + 2 attn | fine detail, low-level noise |
| 1 | 32² | 2 res + 2 attn | mid structure |
| 2 | 16² | 2 res + 2 attn | coarse structure, most compute |
| 3 | 8² | 3 res + 0 attn | bottleneck, global layout |

Params: ~860M, but FLOPs concentrate in mid scales — the reason SD runs at
seconds, not minutes. The timestep embedding `ε_θ(x_t, t, c)` enters every
res-block (sinusoidal t → MLP → added to activations).

## 3. Cross-attention conditioning — the text hookup

The prompt (CLIP text embeddings, 77×768) conditions the U-Net through
cross-attention in every scale-1/2 attention block — the Q/K/V framing from
the fusion file, exactly:

```python
# inside each attention block (conceptually):
q = x @ Wq                       # spatial positions ask
k, v = prompt_emb @ Wk, prompt_emb @ Wv
attn = softmax(q @ k.T / sqrt(d))
x = x + attn @ v                 # prompt content flows in
```

Each spatial location reads whichever prompt tokens are relevant *at that
denoising step* — this is why composition ("a red cube on a blue sphere")
binds attributes to locations, imperfectly. Classifier-free guidance then
amplifies the text direction:

```text
ε̂ = ε_uncond + s · (ε_cond − ε_uncond)        guidance scale, typically 5–8
```

## 4. DiT — the transformer challenger

DiT (used by SD3, Flux, Sora-class) replaces the U-Net with a plain
transformer over *patched latents*: 64² latents with patch=2 → 1024 tokens,
one transformer, adaLN (timestep/prompt modulation instead of conv skips).
Trade table:

| Property | U-Net (SD1.5) | DiT (SD3-class) |
|---|---|---|
| Inductive bias | local, multi-scale | global, learned |
| Compute scaling | resolution-bounded | token count² |
| Scaling-law behavior | flattens | keeps improving |
| Your capstone relevance | what you can run on CPU/GPU-free | what the frontier uses |

## Exercises

1. Compression audit: compute the latent-space memory for a 1024×1024
   image at SD1.5's VAE; then compute how many such latents fit in 2 GB.
2. Guidance drill: implement `eps_hat` with scale ∈ {1, 5, 8, 15} (conceptually);
   at scale 1 you get uncond — verify the collapse by sampling with a fixed
   seed and comparing image "variety" across scales (report as a table).
3. Token math: patch=2 on 64² latents → 1024 tokens; compute DiT attention
   pairs vs the U-Net's scale-2 attention (16²=256 tokens) — the cost of
   "global, learned".

## Pitfalls

- Forgetting `scaling_factor` — encode without it and your "latents" are ~4× off-scale; the diffusion model sees out-of-distribution noise forever.
- Believing "U-Net = old" — SDXL/SD1.5 U-Nets are what your hardware runs; DiT is the research frontier, not your CPU demo.
- Guidance scale 20+ "for prompt adherence" — saturation artifacts; the sweet spot is 5–8 for SD1.5-class models.

## Resources

- Rombach et al. 2022 (Latent Diffusion) §3 (the 48× number's source).
- Peebles & Xie 2023 (DiT); Esser et al. 2024 (SD3, rectified flow + DiT).
