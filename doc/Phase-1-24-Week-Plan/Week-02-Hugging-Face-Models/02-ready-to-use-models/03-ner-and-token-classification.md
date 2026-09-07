# 02.3 — NER & Token Classification

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

---

## What you'll learn

- Token-level classification: BIO tagging and how aggregation rebuilds entities
- Offsets: from entity spans to production uses (highlighting, masking, joins)
- The PII-masking composition (NER + regex, W2-02's pattern deepened)
- Cross-model NER comparison and domain adaptation

## 1. How token classification works

The model labels **each token** (B-PER, I-PER, O, ...) — the raw output is per-subword-token; aggregation rebuilds entities:

```python
from transformers import pipeline

ner = pipeline("token-classification", model="dslim/bert-base-NER",
               aggregation_strategy="simple")

ner("Sundar Pichai announced a $2B data center in Bangalore on March 3rd.")
# [{'entity_group': 'PER', 'score': 0.999, 'word': 'Sundar Pichai',
#   'start': 0, 'end': 13}, ...]
```

Without `aggregation_strategy`, you'd get per-subword fragments: `['Sundar', 'Pichai']` as separate B-PER/I-PER tokens. Aggregation merges consecutive same-label tokens — which is also why **adjacent same-type entities merge** (two people named consecutively become one PER span — check on real data).

## 2. The aggregation strategies

| Strategy | Behavior |
|---|---|
| `none` | raw per-token labels — max detail, needs manual grouping |
| `simple` | merge consecutive same-type tokens; first-token score |
| `average` | merge + average scores across tokens |
| `max` | merge + take max token score |

Choose `simple` for spans, `max` when you need conservative confidence (the max sub-token score survives aggregation), `average` when partial-entity confidence matters.

## 3. Offsets → production uses

The `start`/`end` character offsets are the bridge to real applications:

```python
def mask_pii(text: str, ner) -> str:
    entities = ner(text, aggregation_strategy="simple")
    out, last = [], 0
    for e in sorted(entities, key=lambda e: e["start"]):
        if e["entity_group"] in {"PER", "ORG", "LOC"}:
            out.append(text[last:e["start"]])
            out.append(f"[{e['entity_group']}]")
            last = e["end"]
    out.append(text[last:])
    return "".join(out)

mask_pii("Contact Sundar Pichai at ops@acme.com about Bangalore.")
# 'Contact [PER] at [EMAIL] about [LOC].'   (email via the W1-02 regex pass)
```

The composition order matters: **NER first, then regex** — regex catches what NER misses (emails, phones), NER catches what regex can't (names without pattern). Overlapping spans need merge logic (sort by start, skip contained).

## 4. Domain adaptation (when the model doesn't know your entities)

Pretrained NER knows PEOPLE/ORG/LOC — not product SKUs, internal project names, or medical codes:

```python
# options in order of effort:
# 1. zero-shot-ish: feed context, hope — weak for novel entity types
# 2. pattern rules for structured codes (SKU-1234): regex (W1-02)
# 3. fine-tune: 200+ labeled examples in BIO format (W16-03's loop, token edition)
```

The BIO-format training data for fine-tuning is built by aligning your entity spans to the tokenizer's subword tokens — the `token-classification` docs' dataset-prep pattern. Budget: ~200–500 labeled examples for a usable domain model.

## Exercises

1. Aggregation comparison: run the same text with all four strategies; diff the outputs — when does `max` vs `simple` change the confidence meaningfully?
2. Adjacent-entity probe: "John Smith Mary Jones met today" — does your aggregation split the two PERs? Test and fix (context window or regex post-pass).
3. PII-masking evaluation: 20 synthetic records with names/emails/phones/SKUs — measure mask recall per type; NER vs regex per type (W2-02 ex. 2's table, quantified).
4. Domain NER: find/label 100 product names in your corpus; fine-tune dslim/bert-base-NER (W16-03's loop, token-classification edition) — measure the improvement.
5. Offsets round-trip: verify `text[start:end] == word` for 50 entities — the invariant that makes masking safe.

## Pitfalls

- **Offsets on preprocessed text** — if you clean/normalize *before* NER, offsets point into the cleaned string, not the original; keep both aligned or extract on raw text
- **Adjacent entities merged** — "New York Times" (ORG) as one span vs "New York" (LOC) + "Times" — domain judgment required
- **Subword fragmentation in `word` fields** — with `aggregation_strategy="none"`, words are word-pieces; aggregate before using
- **NER as the only PII defense** — names without context (signatures, addresses) slip through; compose with regex (W2-02's layering)
- **Cross-model label sets** — dslim's PER/ORG/LOC/MISC vs other models' tags differ; map explicitly when swapping models

## Resources

- HF [token classification task guide](https://huggingface.co/docs/transformers/tasks/token_classification) — the full pipeline including fine-tuning
- [dslim models](https://huggingface.co/dslim) — the CoNLL-03-trained family
- W2-02 parent (pipeline), W5-04 (where masking feeds guards), W16-03 (fine-tuning) — composed here
