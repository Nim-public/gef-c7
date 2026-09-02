# 04 — Fine-Tuning Embedders & Rerankers

> E1 index: [README.md](README.md)

**Core topic:** *Fine-tuning your retrieval stack — domain-adapted embedders (bi-encoders) and cross-encoder rerankers.*

---

## What you'll learn

- Why off-the-shelf embedders underperform on domain data — and what fine-tuning fixes
- The training data formats: triplet/query-positive/hard-negative mining
- MultipleNegativesRankingLoss (the workhorse) and CrossEncoder training
- Measured parity: domain gains without general-retrieval regression

## 1. Why fine-tune retrieval

Your W5-02 bake-off compared *pretrained* models. On domain text (tickets, product specs, medical notes), pretrained embedders miss: jargon, abbreviations, synonym mappings specific to your org. Fine-tuning on even **a few hundred domain pairs** typically moves hit-rate measurably — often more than switching models.

| Layer | Trainable | Data needed | Gain |
|---|---|---|---|
| **Embedder (bi-encoder)** | contrastive on pairs | 500–5k query→relevant-doc pairs | domain vocabulary + intent match |
| **Reranker (cross-encoder)** | pairwise relevance | 200–2k (query, doc, label) | precision of the final top-k (W5-03) |

## 2. Training data

Sources (composed from your existing artifacts):

1. **Real logs with outcomes**: W9-05 👍/👎 + clicked citations → (query, cited chunk) positives
2. **Synthetic expansion** (W16-02): LLM generates questions per chunk — *the chunk is the positive*
3. **Hard negatives**: retrieved-but-wrong chunks (the reranker's key food) — mine from your current engine's top-20 misses

```python
# embedder training rows: (query, positive) — and hard negatives per query
{"query": "how long do refunds take?",
 "positive": "Refund requests are processed within 5 business days of approval.",
 "hard_negative": "Refund fraud takes 30 days to investigate."}
```

The hard-negative rule: negatives must be *relevant-looking but wrong* (same topic, different answer) — random docs teach nothing.

## 3. Fine-tune the embedder (MultipleNegativesRankingLoss)

```python
from sentence_transformers import (
    SentenceTransformer, InputExample, losses, models, datasets
)
from torch.utils.data import DataLoader

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

train = datasets.load_dataset("json", data_files="data/retrieval_train.jsonl", split="train")
loader = DataLoader(
    [InputExample(texts=[r["query"], r["positive"]]) for r in train],
    batch_size=16, shuffle=True)

loss = losses.MultipleNegativesRankingLoss(model)   # in-batch negatives: batch-mates are negatives

model.fit(train_objectives=[(loader, loss)], epochs=2, warmup_steps=100,
          output_path="out/embedder-domain-v1")
```

`MultipleNegativesRankingLoss`: for each anchor, its positive must outrank every other in-batch doc — the contrastive idea (W8-04's CLIP loss, single-modality). Bigger batches = more negatives = better; scale `batch_size` to memory.

Then re-run **the W5-02 bake-off harness unchanged** — your fine-tuned model is just another candidate row: hit rate @5, MRR, and the *general* regression check (a public retrieval mini-set or your pre-fine-tune eval slice — domain gains must not cost general retrieval; W16-04's parity discipline).

## 4. Fine-tune the reranker (cross-encoder)

```python
from sentence_transformers import CrossEncoder, InputExample

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", num_labels=1)

rows = [InputExample(texts=[r["query"], r["doc"]], label=r["relevant"])   # 1/0
        for r in rerank_train]

reranker.fit(train_dataloader=DataLoader(rows, batch_size=16), epochs=1,
             output_path="out/reranker-domain-v1")
```

Labels come from: 👍/👎 on retrieved docs, LLM-judged relevance on top-20 candidates (W5-05 judge rules), or graded relevance from your golden set. Deploy by pointing W5-03's `rerank()` at the new path — the harness measures the reranking gain directly.

## 5. Parity + deployment (the discipline)

| Check | How |
|---|---|
| domain gain | W4-05 harness hit rate/MRR vs the base model |
| general non-regression | a public retrieval slice (BEIR-style sample) or your pre-fine-tune scores |
| serving fit | same dims (384) → drop-in for LanceDB (W4-03); **re-embed + re-index everything** (W4-03's drift rule) |
| consistency | pin revision; W16-01 versioning for the model too |

The re-index cost is real: a new embedder invalidates every stored vector — budget the re-embed job and the dual-index migration window (build new table → validate → switch alias).

## Exercises

1. Mine training data from your logs + synthetic expansion: ≥500 query/positive pairs with ≥1 hard negative per query. Report source mix.
2. Fine-tune MiniLM (§3); run the W5-02 bake-off table with your model added. Hit-rate delta vs base?
3. Hard-negative ablation: train with random negatives vs mined hard negatives — compare MRR. (This is why §2's rule exists.)
4. Fine-tune the reranker on 300 labeled pairs (LLM-judged); rerun the W5-03 pipeline — rerank gain on top-k precision?
5. General-regression check: score both models on 20 public retrieval queries (any BEIR sample) — did domain tuning cost general retrieval? Quantify.

## Pitfalls

- **Training/eval leakage** — near-duplicate queries across splits (W16-02's §3 check before training)
- **Forgetting to re-index** — old vectors + new embedder = silent zero-quality retrieval (the recurring W4-03 rule)
- **Overfitting to logs** — 500 pairs of *your* phrasing → brittle model; mix synthetic diversity (W16-02)
- **Reranker label noise** — LLM-judged labels at <80% agreement poison training; hand-verify a sample (W5-05)
- **Max-length truncation** — domain docs longer than the model's window get cut mid-answer; chunk (W4-02) before training too

## Resources

- Sentence Transformers [training docs](https://sbert.net/docs/sentence_transformer/training_overview.html) + [loss reference](https://sbert.net/docs/package_reference/losses.html) — MNRL, TripletLoss, CachedMNRL
- HF blog, *Embedding adaptive to your domain* + [GTE/BGE fine-tune examples](https://huggingface.co/blog/how-to-train-sentence-transformers)
- Muennighoff et al., MTEB + BEIR — the general-regression evaluation sets
- W5-02/03 (bake-off, reranking) + W16-02 (synthetic data) — composed here
