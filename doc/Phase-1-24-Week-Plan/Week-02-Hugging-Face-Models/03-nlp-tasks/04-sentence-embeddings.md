# 03.4 — Sentence Embeddings in Depth

> Subfolder index: [README.md](README.md) · Parent: [../03-nlp-tasks.md](../03-nlp-tasks.md)

---

## What you'll learn

- The embedding API beyond `encode`: normalization, batching, dimensions
- The three production patterns: similarity search, dedup, clustering
- Dimensionality and model selection with measurements (the W5-02 preview)
- The consistency contract that makes embeddings usable across systems

## 1. The encode API, fully

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

emb = model.encode(
    sentences,                    # list[str] — batch for speed
    batch_size=64,                # encode throughput knob
    normalize_embeddings=True,    # unit length → cosine == dot (W4-03's rule)
    convert_to_numpy=True,
    show_progress_bar=True,
)
print(emb.shape)                   # (N, 384)
```

| Parameter | Effect | Default trap |
|---|---|---|
| `normalize_embeddings` | unit length | off by default — cosine ≠ dot without it |
| `batch_size` | throughput | default 32; raise for GPU |
| `convert_to_tensor` | torch tensor | numpy is the interchange default |
| `precision` | float32/16/… | float16 on GPU halves memory |

## 2. The three production patterns

### a. Semantic search (the W4 seed)

```python
def search(query: str, corpus_emb, corpus: list[str], k: int = 5):
    q = model.encode([query], normalize_embeddings=True)[0]
    sims = corpus_emb @ q                       # cosine (normalized)
    top = np.argsort(-sims)[:k]
    return [(corpus[i], float(sims[i])) for i in top]
```

### b. Near-duplicate detection

```python
def find_duplicates(emb, thresh=0.95):
    sims = emb @ emb.T
    pairs = np.argwhere(np.triu(sims, 1) > thresh)     # upper triangle only
    return [(int(i), int(j), float(sims[i, j])) for i, j in pairs]
```

`np.triu(sims, 1)` takes the upper triangle — each pair once. The threshold choice: 0.95+ = likely true duplicates; 0.85–0.95 = review queue. This is the dedup primitive for corpora (W16-02's leakage check) and eval sets (W1-05's hygiene).

### c. Clustering (unsupervised topics)

```python
from sklearn.cluster import AgglomerativeClustering

clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.6,
                                     linkage="average", metric="cosine")
labels = clustering.fit_predict(emb)
# group sentences by cluster label — topic discovery without any labels
```

Agglomerative with a cosine distance threshold builds a topic tree from embeddings — the unsupervised structure discovery behind "auto-organize my tickets."

## 3. Model selection with measurements (the W5-02 preview)

| Model | Dim | Speed (CPU, 1k sents) | Notes |
|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | ~1 min | the fast default |
| all-mpnet-base-v2 | 768 | ~4 min | stronger, slower |
| BAAI/bge-small-en-v1.5 | 384 | ~1 min | query instruction needed |
| intfloat/e5-base-v2 | 768 | ~4 min | "query:"/"passage:" prefixes required |

The selection harness: your W4-05 eval set + this table = the bake-off. The trap set (prefixes, normalization, max_length) comes from file W5-02 — the *same* sentences must be encoded identically per model, with each model's own requirements.

## 4. The consistency contract

Embeddings are only comparable when everything matches:

```python
CONTRACT = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "revision": "8b3219a",              # pinned (W2-01)
    "normalize": True,
    "max_length": 256,                  # tokenizer truncation, fixed
    "version": "corpus-v3",             # W4-05's corpus versioning
}
# every stored embedding records this contract — queries must match it exactly
```

The contract travels with the vectors: stored in the LanceDB table metadata (W9-02), checked at query time, and bumped (with re-embedding) on any change. This is the W4-03 drift rule made into an artifact.

## Exercises

1. Similarity matrix analysis: 30 domain sentences; find the strongest non-obvious pair; inspect *why* (shared topic vs shared boilerplate vs encoding artifact).
2. Dedup precision: at thresholds 0.90/0.95/0.98 — precision of found duplicates on hand-labeled pairs; pick the operating point.
3. Clustering quality: AgglomerativeClustering on 200 sentences with known topics — ARI (adjusted Rand index) vs true labels; sweep the distance threshold.
4. Cross-model agreement: the same 30 sentences through MiniLM and BGE — do the top-5 neighbors agree? (Model-lock-in evidence for the contract.)
5. Build the contract-checking wrapper: `encode_with_contract(texts)` that asserts the stored contract matches the current call — the W4-03 drift rule as a runtime check.

## Pitfalls

- **Comparing embeddings across models** — different spaces, meaningless cosine (the recurring W4-03 rule)
- **Truncation destroying the signal** — long docs need chunking first (W4-02), not silent mid-sentence cuts
- **Threshold drift across corpora** — 0.92 for English prose ≠ 0.92 for code or multilingual text; calibrate per corpus
- **Cache misses on contract changes** — any contract field change invalidates every stored vector; re-embed and re-index (W4-05)
- **Clustering without interpreting** — clusters need labels and review (W16-02's distribution check) before they drive decisions

## Resources

- Sentence Transformers [docs](https://sbert.net/) — encode API, losses, models
- W4-03 (vector DB), W5-02 (bake-off), W16-02 (synthetic + dedup) — composed here
- Reimers & Gurevych, *Sentence-BERT* — the siamese architecture origin
