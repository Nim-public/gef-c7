# 02.2 — API Embedders & Sparse Models

> Subfolder index: [README.md](README.md) · Parent topic: [../02-embedding-models.md](../02-embedding-models.md)

## API embedders

OpenAI and Cohere offer embedding APIs — strong quality, zero infra, per-token cost:

```python
from openai import OpenAI
client = OpenAI()

resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
embs = [d.embedding for d in resp.data]     # 1536-dim vectors
```

| Provider | Model | Dims | Pricing ($/1M tok) | Notes |
|---|---|---|---|---|
| OpenAI | text-embedding-3-small | 1536 | 0.02 | the volume default |
| OpenAI | text-embedding-3-large | 3072 | 0.13 | the quality tier |
| Cohere | embed-multilingual-v3 | 1024 | 0.10 | strong multilingual, int8 option |

The egress question: API embedders send your text to the provider — for sensitive corpora, self-hosted is the only option (W2-05's privacy constraint).

## Sparse models (ELSER)

ELSER (Elastic Learned Sparse EncodeR) produces **learned term-weight vectors** — like BM25 but with model-learned term expansion. "Refund" activates "reimbursement", "money-back", "return" — synonyms the model learned from training.

| | Dense | Sparse (ELSER) |
|---|---|---|
| representation | dense float vector | sparse term-weight dict |
| vocabulary bridging | learned geometry | learned term expansion |
| exact match | weak | strong (terms are preserved) |
| infra | any vector DB | Elasticsearch required |

The hybrid dense+sparse pattern: both representations indexed; RRF fuses the rankings (W4-04). ELSER requires an Elasticsearch stack — for simpler deployments, BM25 serves as the sparse arm.

## Exercises

1. API embedder test: OpenAI 3-small on your 25-query eval — hit rate vs MiniLM; the quality/cost/latency table.
2. The egress audit: log what data leaves during API embedding — assess the PII exposure (W5-04's intake guard).
3. The hybrid + sparse design: document how ELSER (or BM25) complements your dense embedder — the coverage gap analysis.

## Pitfalls

- **API rate limits on bulk embedding** — 1M chunks take hours; batch and throttle
- **Dimension mismatch across providers** — OpenAI 1536 ≠ Cohere 1024 ≠ MiniLM 384; separate indexes per model
- **Sparse model lock-in** — ELSER requires Elasticsearch; plan the migration path

## Resources

- OpenAI [embeddings guide](https://platform.openai.com/docs/guides/embeddings)
- Cohere [embed docs](https://docs.cohere.com/docs/embed-api)
- Elastic [ELSER docs](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)
