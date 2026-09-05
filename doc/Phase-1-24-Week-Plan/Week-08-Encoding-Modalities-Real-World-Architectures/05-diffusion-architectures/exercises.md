# Exercises — Diffusion Architectures

Expanded set with worked approaches. CPU-friendly: every experiment is ≤ 50
steps on a small pipeline; the by-hand math needs only numpy.

## 1. Schedule lab, extended (from 01-forward-reverse)

**Task:** plot `ᾱ_t` for linear and cosine schedules on one figure; mark
where each crosses 0.5 (the "half-destroyed" step); compute the signal
coefficient `√ᾱ` at t=100 for both.

**Worked approach:** `np.searchsorted(alpha_bar, 0.5)` gives the crossing
step (linear ≈ 285, cosine ≈ 320). The coefficient at t=100: linear `√ᾱ ≈
0.95`, cosine slightly higher — the cosine schedule's "gentle start".

**Pass criterion:** the two curves on one axes with crossings marked; the
t=100 coefficients in a table.

## 2. Reverse-step correctness proof (from 01)

**Task:** the cheat-mode drill from file 01, extended: run 1000 reverse
steps with the *true* noise fed back; measure final reconstruction error
(`MSE(x0_hat, x0)`). Then corrupt one step's `ε_pred` by 10% and remeasure —
write down how error propagates.

**Worked approach:** with perfect predictions, error ≈ 0 (the step is exact
given `ε`); a single 10% corruption introduces a bounded deviation that
subsequent steps partially correct — the empirical justification for why
learned ε with ~90% accuracy still produces coherent images.

**Pass criterion:** two MSE numbers + one sentence interpreting the
robustness.

## 3. VAE roundtrip quality (from 02-latent-diffusion)

**Task:** encode/decode 5 processed images; compute PSNR between original
and reconstruction; view side-by-side.

**Worked approach:**

```python
with torch.no_grad():
    lat = vae.encode(img).latent_dist.mode() * vae.config.scaling_factor
    rec = vae.decode(lat / vae.config.scaling_factor).sample.clamp(-1, 1)
psnr = -10 * torch.log10(((rec - img) ** 2).mean())
```

Expect PSNR ≈ 20–24 dB: visibly-near-identical but lossy. Note *what* is
lost (fine text, small patterns) — exactly why OCR runs on pixels, never on
VAE decodes.

**Pass criterion:** 5 PSNRs + one loss-mode observation each.

## 4. The deterministic demo image (from 03-pipeline-anatomy, 04)

**Task:** produce your capstone's demo image: pick prompt/negative/steps/
guidance/seed, log the full run tuple, generate, then regenerate and assert
byte-identity (`sha256` of both PNGs).

**Worked approach:** the assertion is the deliverable — a `tests/
test_generation_reproducible.py` that rebuilds the image from the committed
run tuple and compares hashes (skip if the model is not downloaded, with a
visible skip reason).

**Pass criterion:** green test on the same machine; a documented
device/dtype caveat for cross-machine reproduction.

## 5. Capstone: the generation decision (from all files)

**Task:** one-paragraph addition to the encoder decision memo: is
generation *in* your capstone? If yes: which pipeline, which run tuples,
where the artifacts are committed. If no: one sentence naming the eval
result that would revisit the decision.

**Worked approach:** for most GEF C7 capstones the answer is "demo garnish
only" — pre-generated, seeded, committed. Writing the no-case down is as
valuable as the yes: it prevents week-14 scope creep.

**Pass criterion:** the memo paragraph exists with a trigger or a decision
and cites the artifacts from exercise 4.

## Pitfalls recap

- PSNR on [-1,1] vs [0,1] tensors — normalization errors of 2× distort every PSNR; state the range.
- Sweep images saved over each other — filenames carry the run tuple or the sweep is lost.
- "Reproducible" claims without the assertion — a seed you have not tested is a hope, not a property.
