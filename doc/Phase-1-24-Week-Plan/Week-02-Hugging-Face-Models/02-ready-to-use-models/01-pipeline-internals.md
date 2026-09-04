# 02.1 — Pipeline Internals

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

---

## What you'll learn

- The three pipeline stages, each inspectable
- The task registry: every task name and its default model
- Batching, device placement, and truncation — the production knobs
- Building a pipeline-equivalent from raw components (to demystify it)

## 1. The three stages, inspected

```python
from transformers import pipeline

clf = pipeline("sentiment-analysis")            # default: distilbert SST-2

# what pipeline() built:
print(type(clf.model), type(clf.tokenizer))
print(clf.device)                                # where tensors go
```

`pipeline(task, model, ...)` = **preprocess** (tokenizer) → **model forward** → **postprocess** (argmax, label mapping, aggregation). Every convenience hides one of these three — and each can be inspected or replaced:

```python
# the manual equivalent — identical output:
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english")
model.eval()

text = "great product"
inputs = tok(text, return_tensors="pt", truncation=True)
with torch.no_grad():
    logits = model(**inputs).logits
probs = logits.softmax(-1)[0]
labels = model.config.id2label
best = probs.argmax()
print(labels[best.item()], probs[best].item())    # POSITIVE 0.9998 — same as pipeline
```

## 2. The task registry

| Task name | Default model (varies by version) | Output |
|---|---|---|
| `sentiment-analysis` | distilbert SST-2 | label + score |
| `text-classification` | same family | label(s) + score |
| `token-classification` | dslim/bert-base-NER | entities |
| `zero-shot-classification` | facebook/bart-large-mnli | labels ranked |
| `summarization` | sshleifer/distilbart-cnn | text |
| `question-answering` | distilbert SQuAD | span + score |
| `translation_xx_to_yy` | t5/opus family | text |
| `feature-extraction` | various | embeddings |

**Pin the model explicitly** — defaults move between transformers versions (W2-01's drift rule, task-registry edition). `pipeline("text-classification")` on your machine may not match the docs.

## 3. Production knobs

```python
clf = pipeline("sentiment-analysis", model=MODEL_ID, device=0,       # GPU:0 / "cpu"
               truncation=True, max_length=256)

for out in clf(texts, batch_size=16):                                # batching
    ...
```

| Knob | Effect | Trap |
|---|---|---|
| `device` | CPU vs GPU placement | default is CPU even with a GPU present |
| `batch_size` | throughput | default 1 — 10–20× slower on big jobs |
| `truncation`/`max_length` | long-input handling | silent truncation without it (errors otherwise) |
| `top_k`/`return_all_scores` | output shape | affects downstream parsing |

## 4. When to go below the pipeline

The pipeline is ideal until you need one of:

- **logits/probabilities per token** (custom confidence) → raw model + manual postprocess
- **multi-model ensembles** → shared tokenizer, separate forwards
- **custom preprocessing** (domain normalization before tokenization) → your own tokenize step
- **streaming/batched production serving** → a proper server (W15-03), not a pipeline in a loop

```python
# the demystified version — same math, full control:
inputs = tok(texts, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    logits = model(**inputs).logits
probs = torch.softmax(logits, dim=-1)
conf, pred = probs.max(-1)
```

Softmax over logits, argmax over probs — the three stages are three lines you now own (the W1-01 lesson applied to encoders).

## Exercises

1. Rebuild the sentiment pipeline from raw components; assert identical outputs on 50 texts (bit-level on the same hardware).
2. Task-registry census: for 8 task names, print the default model and read its card — record which defaults you'd change and why.
3. Batching benchmark: 1,000 texts at batch_size 1 vs 16 vs 64 — throughput table (file W2-02 parent's numbers, verified).
4. Custom postprocess: return raw logits and build your own label+confidence mapping — including the multi-label case (sigmoid, not softmax).
5. Device audit: run on CPU vs GPU; measure the placement overhead of `.to(device)` per batch vs once.

## Pitfalls

- **Truncation not requested** — >512-token inputs raise or silently misbehave depending on call shape; set `truncation=True` explicitly
- **Softmax on multi-label heads** — SST-2 heads are single-label (softmax fine); multi-label heads need sigmoid per class
- **`device` mismatch** — model on GPU, inputs on CPU → runtime error; place both
- **Pipeline object reuse across threads** — not thread-safe for all tasks; one per worker or lock
- **Default-model drift across transformers versions** — pin `model=` and record the transformers version (W2-01)

## Resources

- HF [pipelines reference](https://huggingface.co/docs/transformers/main_classes/pipelines) — task catalog, API
- W2-02 parent, W1-01 (tokenization), W11-01 (the production-serving contrast) — composed here
