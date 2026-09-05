# Food Image Generator — Diffusion App with Controls

**What you'll learn:** wrap the Week-08 diffusion pipeline in an app: knobs
that map to pipeline args, seeds that make results shareable, and the
guards (timeouts, size caps) that keep a public demo alive.

## 1. The app, complete

```python
import gradio as gr, torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float32)
pipe.enable_attention_slicing()          # CPU/low-VRAM friendliness

DISHES = ["ramen bowl", "croissant", "thali platter", "tacos", "sushi platter"]

def generate(dish: str, guidance: float, steps: int, seed: int):
    g = torch.Generator("cpu").manual_seed(seed)
    img = pipe(f"professional food photography of {dish}, overhead shot, "
               f"soft light", negative_prompt="blurry, watermark, text",
               guidance_scale=guidance, num_inference_steps=steps,
               generator=g).images[0]
    return img, f"seed={seed} steps={steps} guidance={guidance}"

with gr.Blocks(title="Food Generator") as demo:
    gr.Markdown("## Food image generator — deterministic by seed")
    with gr.Row():
        dish = gr.Dropdown(DISHES, value=DISHES[0], label="Dish")
        seed = gr.Number(value=42, precision=0, label="Seed")
    with gr.Row():
        guidance = gr.Slider(3, 12, value=7.5, step=0.5, label="Guidance")
        steps = gr.Slider(10, 50, value=30, step=5, label="Steps")
    out_img, out_meta = gr.Image(), gr.Textbox(label="Run tuple")
    btn = gr.Button("Generate")
    btn.click(generate, [dish, guidance, steps, seed], [out_img, out_meta])

demo.queue(max_size=8).launch()
```

## 2. The knob-to-UX mapping

| Pipeline arg | UI element | Range rationale |
|---|---|---|
| `guidance_scale` | Slider 3–12 step 0.5 | <3 meaningless, >12 saturated (W8 file 04) |
| `num_inference_steps` | Slider 10–50 step 5 | knee at ~30; bounds protect the queue |
| `seed` | Number, integer | shareable reproducibility (W8 file 04) |
| negative prompt | fixed in code | free-text negatives confuse casual users |

The *returning the run tuple* line is the app's quiet star: every image
displays the tuple that made it — support requests become copy-paste.

## 3. Guards for a public-ish demo

| Guard | Implementation | Failure prevented |
|---|---|---|
| Slider bounds | `gr.Slider(min, max)` | 200-step requests hogging the queue |
| Queue cap | `demo.queue(max_size=8)` | unbounded memory from pending jobs |
| Timeout | `gr.Button` + handler-side time budget | zombie generations |
| Size cap | fixed 512×512 | OOM at 1024² on small machines |

```python
import time
def generate_guarded(dish, guidance, steps, seed):
    t0 = time.perf_counter()
    img, meta = generate(dish, guidance, steps, seed)
    return img, f"{meta} | {time.perf_counter()-t0:.1f}s"
```

Measuring and *displaying* latency sets user expectations — an app that
says "3.2 s" feels faster than one that is silently 3.2 s.

## 4. The determinism claim, tested

The Week-08 test translates: same seed + same args ⇒ same bytes. In app
form, log `(seed, guidance, steps)` with each output image (the meta box)
and keep a `tests/` assertion that regenerates seed 42's default dish —
your demo's fallback image is then reproducible forever.

## Exercises

1. Add a "randomize seed" button that produces a *new* seed and immediately
   generates — one click, no page state (hint: update `gr.Number` then
   chain `.then()`).
2. Add image-to-image mode with a `strength` slider (0.3–0.6); guard that
   an input image is present.
3. Load test: 5 concurrent requests on the queued app; record queue wait vs
   generation time — the two numbers that decide your demo's pacing.

## Pitfalls

- `gr.Number` without `precision=0` — float seeds work but break your
  logged run-tuple convention.
- Reloading the pipeline per request — models load once at module import;
  per-request loads are 100× the latency.
- Sharing the app URL with `share=True` *and* an unbounded queue — a public
  URL is an API; bound everything.

## Resources

- Gradio Blocks guide (Row/Column/Tabs layout).
- Week-08 pipeline anatomy — the knobs this UI exposes.
