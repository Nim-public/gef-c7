# 01 — Tokenization & Text Representation: Deep Dive

> Parent topic: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md) · Week 1 index: [../../README.md](../../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-tokenization-strategies-and-bpe.md](01-tokenization-strategies-and-bpe.md) | Word/char/subword, BPE trained from scratch | 4 h |
| 2 | [02-special-tokens-and-attention-masks.md](02-special-tokens-and-attention-masks.md) | `<PAD>`/`<EOS>`/`<CLS>`, padding, chat templates | 3 h |
| 3 | [03-encodings-one-hot-and-multilabel.md](03-encodings-one-hot-and-multilabel.md) | One-hot, multi-hot, sklearn encoders, limits | 2 h |
| 4 | [04-embeddings-and-visualization.md](04-embeddings-and-visualization.md) | Cosine/dot/L2, PCA/UMAP on a real corpus | 3 h |
| 5 | [05-tokenizer-apis-and-cost.md](05-tokenizer-apis-and-cost.md) | tiktoken vs HF, multilingual/emoji, cost math | 2 h |
| — | [exercises.md](exercises.md) | Expanded exercise set | 3 h |

**Why the deep dive:** every later week — RAG chunking (W4), routing thresholds (W15-04), fine-tuning data prep (W16-03) — assumes you can move text between representations fluently and *count tokens precisely*. This subfolder takes the parent's overview to working depth: you will train a BPE tokenizer from scratch, break padding on purpose, and audit token costs.

## File map

- **01** — the three tokenization strategies, a from-scratch BPE trainer on your own corpus, merge visualizations, OOV behavior
- **02** — special tokens as protocol, padding + attention masks (including the mask-less failure demo), chat template inspection
- **03** — one-hot and multi-hot encodings by hand and with sklearn, the sparsity problem, where they still belong
- **04** — embedding similarity metrics (cosine/dot/L2) derived and compared, dimensionality reduction, visualization on real text
- **05** — tokenizer API differences, token-cost accounting, multilingual/emoji edge cases
- **exercises.md** — expanded lab set with worked approaches
