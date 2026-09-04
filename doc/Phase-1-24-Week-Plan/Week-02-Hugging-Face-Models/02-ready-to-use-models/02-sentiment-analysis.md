# 02.2 — Sentiment Analysis, Deeply

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

---

## What you'll learn

- What the score mathematically is — and what it isn't
- Domain shift, measured on your own data
- The sanity-test protocol, formalized as a reusable harness
- The three-label and multi-label variants

## 1. What the score actually is

`{'label': 'POSITIVE', 'score': 0.9998}` — the score is **softmax over the model's logits**: the probability that a model trained on SST-2 (movie reviews) assigns to its classes. It is *not*:

- the probability the answer is correct (calibration ≠ softmax)
- transferable across domains (support tickets ≠ movie reviews)
- comparable across models (different trainings, different scales)

```python
from transformers import pipeline

clf = pipeline("sentiment-analysis",
               model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

for text in ["Battery lasts two days. Best phone I've owned.",
             "Screen scratched in the first week. Avoid.",
             "It works, I guess. Nothing special.",
             "I would buy it again if I hated myself."]:      # sarcasm
    print(clf(text[:512])[0])
```

The sarcasm line is the teaching case: the model is confidently wrong — high score, wrong label. Every sentiment deployment needs this example in its test set.

## 2. The sanity-test protocol, formalized

```python
SANITY_CASES = [
    ("negation",     "Not bad at all, actually loved it"),
    ("sarcasm",      "I would buy it again if I hated myself"),
    ("neutral",      "It works, I guess. Nothing special."),
    ("mixed",        "Great battery, terrible screen"),
    ("domain-shift", "Ticket closed as duplicate"),          # support tone
    ("encoding",     "Producto exceleente!!!"),              # typos + non-English
]

def sanity_report(clf):
    for kind, text in SANITY_CASES:
        out = clf(text[:512])[0]
        print(f"{kind:12} -> {out['label']:8} {out['score']:.3f}")
```

Five minutes, no training data — and it reveals more than the model card: which edge cases the model handles and which it silently fails. Run it on every candidate (W2-06's protocol step 3).

## 3. The three-label and multilingual variants

```python
# 3-class (POS/NEG/NEUTRAL), twitter-trained:
clf3 = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
# label names are lowercase ('positive'/'neutral'/'negative') and index-0 is often
# a 'None' placeholder in some revisions — read the card's label mapping!

# multilingual:
multi = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
```

Label-mapping checks are mandatory: `model.config.id2label` tells you what each output index means — the card documents it, the config confirms it. A model trained with label 0 = "very negative" produces indices that mean the opposite of SST-2's.

## 4. The deployment decision (with numbers)

Run the W2-06 comparison on the same 40 tickets:

| System | Accuracy | p50 latency | $/1k |
|---|---|---|---|
| SST-2 distilbert | measure | ~15 ms | ~0 |
| twitter-roberta (3-class) | measure | ~25 ms | ~0 |
| LLM zero-shot (W1-07) | measure | ~800 ms | $ |
| LLM few-shot (W3-01) | measure | ~900 ms | $$ |

The encoder wins on cost/latency/determinism whenever the label set is fixed and the domain shift is manageable; the LLM wins when labels change or nuance dominates. The W15-04 router composes both.

## Exercises

1. Score-distribution study: run 100 real support messages; plot the score histogram per label — bimodal? concentrated near 0.5? What does that say about deployability?
2. Sanity-harness formalization: turn `SANITY_CASES` into a pytest suite with per-kind expected behavior; run it on 3 candidate models.
3. Domain-adaptation probe: fine-tune on 50 of your labeled tickets (W16-03's loop) — measure the domain-shift gap closing.
4. Calibration check: reliability diagram (W5-04 ex. 3) for the sentiment scores — is 0.9 confidence 90% correct on *your* data?
5. Cross-lingual probe: run the multilingual model on Hindi reviews; compare with an LLM's judgment on the same texts — where do they disagree?

## Pitfalls

- **Score-as-truth** — a 0.99 score on sarcasm is the canonical example; scores need calibration on domain data
- **Label mapping assumed** — verify `config.id2label` per model; index 0 means different things per training run
- **Long inputs silently truncated** — SST-2's 512-token limit with no warning; check lengths in the pipeline
- **Neutral absent in binary models** — forcing 3 classes onto a 2-class head produces confident nonsense
- **Comparing models on different thresholds** — argmax vs score>0.5 are different systems; fix the decision rule when comparing

## Resources

- W2-02 parent, W5-04 (calibration), W16-03 (domain adaptation) — composed here
- [SST-2 dataset card](https://huggingface.co/datasets/stanfordnlp/sst2) — what the default model actually learned from
- [cardiffnlp models](https://huggingface.co/cardiffnlp) — the 3-class twitter family and its label mappings
