# Deep-Dive: Gradio Multimodal Applications

Parent overview: [`../01-gradio-multimodal-apps.md`](../01-gradio-multimodal-apps.md)

This subfolder turns the two demo apps into engineering: the Gradio
execution model (why `queue=True` is not optional), the diffusion app with
real controls, the cataloger as a composition lesson (CLIP + BLIP + SQLite),
and the deployment patterns that survive a demo day.

## File map

| File | What it covers |
|---|---|
| [`01-gradio-model.md`](01-gradio-model.md) | Interface vs Blocks, events, queue, state |
| [`02-food-image-generator.md`](02-food-image-generator.md) | Diffusion app with knobs, seeds, and guards |
| [`03-product-cataloger.md`](03-product-cataloger.md) | CLIP + BLIP + SQLite — composition patterns |
| [`04-deployment-patterns.md`](04-deployment-patterns.md) | Local, Spaces, API — with cost notes |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-gradio-model.md` — the mental model before any app.
2. `02-food-image-generator.md` — your first heavy-model app.
3. `03-product-cataloger.md` — composing three systems behind one UI.
4. `04-deployment-patterns.md` — get it off your laptop safely.

## Prerequisites

- Week 02 (model loading), Week 07 (explorer — a first Gradio app).
- [`../../Week-08-Encoding-Modalities-Real-World-Architectures/05-diffusion-architectures/03-pipeline-anatomy.md`](../../Week-08-Encoding-Modalities-Real-World-Architectures/05-diffusion-architectures/03-pipeline-anatomy.md)
  — the pipeline this app wraps.
