# 02 — Ready-to-Use Models: Deep Dive

> Parent topic: [../02-ready-to-use-models.md](../02-ready-to-use-models.md) · Week 2 index: [../README.md](../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-pipeline-internals.md](01-pipeline-internals.md) | What `pipeline()` actually does, per stage | 3 h |
| 2 | [02-sentiment-analysis.md](02-sentiment-analysis.md) | Scores, domain shift, the sanity protocol | 3 h |
| 3 | [03-ner-and-token-classification.md](03-ner-and-token-classification.md) | Entities, aggregation, offsets, PII use | 3 h |
| 4 | [04-zero-shot-classification.md](04-zero-shot-classification.md) | NLI mechanics, templates, calibration | 3 h |
| 5 | [05-encoder-vs-api-decision.md](05-encoder-vs-api-decision.md) | The measured decision framework | 2 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — the three pipeline stages (preprocess → model → postprocess), task registry, batching, device placement
- **02** — sentiment end to end: what the score means, domain shift measured, the sanity-test protocol formalized
- **03** — NER: token-level classification, aggregation strategies, offsets → PII masking (the W2-02 composition)
- **04** — zero-shot classification via NLI: the entailment mechanism, template sensitivity, calibration
- **05** — the encoder-vs-LLM decision framework with your measured numbers
- **exercises.md** — labs including the sanity-protocol formalization and the benchmark drill
