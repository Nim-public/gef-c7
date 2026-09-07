# 01.4 — Embeddings & Visualization

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

---

## What you'll learn

- The three similarity metrics — cosine, dot, L2 — derived and related
- Real embeddings on your corpus (sentence-transformers)
- Dimensionality reduction: PCA vs UMAP/t-SNE for visualization
- A repeatable embedding-visualization workflow (the E10-02 probing foundation)

## 1. The three similarity metrics, related properly

```python
import numpy as np

a = np.array([1.0, 2.0, 3.0]); b = np.array([2.0, 1.0, 3.0])

cosine   = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))   # angle only, [-1, 1]
dot      = a @ b                                              # angle × magnitudes
l2       = np.linalg.norm(a - b)                              # euclidean distance

# the identity that ties them together:
#   ||a - b||² = ||a||² + ||b||² - 2·(a·b)
#   → for unit vectors:  L2²  = 2 - 2·cosine   (monotonic — same ranking!)
```

Consequence you can *derive* (not memorize): if all vectors are normalized (unit length), **cosine, dot, and L2 produce identical rankings**. That's why this program normalizes everywhere (W4-03) — one metric, three APIs, zero ambiguity. Un-normalized vectors make dot-product scores incomparable across documents of different magnitude.

## 2. Real embeddings on your corpus

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "How do I reset my password?",            # access
    "I cannot log into my account.",          # access
    "Where is my refund?",                    # billing
    "The app crashes on startup.",            # technical
    "I was charged twice this month.",        # billing
]
emb = model.encode(sentences, normalize_embeddings=True)     # (5, 384)
sims = emb @ emb.T                                           # full similarity matrix

import matplotlib.pyplot as plt
plt.imshow(sims, cmap="viridis"); plt.colorbar()
plt.xticks(range(5), sentences, rotation=45, ha="right"); plt.yticks(range(5), sentences)
plt.title("Embedding similarity matrix"); plt.tight_layout(); plt.savefig("sims.png")
```

Read the matrix like an analyst: block structure reveals the latent classes (access/billing/technical) **without any labels** — unsupervised structure discovery, the foundation of W4's semantic search.

## 3. Dimensionality reduction: seeing 384 dimensions

384 dims can't be plotted directly; reductions project to 2-D:

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pts = pca.fit_transform(emb)
print(pca.explained_variance_ratio_)      # how much variance the 2 dims keep

plt.scatter(pts[:, 0], pts[:, 1])
for s, (x, y) in zip(sentences, pts):
    plt.annotate(s[:24], (x, y))
plt.title("PCA projection"); plt.savefig("pca.png")
```

| Method | Keeps | Best for | Cost |
|---|---|---|---|
| **PCA** | max global variance | quick look, linear structure | ms |
| **t-SNE** | local neighborhoods | cluster shapes | seconds–minutes |
| **UMAP** | local + some global | balanced, scalable | seconds |

Caveats that matter: reductions distort distances (2-D neighbors ≠ 384-D neighbors); use them to *generate hypotheses*, then verify in the full space. And PCA on normalized embeddings ≈ keeping the top principal directions of meaning.

## 4. A repeatable visualization workflow

```python
def plot_embeddings(texts, labels=None, model=None, title="embeddings", path="emb.png"):
    embs = model.encode(texts, normalize_embeddings=True)
    pts = PCA(n_components=2).fit_transform(embs)
    plt.figure(figsize=(7, 5))
    plt.scatter(pts[:, 0], pts[:, 1],
                c=range(len(texts)) if labels is None else labels, cmap="tab10")
    for t, (x, y) in zip(texts, pts):
        plt.annotate(t[:20], (x, y), fontsize=7)
    plt.title(title); plt.savefig(path); plt.close()
```

Batch it: this function over each W5-02 candidate model gives you visual model comparison — same sentences, different geometry. Cluster separation in the plot previews retrieval quality (file 01.1's §5 link).

## 5. Similarity ≠ causality (the interpretation caveat)

Embedding proximity captures *distributional* similarity — words/documents appearing in similar contexts. It may reflect: topic (good), register/style (neutral), or dataset bias (harmful — e.g., names clustered by frequency of co-occurrence with negative contexts). When you show an embedding plot to stakeholders, state what the geometry encodes and its provenance (the W7-01 metadata discipline applied to vectors).

## Exercises

1. Prove the normalization identity numerically: random vectors, normalized — verify L2² = 2−2·cos and that argsort(cosine) == argsort(-L2).
2. Similarity matrix for 10 capstone-related sentences; identify the 2 strongest non-obvious pairs and explain *why* the encoder grouped them (shared topic? shared function words?).
3. PCA vs UMAP on 200 sentences from 4 topics: which separation matches the true labels better? (Color by label; compute silhouette scores.)
4. Outlier hunt: find the sentence with the lowest max-similarity to all others in your corpus — is it genuinely unusual or an encoding artifact?
5. Build `plot_embeddings` (§4) with your W5-02 top-2 embedders; same sentences, two plots — which geometry would you trust for routing decisions?

## Pitfalls

- **Interpreting 2-D distances as 384-D distances** — projection distorts; verify any claimed cluster in the full space
- **Uncached model downloads in loops** — encode in batches; re-loading the model per call dominates runtime
- **t-SNE randomness** — it's stochastic; set `random_state` or the "clusters" move between runs (W15-03's determinism rule)
- **Cosine on unnormalized vectors** — undefined ranking semantics; normalize once at encode time
- **Showing bias-bearing clusters without context** — an embedding plot can surface dataset bias; frame it as data inspection, not model verdict

## Resources

- sklearn [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html) · [UMAP docs](https://umap-learn.readthedocs.io/) — the reduction tools
- Sentence Transformers [semantic search](https://sbert.net/examples/applications/semantic-search/README.html) — production patterns
- W1-05 (TF-IDF vs embeddings), W8-01 (learned representations), W10-02 (probing) — the connections
