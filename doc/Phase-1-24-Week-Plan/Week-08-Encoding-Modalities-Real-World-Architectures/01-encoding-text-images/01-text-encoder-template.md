# The Text Encoder Template — Tokens → Embeddings → Pooled Vectors

**What you'll learn:** the four-stage pattern every encoder in this program
instantiates — tokenize, embed, contextualize, pool — so each new modality
becomes a variation you can read, not a new subject.

## 1. The template, named once

```text
input ──▶ [1] TOKENIZE  ──▶ [2] EMBED  ──▶ [3] CONTEXTUALIZE ──▶ [4] POOL ──▶ vector
         units→ids        ids→vectors    mix vectors          many→one
```

| Stage | Text | Image (ViT) | Audio (wav2vec2) |
|---|---|---|---|
| Tokenize | BPE → ids | 224×224 → 196 patches | wave → 49 frames/s |
| Embed | id → 384-d table | patch flatten → linear | conv frontend |
| Contextualize | transformer layers | transformer layers | transformer layers |
| Pool | CLS / mean | CLS patch token | time pooling |

Same shape everywhere. When you meet a new encoder, find its four stages and
you can predict its inputs, outputs, and failure modes before reading a paper.

## 2. The template in runnable text form

```python
import torch
from transformers import AutoTokenizer, AutoModel

tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
mdl = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

@torch.no_grad()
def encode(texts: list[str], pool: str = "mean") -> torch.Tensor:
    enc = tok(texts, padding=True, truncation=True, max_length=128,
              return_tensors="pt")
    out = mdl(**enc).last_hidden_state        # (B, T, 384) — context stage
    mask = enc["attention_mask"].unsqueeze(-1)
    if pool == "cls":
        return out[:, 0]
    summed = (out * mask).sum(1)              # mean over real tokens only
    counts = mask.sum(1).clamp(min=1)
    return summed / counts

v = encode(["Q3 revenue rose 12%.", "short"])
print(v.shape, float((v[0] @ v[1]) / (v[0].norm() * v[1].norm())))
```

Two details that separate correct from naive: **mask-aware pooling** (the
`short` row's padding must not dilute its mean) and **truncation policy**
(max_length=128 silently drops content — the capstone chunks instead, see
Week 04).

## 3. Pooling choices and their consequences

| Pooling | Keeps | Loses | Use when |
|---|---|---|---|
| CLS token | trained summary | detail if untrained for your task | model has a CLS head |
| Mean of tokens | robust, no special token | emphasis (all tokens equal) | MiniLM/E5 defaults |
| Max | strongest feature | everything else | rare; sparse signals |
| Last-token (causal LLM) | recency | early tokens | decoder-only embedders |

The capstone retrieval lesson: **pooling is part of the model contract.**
E5-family models are trained for mean pooling; using CLS on them degrades
retrieval silently — no error, just worse numbers in Week 12.

## 4. The template as a refactor target

Every encoder wrapper in the capstone should expose the same signature:

```python
class Encoder(Protocol):
    dim: int
    def encode(self, units: list[dict]) -> np.ndarray: ...
```

Text, image (file 03), audio (Week-09 file) and video encoders then differ
only in preprocessing + pooling internals. This one interface is what makes
the fusion experiments (Week-08 file 03) and the encoder decision note
(practice file) measurable: swap encoders, keep everything else fixed.

## Exercises

1. Prove mask-aware pooling matters: encode a 5-word sentence and a 40-word
   sentence; compare mean-pooled norm with and without the mask division.
2. Swap pooling to CLS on MiniLM; rerun your Week-04 retrieval eval (file 05
   of Week 07); quantify the R@1 drop. Name the finding in one sentence.
3. Write `TextEncoder` against the Protocol; write the roundtrip test that
   pins `dim=384` and cosine self-similarity = 1.0.

## Pitfalls

- Pooling with `out.mean(1)` unmasked — padded rows pollute every batch with a long sentence in it.
- `max_length` defaults (512 for BERT-family) treated as "long enough" — your lecture transcripts are not; chunk.
- Cosine similarity without normalizing when one side came from a different pooling — scales differ; always L2-normalize pooled vectors.

## Resources

- Sentence-transformers pooling docs (`sentence_bert_config.json` per model).
- Week 04's retrieval index — the consumer of this encoder.
