# 01.1 — Hub Anatomy & Discovery

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

---

## What you'll learn

- The three artifact types and their URL/identity conventions
- Discovery patterns: filters, sort signals, and widget testing
- The file tab: reading a repo's contents before downloading
- Organization and collection pages as quality signals

## 1. The three artifact types

| Artifact | URL | Identity | Contents |
|---|---|---|---|
| Model | `hf.co/{org}/{name}` | weights + tokenizer + config + card | inference artifacts |
| Dataset | `hf.co/datasets/{org}/{name}` | data + viewer + loader | training/eval data |
| Space | `hf.co/spaces/{org}/{name}` | app (Gradio/Streamlit/Docker) | runnable demos |

Identity conventions worth knowing: org accounts (`openai`, `google`, `meta-llama`) vs user accounts (`Nim`); canonical mirrors (`google-t5/t5-base` is the official T5); `-community` uploads under user namespaces.

## 2. Discovery patterns that work

```python
from huggingface_hub import list_models

# the programmatic version of the Models page filters
for m in list_models(task="zero-shot-classification", sort="downloads",
                     direction=-1, limit=10):
    print(f"{m.downloads:>9,}  {m.id}  [{getattr(m, 'license', '?')}]")
```

The signal hierarchy (what each sort actually tells you):

| Sort | Signal | Trap |
|---|---|---|
| Downloads | community trust at scale | legacy models accumulate downloads forever |
| Trending | what's new and hot | hype-sensitive; verify maturity |
| Likes | curated appreciation | small-n popularity contests |
| Recently updated | active maintenance | also includes trivial edits |

The professional workflow: filter by task → license → language → sort by downloads → shortlist 5 → read cards → widget-test → shortlist 3 → harness-run (the W2-06 protocol). Each filter cuts the candidate pool by an order of magnitude.

## 3. The Files tab — reading before downloading

```
model.safetensors          4.4 GB    ← weights (fp16: params × 2 bytes)
tokenizer.json             7.1 MB    ← fast tokenizer (W1-01)
config.json                1.2 kB    ← architecture + params count
generation_config.json     0.5 kB    ← default sampling settings
model.safetensors.index.json         ← sharded weights manifest
```

What to check in the file listing:

- **Total size** → your RAM/VRAM plan (params × 2 bytes at fp16, W2-04)
- **Sharding** (`-00001-of-00002.safetensors`) → multi-file weights, still loads transparently
- **`safetensors` vs `.bin`** → safetensors is the safe format (no pickle execution)
- **Tokenizer files present** → `tokenizer.json`/`tokenizer_config.json` — a model without them needs manual config
- **`chat_template.jinja`** → instruct model with a serving template

## 4. Organizations and collections as quality signals

- **Verified orgs** (`openai`, `google`, `meta-llama`, `mistralai`, `Qwen`) — maintained, documented, gated models with real licensing
- **Collections** — curated model groups (e.g., "Qwen2.5 family") showing variants by size/quantization; the fastest way to survey a family
- **Model repos with discussions** — active issue threads signal a maintained model; unanswered bug reports from months ago signal abandonment

## Exercises

1. Discovery protocol: find the top-3 downloaded models for `text-classification` and for `object-detection` — read each card; tabulate license, params, and maintainer activity.
2. File-tab audit: for 3 candidate models, list every file with size; compute the fp16 memory and flag any missing tokenizer files.
3. Widget test: run 3 candidate models' in-browser widgets on your own sample text — first-pass quality notes in your log.
4. Collection survey: find one model family's collection page; tabulate its variants (size × quantization × license) — the fastest family survey there is.
5. Trending vs downloads: compare the top-5 trending vs top-5 downloaded models for one task — what does each ranking surface that the other misses?

## Pitfalls

- **Download-count worship** — a 2019 BERT variant has years of accumulated downloads; sort trending too
- **Missing tokenizer files** — weights without tokenizer configs are unrunnable; check the file list first
- **Unpinned org references** — `org/model` without revision drifts (W2-01's rule)
- **Trusting the widget alone** — the widget runs default settings on demo inputs; your data differs
- **Ignoring discussions** — open bug threads on the Hub are free field reports

## Resources

- [HF Hub docs](https://huggingface.co/docs/hub/index) — repositories, organizations, collections
- [huggingface_hub API](https://huggingface.co/docs/huggingface_hub/index) — file 03's foundation
- W2-01 parent, W2-06 (the protocol consuming this discovery) — composed here
