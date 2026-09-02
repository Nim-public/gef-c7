# 04 — Modern Models: CLIP, Whisper, LLMs & Diffusion

> Week 2 index: [README.md](README.md)

**Session 2 topic:** *Modern: OpenClip, OpenWhisper, LLM & Diffusion Model.*

---

## What you'll learn

- **CLIP/OpenCLIP** — matching images to text in one embedding space (Week 8 foundation)
- **Whisper** — speech-to-text with timestamps and translation
- **LLMs via `pipeline`** — local generation with chat templates
- **Diffusion models** — text-to-image generation with `diffusers`
- The hardware/memory thinking that decides what you can run where

## 0. Hardware reality check

Before any download, check fit: **fp16 ≈ 2 bytes/param → params × 2 = GB** (add ~30% overhead). An 8 GB laptop runs ≤ 3 B comfortably; anything bigger needs quantization, CPU offload, or an API. The code below uses small checkpoints that run everywhere.

## 1. CLIP / OpenCLIP — images and text, one space

CLIP trains an image encoder and a text encoder to map matching pairs to nearby vectors. Result: **zero-shot image classification with arbitrary text labels.**

```python
from transformers import pipeline

clip = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")

image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg"
clip(image_url, candidate_labels=["a photo of a car", "a photo of a bicycle", "a photo of a cat"])
# [{'label': 'a photo of a car', 'score': 0.98}, ...]
```

Two ways to use it, both you'll need:

```python
# A) classification (pipeline above) — labels compete, softmax-style scores
# B) raw embeddings for retrieval (Week 9: multimodal RAG)
from transformers import CLIPProcessor, CLIPModel
import requests
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

img = Image.open(requests.get(image_url, stream=True).raw)
inputs = proc(text=["a car", "a bicycle"], images=img, return_tensors="pt", padding=True)
out = model(**inputs)
img_emb = out.image_embeds          # 512-dim — index these in a vector DB
txt_emb = out.text_embeds
```

OpenCLIP (`laion/CLIP-ViT-B-32-laion2B-s34B-b79K`) is the open-data retraining — often stronger on wider domains. Weaknesses to test yourself: counting, negation ("a photo with no car"), fine-grained differences.

## 2. Whisper — speech to text

```python
from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")
# local file:  asr("meeting_clip.wav")
asr("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/1.flac")
# {'text': ' A man said to the universe, sir, I exist.'}
```

- Sizes: `tiny` (39M) → `base` → `small` → `medium` → `large-v3`; accuracy scales, speed inverts. `tiny.en`/`base.en` = English-only (faster); multilingual versions handle 99 languages
- Language tasks: transcription, translation to English (task token), and word **timestamps** (`return_timestamps=True`)
- Alternatives with better speed/accuracy trade-offs exist (`distil-whisper/*` = distilled, ~6× faster)

Why you care now: audio in → text out is the cheapest path into the whole NLP stack. Multimodal RAG (Week 9) indexes transcripts exactly like documents.

## 3. LLMs on the Hub — generation with chat templates

```python
from transformers import pipeline

llm = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")

messages = [
    {"role": "system", "content": "Answer in one short paragraph."},
    {"role": "user", "content": "Explain vector databases to a DBA."},
]
out = llm(messages, max_new_tokens=120, temperature=0.3)
print(out[0]["generated_text"][-1]["content"])   # last message = assistant reply
```

Notes that trip people up:

- `max_new_tokens` (output length), not `max_length` (prompt+output) — prefer the former
- Passing `messages` applies the model's **chat template** automatically (file W1-01)
- The generated history includes your prompt — `[-1]["content"]` extracts just the reply
- Small instruct models to rotate through: `Qwen/Qwen2.5-0.5B-Instruct`, `HuggingFaceTB/SmolLM2-360M-Instruct`, `google/gemma-2-2b-it` (gated)
- For production serving of open LLMs you'll later meet `vLLM` (Week 15); for now, pipeline = your local playground

## 4. Diffusion models — text to image

Diffusion models generate images by **denoising random noise, step by step, guided by the text embedding** (CLIP-style text encoder inside!).

```python
import torch
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5",
    dtype=torch.float16,          # half precision = half memory
)
pipe.enable_attention_slicing()   # CPU/laptop-friendly memory trade
pipe.to("cpu")                    # slow but works; "cuda" if you have a GPU

img = pipe(
    "a photorealistic image of a golden retriever reading a book about transformers",
    num_inference_steps=25,       # fewer steps = faster, rougher
    guidance_scale=7.5,           # how strictly to follow the prompt
).images[0]
img.save("dog_study.png")
```

Key knobs: `num_inference_steps` (quality/latency), `guidance_scale` (prompt adherence vs creativity), `negative_prompt` (things to avoid). Note `dtype=torch.float16` requires a GPU; on CPU-only drop it (slower, same output).

The concept to retain (Weeks 7–9 build on it): diffusion = *iterative refinement in latent space*, the mirror image of LLMs' token-by-token generation. Also flag `safety_checker` presence and dataset licensing — generated-image copyright is an open area; check model card terms before commercial use.

## 5. Choosing where to run what

| Need | Run it… |
|---|---|
| 1-off experiments | HF Inference API / widget (free tier, zero setup) |
| High-volume fixed task | local encoder, CPU (file 02 pattern) |
| Interactive LLM, private data | local SLM (file 05) or self-hosted endpoint |
| Heavy image/video/audio | GPU box or batch API queue |
| App demo next week | Gradio + local models |

## Exercises

1. CLIP: collect 5 product images from your capstone domain; classify with 5 handcrafted labels. Where does it fail (counting? fine differences?) — record 3 failure modes.
2. Whisper: record 60 s of speech (phone memo), transcribe with `tiny.en` and `base`. Diff the outputs; count errors per 100 words.
3. Run the same prompt on `SmolLM2-360M-Instruct` and `Qwen2.5-0.5B-Instruct`. Judge: which instructions does each follow? What does 360M vs 500M change?
4. Generate 4 images varying `guidance_scale` (2.5 / 7.5 / 15) at fixed seed (`generator=torch.Generator("cpu").manual_seed(42)`). Explain the trend.
5. Memory audit: `model = CLIPModel.from_pretrained(...)`, then `sum(p.numel() for p in model.parameters()) * 2 / 1e9` — predicted GB vs actual RAM delta. Repeat for Whisper-tiny.

## Pitfalls

- **fp16 on CPU** — unsupported/misleadingly slow; use fp32 or run GPU
- **`max_length` vs `max_new_tokens`** confusion (again!)
- **CLIP ≠ object detector** — it scores whole-image text match; use detection models (`facebook/detr-resnet-50`) for localization
- **Whisper hallucinating on silence** — trim silence; chunk long audio
- **First-run download surprise** — 5 GB checkpoints on hotel Wi-Fi; pre-pull with `huggingface-cli download`

## Resources

- [CLIP paper](https://arxiv.org/abs/2103.00020) (skim: fig. 1) · [Whisper paper](https://arxiv.org/abs/2212.04356) (fig. 1 + table 1)
- [Diffusers quickstart](https://huggingface.co/docs/diffusers/quicktour)
- HF docs: [zero-shot image classification](https://huggingface.co/docs/transformers/tasks/zero_shot_image_classification), [ASR](https://huggingface.co/docs/transformers/tasks/asr)
- [Whisper live demo Space](https://huggingface.co/spaces/openai/whisper) — test before downloading
