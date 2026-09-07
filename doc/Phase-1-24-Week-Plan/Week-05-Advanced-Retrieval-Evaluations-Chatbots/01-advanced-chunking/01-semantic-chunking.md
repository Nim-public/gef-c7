# 01.1 — Semantic Chunking

> Subfolder index: [README.md](README.md) · Parent topic: [../01-advanced-chunking.md](../01-advanced-chunking.md)

---

## What you'll learn

- Splitting at topic boundaries using embedding similarity between consecutive sentences
- Threshold calibration from the similarity distribution
- The trade-off: semantic boundaries vs compute cost

## 1. The mechanism

Embed consecutive sentences; where similarity between neighbors drops sharply, that's a topic boundary:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_chunks(text: str, threshold: float = 0.5, min_sents: int = 3) -> list[str]:
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    embs = model.encode(sents, normalize_embeddings=True)
    chunks, start = [], 0
    for i in range(1, len(sents)):
        sim = float(embs[i-1] @ embs[i])
        if sim < threshold and i - start >= min_sents:
            chunks.append(" ".join(sents[start:i]))
            start = i
    chunks.append(" ".join(sents[start:]))
    return chunks
```

## 2. Threshold calibration

Plot the histogram of consecutive similarities on your corpus. The distribution is typically bimodal: high similarity within topics, low across boundaries. The threshold sits in the valley:

```python
sims = [float(embs[i-1] @ embs[i]) for i in range(1, len(sents))]
plt.hist(sims, bins=30); plt.axvline(threshold, color="r")
```

Too low → one giant chunk per document; too high → single-sentence fragments. The valley in the histogram is the natural split point.

## 3. The trade-off

| | Fixed/recursive | Semantic |
|---|---|---|
| boundary quality | arbitrary | meaning-aligned |
| compute | zero | one embed per sentence |
| determinism | fully | depends on threshold |
| best for | structured docs | meandering prose |

## Exercises

1. Plot the similarity histogram for 3 document types (policy, FAQ, transcript); identify the natural thresholds.
2. Compare chunk counts and boundary quality: recursive vs semantic at the calibrated threshold.
3. The single-topic document: what happens when the entire document is one topic? (One giant chunk — is that correct?)

## Pitfalls

- **Threshold set without the histogram** — the valley isn't universal; calibrate per corpus
- **min_sents too low** — single-sentence "chunks" lose all context
- **Embedding cost ignored** — one encode per sentence vs per chunk; measure the overhead

## Resources

- LangChain [SemanticChunker](https://python.langchain.com/docs/how_to/semantic-chunker/)
- Greg Kamradt, *5 Levels of Text Splitting* — the chunking taxonomy
