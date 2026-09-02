# Week 2 — Hugging Face Models: Study Guide

> Full schedule: [../README.md](../../README.md)

**Sessions:** Sat 12 Sep, 7–10 PM IST (Session 1) · Sun 13 Sep, 7–10 PM IST (Session 2) · Office Hours Thu 17 Sep, 7–8 PM IST

**Weekly task:** [06-capstone-task-huggingface-integration.md](06-capstone-task-huggingface-integration.md)

---

## Why this week matters

Week 1 taught you what models are; Week 2 makes you a *consumer* of the world's largest open model ecosystem. Everything later in the program — RAG (Weeks 4–6), multimodal (Weeks 7–9), agents (Weeks 10–14) — starts by pulling components off the Hugging Face Hub. This week you learn to find them, evaluate them, run them, and wire them into your capstone.

## What you will be able to do after this week

- [ ] Navigate the Hub: models, datasets, spaces — and read a model card critically
- [ ] Download/cache models and datasets with `huggingface_hub`
- [ ] Run ready-to-use traditional ML models (sentiment, NER, zero-shot classification) via `pipeline`
- [ ] Use models for summarization, extractive/generative Q&A, translation, and embeddings
- [ ] Run modern models: CLIP-style image-text matching, Whisper ASR, LLM generation, diffusion image generation
- [ ] Pick and run a Small Language Model locally; know when an SLM beats an API
- [ ] Integrate at least one HF model into your capstone for a concrete NLP/CV/translation task

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-huggingface-platform.md](01-huggingface-platform.md) | The Hub, model cards, licensing, caching, Spaces | 2–3 h |
| 2 | [02-ready-to-use-models.md](02-ready-to-use-models.md) | Pipelines: sentiment, NER, zero-shot classification | 3 h |
| 3 | [03-nlp-tasks.md](03-nlp-tasks.md) | Summarization, Q&A, translation, embeddings | 3 h |
| 4 | [04-modern-models.md](04-modern-models.md) | CLIP, Whisper, LLM generation, diffusion | 3–4 h |
| 5 | [05-small-language-models.md](05-small-language-models.md) | SLM landscape, running locally, API vs local | 2 h |
| 6 | [06-capstone-task-huggingface-integration.md](06-capstone-task-huggingface-integration.md) | Wire an HF model into your capstone | 2–3 h |

## Environment setup

```powershell
pip install transformers datasets huggingface_hub accelerate
pip install sentence-transformers
pip install gradio                    # quick demo UIs (Spaces run these)
pip install diffusers safetensors     # image generation (file 04)
pip install soundfile librosa         # only if you try Whisper locally
```

Sign up at [huggingface.co](https://huggingface.co) (free), then authenticate — some models (Gemma, Llama) and all private repos need it:

```powershell
huggingface-cli login          # or: set HF_TOKEN in .env
```

Downloads cache under `~/.cache/huggingface` (override with `HF_HOME`) — fetch once, reuse everywhere.

## Self-check before Week 3

1. A model card shows license `cc-by-nc-4.0` and 12k downloads. Can your capstone use it? Why/why not?
2. `pipeline("sentiment-analysis")` returns `{'label': 'POSITIVE', 'score': 0.998}` — what model is behind it, and what was it trained on?
3. When is `conversational` style Q&A (generative) better than extractive Q&A — and vice versa?
4. Your laptop has 8 GB RAM. Which CLIP-size model can you run, and how do you check before downloading?
5. Name two concrete reasons to prefer a local SLM over an API for your capstone — and one reason to prefer the API.
