# 02 — Ready-to-Use Models: Sentiment & Traditional ML Tasks

> Week 2 index: [README.md](README.md)

**Session 2 topic:** *Using models (ready-to-use) on HuggingFace — Traditional ML Models: Sentiment Analysis, etc.*

---

## What you'll learn

- The `pipeline()` API — the 3-line path from model card to working prediction
- Sentiment analysis with encoder models, and why scores are not probabilities of truth
- NER for entity extraction
- Zero-shot classification — the "no training data" classifier
- Where these traditional models beat LLM APIs (cost, latency, determinism)

## 1. `pipeline()`: the universal loader

```python
from transformers import pipeline

clf = pipeline("sentiment-analysis")            # default: distilbert SST-2
print(clf("The new model card format is excellent!"))
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

`pipeline(task, model=...)` bundles tokenizer + model + postprocessing. Every task has a default model; you almost always want to *choose* one explicitly:

```python
clf = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device="cpu",            # or "cuda"
)
```

Batching (real speedup — encoders love batches):

```python
texts = ["great product", "support never replied", "works as advertised"]
for out in clf(texts, batch_size=8):
    print(out)
```

## 2. Sentiment analysis — and reading the scores

```python
reviews = [
    "Battery lasts two days. Best phone I've owned.",
    "Screen scratched in the first week. Avoid.",
    "It works, I guess. Nothing special.",
]

for out in clf(reviews):
    print(f"{out['label']:8} {out['score']:.4f}")
```

Three things to internalize now (they return in Week 16's evals):

1. **The score is the model's confidence in its label**, not correctness. `POSITIVE 0.99` on sarcasm is still wrong.
2. **Domain shift is the killer**: SST-2 was movie reviews. Support-ticket tone ("ticket closed as duplicate") is out of distribution.
3. **Label sets are fixed** at training time — this model knows only `POSITIVE`/`NEGATIVE`, not `NEUTRAL`, not "mixed". For richer label sets: zero-shot classification, below.

### Sanity-test protocol (do this every time)

```python
tests = [
    ("This is fine I guess", None),            # neutral — model must pick one anyway
    ("Not bad at all, actually loved it", None),  # negation
    ("I would buy it again if I hated myself", None),  # sarcasm
]
for text, _ in tests:
    print(text, "->", clf(text)[0])
```

Run these five lines and you've learned more about the model than the card tells you.

## 3. Named entity recognition (NER)

```python
ner = pipeline("token-classification",
               model="dslim/bert-base-NER",
               aggregation_strategy="simple")

ner("Sundar Pichai announced a $2B data center in Bangalore on March 3rd.")
# [{'entity_group': 'PER', 'word': 'Sundar Pichai', 'score': 0.999, 'start': 0, 'end': 13},
#  {'entity_group': 'MISC', ... 'Bangalore' ...}, ...]
```

With `start`/`end` offsets you can highlight spans in a UI or mask PII before sending text to an LLM API (Week 1 regex does patterns; NER does *semantics* — "Nimesin" isn't a regex match, it is a `PER`).

## 4. Zero-shot classification: labels you choose at runtime

A pretrained **NLI model** (entails/contradicts) turns any label list into a classifier — no training data:

```python
zsc = pipeline("zero-shot-classification",
               model="facebook/bart-large-mnli")

zsc(
    "My laptop battery drains within two hours after the update.",
    candidate_labels=["hardware issue", "software bug", "billing", "account access"],
)
# {'labels': ['hardware issue', 'software bug', ...], 'scores': [0.72, 0.21, ...]}
```

- Add `hypothesis_template="This customer message is about {}."` to tune the phrasing
- Trade-offs vs Week 1's TF-IDF classifier: no labeled data needed / handles unseen categories — but slower (NLI forward passes per label), and label *wording* strongly affects scores (try synonyms and watch results move)
- Multilingual: `joeddav/xlm-roberta-large-xnli`

## 5. When do traditional models beat LLM APIs?

| Criterion | Encoder (BERT-class) | LLM API |
|---|---|---|
| Latency (single short text) | ~10–50 ms | ~500–2000 ms |
| Cost per 1k texts | ~free (self-hosted CPU) | $ |
| Fixed label set, high volume | **wins** | overkill |
| Labels change daily / nuance needed | retraining needed | **wins** (prompt) |
| Determinism | same input → same output | sampling variance |
| Explanation of decision | none (black box score) | can explain in-line |

The capstone pattern you'll use in Week 13: **encoders filter/route cheaply, LLMs handle the hard tail**.

## Exercises

1. Run the sanity-test protocol on 3 sentiment models: the default, `cardiffnlp/twitter-roberta-base-sentiment-latest` (3 classes), and a domain model you find on the Hub. Which handles negation/sarcasm best?
2. Build a PII-masking function: NER (person/location/org) + Week 1 regex (email/phone) → replaced with `[REDACTED-*]`. Test on a synthetic ticket.
3. Zero-shot the same 10 support messages with two different `hypothesis_template` phrasings. Quantify how much label wording changes the winner.
4. Benchmark: time `clf` on 100 texts vs a Week-1-style LLM API call for the same task. Compute cost per 1,000 items for both.
5. Wrap your best sentiment model in the Gradio snippet from file 01 and run it locally.

## Pitfalls

- **Long inputs** — BERT-class models cap at 512 tokens; truncate deliberately (`truncation=True`) and note what you're throwing away
- **Score ≠ probability of correctness** — calibrate on your data (Week 16)
- **Default-model drift** — pin `model=` explicitly, always
- **`aggregation_strategy` forgotten in NER** — you get word-pieces with per-piece scores, not entities
- **Zero-shot with single-word labels on domain jargon** — rephrase labels descriptively

## Resources

- HF docs: [Pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines) (all task names + default models)
- HF Course ch. 1 (pipeline internals) & ch. 7 (token classification)
- [NLI explanation](https://huggingface.co/tasksource/blogpost_zero_shot_classification) — how zero-shot classification actually works
- [Transformer architectures overview](https://huggingface.co/learn/nlp-course/chapter1/3) — encoder vs decoder recap
