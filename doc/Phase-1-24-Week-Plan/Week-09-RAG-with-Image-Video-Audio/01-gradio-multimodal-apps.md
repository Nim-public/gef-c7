# 01 — Gradio Multimodal Applications

> Week 9 index: [README.md](README.md)

**Session 1 topics:** *Multimodal Gradio Application Deployment. Introduction to Gradio and Features of Gradio. Smart Food Image Generator with Gradio. Smart Product Cataloger with Gradio.*

---

## What you'll learn

- Gradio's model: Interface vs Blocks, components, events, queues, deployment
- App 1: a text→image generator with model cards and controls
- App 2: a product cataloger — image in → classified, captioned, priced, logged
- Deployment patterns: local, Spaces, and the loading/caching rules

## 1. Gradio in one page

Gradio turns a Python function into a shareable web UI — the standard demo layer for every ML artifact in this program (and Week 16's capstone demo).

```python
import gradio as gr

def greet(name, intensity):
    return "Hello " + name * intensity

demo = gr.Interface(
    fn=greet,
    inputs=[gr.Textbox(label="Name"), gr.Slider(1, 5, value=2, step=1)],
    outputs=gr.Textbox(label="Greeting"),
)
demo.launch()          # local URL; share=True -> temporary public link
```

| Concept | What it gives you |
|---|---|
| `gr.Interface` | one function in, one out — the 80% case |
| `gr.Blocks` | multi-step layouts, state, custom flows (chat UIs) |
| Components | `Image`, `Audio`, `Video`, `Textbox`, `ChatInterface`, `Gallery`, `DataFrame` — typed in/out |
| `examples=` | one-click sample inputs (the fastest way to look professional) |
| Queue | request serialization for slow models (`demo.queue()`) |
| `share=True` | public tunnel for demos (temporary) |
| State | `gr.State` for per-session memory (chat history) |

Model loading rule: **load once at module level**, not inside the function — Gradio reloads per request otherwise. Heavy models + `demo.queue()` + `max_threads` control concurrency.

## 2. App 1 — Smart Food Image Generator

Text → image via diffusion (W2-04/W8-05), with food-domain prompt scaffolding:

```python
import torch
import gradio as gr
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", dtype=torch.float32)
pipe.to("cpu")                                   # Spaces: "cuda" on GPU hardware

FOOD_STYLES = ["professional food photography", "top-down flat lay", "rustic wooden table"]

def generate_food_image(dish: str, style: str, guidance: float, seed: int):
    prompt = f"{dish}, {style}, appetizing, natural light, high detail"
    gen = torch.Generator("cpu").manual_seed(seed)
    return pipe(prompt, negative_prompt="blurry, text, watermark, people",
                num_inference_steps=25, guidance_scale=guidance, generator=gen).images[0]

demo = gr.Interface(
    fn=generate_food_image,
    inputs=[gr.Textbox(label="Dish", value="masala dosa with chutney"),
            gr.Dropdown(FOOD_STYLES, value=FOOD_STYLES[0]),
            gr.Slider(2, 12, value=7.5, label="Guidance"),
            gr.Number(value=42, label="Seed")],
    outputs=gr.Image(label="Generated dish"),
    examples=[["paneer tikka", FOOD_STYLES[1], 7.5, 7]],
    title="Smart Food Image Generator",
)
demo.queue(max_threads=2).launch()
```

Engineering notes: fixed **seed** control (W8-05's determinism), negative prompts, `queue` for a CPU-bound pipe, examples for one-click demos. On CPU each image takes ~1–3 min — set expectations in the UI text, and cache `pipe` once.

## 3. App 2 — Smart Product Cataloger

Image in → **classify** (CLIP zero-shot, W2-04) → **describe** (BLIP, W8-04) → **price/stock lookup** (SQLite from Week 6) → **catalog entry** logged as JSONL:

```python
import json, sqlite3, datetime
import gradio as gr
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image

clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
cproc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
blip = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").eval()
bproc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

LABELS = [f"a photo of a {x}" for x in ["keyboard", "laptop", "headphones", "mouse", "monitor"]]
CAT_PRICES = {"keyboard": 4500, "laptop": 55000, "headphones": 3000, "mouse": 1200, "monitor": 12000}
DB = sqlite3.connect("file:capstone.db?mode=ro", uri=True)      # read-only (W6-02)

def catalog(image):
    inputs = cproc(text=LABELS, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        out = clip(**inputs)
    probs = out.logits_per_image.softmax(dim=1)[0]
    category = LABELS[int(probs.argmax())].removeprefix("a photo of a ")

    b_in = bproc(image, return_tensors="pt")
    caption = bproc.decode(blip.generate(**b_in, max_new_tokens=30)[0],
                           skip_special_tokens=True)

    row = DB.execute("SELECT price, stock FROM products WHERE category = ? LIMIT 1",
                     (category,)).fetchone()
    entry = {"ts": datetime.datetime.now().isoformat(), "category": category,
             "confidence": float(probs.max()), "caption": caption,
             "price": row[0] if row else None, "stock": row[1] if row else None}
    with open("catalog_entries.jsonl", "a", encoding="utf-8") as f:   # W1-04 JSONL logging
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {l: float(p) for l, p in zip(LABELS, probs)}, caption, entry

demo = gr.Interface(
    fn=catalog,
    inputs=gr.Image(type="pil", label="Product photo"),
    outputs=[gr.Label(num_top_classes=3, label="Category"),
             gr.Textbox(label="Generated description"),
             gr.JSON(label="Catalog entry")],
)
demo.queue().launch()
```

This app is your Week 9 pipeline in miniature: **encode → classify → describe → structured lookup → persist** — exactly the ingestion pattern file 04 scales to the whole corpus.

## 4. Deployment patterns

| Target | How | Notes |
|---|---|---|
| Local demo | `demo.launch()` | dev loop; LAN via `server_name="0.0.0.0"` |
| Public demo | `share=True` (temporary tunnel) | 72 h link — fine for Office Hours |
| **HF Spaces** | push `app.py` + `requirements.txt` + `README.md` (yaml header: `sdk: gradio`) | persistent; hardware tiers (CPU free) |
| Behind your API | `FastAPI` + gradio `mount_gradio_app` | embed in the capstone app |

Spaces gotchas: model files download on *startup* (first boot is slow — pin revisions), CPU free tier means fp32 + small models, secrets via Space settings (not code).

## Exercises

1. Extend the cataloger: low-confidence path — if `probs.max() < 0.6`, return "Uncertain — please tag manually" (W5-04's confidence hook, in UI form).
2. Add a `gr.ChatInterface` front page that answers "what is this product?" by calling the cataloger + a small LLM (W1-07). Keep history in `gr.State`.
3. Space it: deploy the cataloger to HF Spaces. First-boot time? Add a startup log line showing model load duration.
4. Cataloger → indexer: every saved JSONL entry appends to your Week 4 LanceDB/BM25 index (call your `ingest.py`). The demo is now feeding the RAG corpus.
5. UI audit: run the food generator with 3 seeds at fixed prompt — are results consistent enough for a "menu" use case? What does that imply about generation in product pipelines?

## Pitfalls

- **Model loads inside the handler** — seconds added per click, GPU re-allocations; module-level load only
- **`share=True` links treated as production** — they expire and are public; Spaces or your server for anything real
- **Blocking handlers without `queue()`** — UI freezes under concurrency
- **Uploading user media into git/HF repos** — privacy + size; store references (W7-01 manifest rule)
- **fp16 models on free CPU Spaces** — crashes/NaNs; fp32 or a smaller checkpoint

## Resources

- [Gradio docs](https://www.gradio.app/docs) — Interface, Blocks, ChatInterface guides
- [HF Spaces docs](https://huggingface.co/docs/hub/spaces) — config, secrets, hardware
- Diffusers [text-to-image](https://huggingface.co/docs/diffusers/using-diffusers/conditional_image_generation) guide (UI integration notes)
- Your own Week 2 apps — revisit and Gradio-ify one per remaining week
