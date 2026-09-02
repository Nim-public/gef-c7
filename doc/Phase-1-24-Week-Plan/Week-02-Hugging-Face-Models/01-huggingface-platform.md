# 01 — The Hugging Face Platform

> Week 2 index: [README.md](README.md)

**Session 1 topic:** *HuggingFace walkthrough — why HuggingFace matters, Models, Datasets, Spaces.*

---

## What you'll learn

- What the Hub is and why it became the standard for open AI artifacts
- How to read a model card like a professional (license, data, benchmarks, usage)
- Model / dataset / space discovery patterns
- Programmatic access: `huggingface_hub`, caching, versioned commits

## 1. Why Hugging Face matters

The Hub is to AI models what GitHub is to code, plus three things GitHub doesn't standardize: **model cards** (what the model is and isn't), **license labels** (what you may do with it), and **inference widgets** (try it in the browser, zero code).

For this program it matters because:

- Every week's building blocks live there: tokenizers (W1), encoders/summarizers (W2), embedders for RAG (W4–6), vision/audio models (W7–9)
- Weights are versioned with immutable commit SHAs — reproducibility for evals (Week 16)
- Free, license-transparent alternatives to paid APIs exist for most tasks

## 2. The three artifact types

| Artifact | URL shape | What it holds |
|---|---|---|
| **Model** | `hf.co/<org>/<model>` | weights + tokenizer + config + model card |
| **Dataset** | `hf.co/datasets/<org>/<name>` | data + viewer + loader script/parquet |
| **Space** | `hf.co/spaces/<org>/<name>` | hosted demo apps (Gradio/Streamlit/Docker) |

### Discovery patterns that work

- Filter the [Models](https://huggingface.co/models) page: task → framework → license → language, sort by **Trending/Downloads**
- Downloads ≈ community trust proxy; *Trending* ≈ what's new and hot
- Check the **Files** tab before downloading: `model.safetensors` size tells you RAM/VRAM needs (fp16 ≈ 2 bytes/param → 0.5B ≈ 1 GB)
- Widget on the right = instant sanity test without any setup

## 3. Reading a model card critically

Open [distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english) and read it as a checklist:

| Section | Question you're answering |
|---|---|
| License | Can I ship this commercially? (`apache-2.0`/`mit` yes; `cc-by-nc-4.0` research only) |
| Training data | Is my domain represented? (`SST-2` = movie reviews — how far from support tickets?) |
| Limitations/bias | What inputs will it get wrong? |
| Metrics | F1 91% on SST-2 ≠ 91% on *your* data — plan your own eval |
| Usage code | Exact `pipeline` call — copy it, run it |
| Base model | Architecture + size (DistilBERT: 6 layers, 66M params) |

**Rule for the capstone:** never adopt a model without (1) acceptable license, (2) a 20-example sanity test on *your* data, (3) a noted eval plan.

## 4. Programmatic access

### The `huggingface_hub` CLI and API

```powershell
huggingface-cli download distilbert/distilbert-base-uncased-finetuned-sst-2-english --revision main
huggingface-cli whoami
```

```python
from huggingface_hub import hf_hub_download, list_models

path = hf_hub_download(
    repo_id="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    filename="config.json",
)
print(path)          # inside the local cache

models = list_models(task="text-classification", sort="downloads", direction=-1, limit=5)
for m in models:
    print(m.id, m.downloads)
```

### Pin versions for reproducibility

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained(
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    revision="735b0a1",          # commit SHA from the repo's history
)
```

Every load in this program should eventually carry a revision — silent upstream model updates are a real production failure mode.

### Authentication

```powershell
huggingface-cli login
```

```python
from huggingface_hub import HfApi
api = HfApi()                    # picks up your stored token
print(api.whoami()["name"])
```

Needed for: gated models (Gemma, Llama), private repos, pushing your own artifacts (you will push datasets/models by Week 16).

## 5. Datasets

```python
from datasets import load_dataset

ds = load_dataset("imdb")               # {"train": 25000, "test": 25000}
print(ds["train"][0])
ds["train"].features                     # schema: text + label classes
```

`datasets` gives you: memory-mapped loading (bigger-than-RAM), `.filter/.map/.shuffle` processing, and instant integration with `Trainer`. Browse with the dataset viewer on the Hub before downloading — check the schema, splits, and a few rows.

## 6. Spaces: where demos live

Spaces host runnable demos (mostly **Gradio**). Two uses for you:

1. **Study** — every Space's code is public; find a pipeline demo and read how it wires `gr.Interface` around a `transformers` call
2. **Publish** — you'll host a capstone demo Space by Week 16

Smallest possible Gradio demo around an HF model:

```python
import gradio as gr
from transformers import pipeline

clf = pipeline("sentiment-analysis")

def score(text):
    out = clf(text[:512])[0]
    return {out["label"]: out["score"]}

gr.Interface(fn=score, inputs=gr.Textbox(), outputs=gr.Label()).launch()
```

## Exercises

1. Find the top-3 downloaded models for `zero-shot-classification`. Record: license, base architecture, params, and one sentence on what each does differently.
2. Pick any dataset for your capstone domain; load it, print `features`, and write down 3 data-quality observations (duplicates, label noise, length outliers).
3. Download a gated model's *card* only (e.g., `google/gemma-2b`) — what does accepting the license actually bind you to?
4. Fork a simple Space into your account, run it, and change one thing (title, default text, model).
5. Write `inspect_model(repo_id)` that prints params count from `config.json`, license from the card, and last-modified date — without loading weights.

## Pitfalls

- **Trusting benchmark numbers** over a sanity test on your own data
- **Ignoring licenses** — "it's on the Hub" ≠ "it's usable in my product"
- **Floating refs** — loading `main` in code that must reproduce results; pin `revision=`
- **Re-downloading in CI/containers** — mount/persist `HF_HOME` cache
- **Gated ≠ free** — some models require accepting terms per organization

## Resources

- [HF Hub docs](https://huggingface.co/docs/hub/index) · [`huggingface_hub` docs](https://huggingface.co/docs/huggingface_hub/index)
- [Model card guide](https://huggingface.co/docs/hub/model-cards) (standard sections, model card metadata)
- HF Course ch. 1–5 (the canonical walkthrough of everything above)
- [Full transformer architecture list](https://huggingface.co/models?pipeline_tag=text-classification&sort=trending) — use filters, learn the landscape by browsing
