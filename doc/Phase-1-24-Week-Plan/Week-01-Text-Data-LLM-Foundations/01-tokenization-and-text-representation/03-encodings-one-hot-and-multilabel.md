# 01.3 — Encodings: One-Hot, Multi-Label & Their Limits

> Subfolder index: [README.md](README.md) · Parent: [../01-tokenization-and-text-representation.md](../01-tokenization-and-text-representation.md)

---

## What you'll learn

- One-hot, multi-hot, and index encodings — by hand and with sklearn
- Why sparse encodings can't represent similarity (the geometry argument)
- The sklearn encoder family: `OneHotEncoder`, `LabelBinarizer`, `MultiLabelBinarizer`, `CountVectorizer`
- Where sparse encodings still belong in a modern stack

## 1. The encodings by hand

```python
import numpy as np

vocab = {"action": 0, "comedy": 1, "drama": 2, "horror": 3}

def one_hot(label: str) -> np.ndarray:
    v = np.zeros(len(vocab)); v[vocab[label]] = 1; return v

def multi_hot(labels: list[str]) -> np.ndarray:
    v = np.zeros(len(vocab))
    for l in labels: v[vocab[l]] = 1
    return v

one_hot("comedy")                 # [0., 1., 0., 0.]
multi_hot(["action", "comedy"])   # [1., 1., 0., 0.]
```

The geometry argument, stated precisely: **any two distinct one-hot vectors are orthogonal** — their dot product is always 0. So the encoding carries zero information about similarity: `"action"` and `"comedy"` are exactly as similar as `"action"` and `"horror"`. This is not a defect you can tune away; it's structural.

## 2. The sklearn encoder family

```python
from sklearn.preprocessing import OneHotEncoder, MultiLabelBinarizer, LabelBinarizer

# single categorical column (the deployment-grade way)
enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
enc.fit([["billing"], ["technical"], ["account"]])
enc.transform([["billing"]])                     # [[1., 0., 0.]]
enc.transform([["legal"]])                       # all zeros — handle_unknown saved you

# multi-label targets
mlb = MultiLabelBinarizer(classes=["action", "comedy", "drama"])
mlb.fit_transform([["action", "comedy"], ["drama"]])
# array([[1, 1, 0],
#        [0, 0, 1]])

# class labels → one-hot for training (usually the loss does this for you)
LabelBinarizer().fit_transform(["billing", "technical"])
```

`handle_unknown="ignore"` matters in production: an unseen category at inference otherwise raises. (The all-zeros row it produces is ambiguous though — log it, W10-05.)

## 3. Text encodings: CountVectorizer as multi-hot/count space

Before embeddings, documents were bag-of-words vectors:

```python
from sklearn.feature_extraction.text import CountVectorizer

docs = ["refund processed in 5 days", "refund fraud takes 30 days", "password reset link"]
cv = CountVectorizer(binary=True)                 # binary=True → multi-hot over vocabulary
X = cv.fit_transform(docs).toarray()
print(cv.get_feature_names_out())                 # the 'vocabulary'
print(X[0])                                       # multi-hot vector for doc 1
```

The vocabulary here is the *document-level* analog of the token vocabulary in file 01.1 — and it inherits the same orthogonality: `"refund fraud"` and `"refund processed"` share the `refund` dimension but nothing else. TF-IDF (file W1-05) weights it; embeddings (file 01.4) replace it.

## 4. Where sparse encodings still belong

| Use | Why sparse is right |
|---|---|
| classification **targets** | one-hot/y is what cross-entropy consumes |
| small categorical features | cheap, exact, interpretable |
| **input features for tiny models** | linear/logistic models can't use embeddings efficiently at small scale |
| explainability | one-hot columns map 1:1 to meaning |

The rule: **sparse encodings for outputs and small inputs; learned embeddings for anything similarity-shaped.**

## 5. The bridge to embeddings (preview)

One-hot `e(word)` is a vector with one 1. An embedding matrix `E ∈ R^(V×d)` maps it: `emb(w) = e(w) @ E` — a learned linear projection that *can* place similar words nearby (file W8-01 §2). Every embedding layer in every model is exactly this multiplication.

## Exercises

1. Implement `one_hot`/`multi_hot`; prove all distinct one-hot pairs are orthogonal by computing the Gram matrix.
2. `OneHotEncoder` with `handle_unknown="ignore"` vs `"error"` — feed 3 unseen categories; compare behavior and decide which your pipeline wants.
3. Build a multi-hot movie-geneme dataset (20 movies × 8 genres); compute pairwise Jaccard similarity — show that it *is* computable on sparse vectors (unlike cosine semantics).
4. Convert the same corpus to `CountVectorizer(binary=True)` and to `MiniLM` embeddings (file 01.4); for 5 queries compare which representation ranks the right document first — and why the answer differs by question type.
5. Estimate memory: a 50k-word vocabulary one-hot (float32) vs a 384-dim embedding — the compression factor that motivated §5.

## Pitfalls

- **All-zeros ambiguity** — `handle_unknown="ignore"` maps unseen categories to the zero vector, indistinguishable from "no category"; add an explicit `unknown` category when it matters
- **Fit on train only** — `OneHotEncoder` fitted on full data leaks test categories; fit on train, transform test (W1-05 leakage rule)
- **`LabelBinarizer` quirks with binary data** — it returns a flat column for 2 classes; use `OneHotEncoder` for consistency
- **Comparing one-hot with cosine** — always 0 or undefined; there is no signal to compare
- **Confusing multi-hot with counts** — `CountVectorizer(binary=False)` keeps term frequency; the binary variant discards it deliberately

## Resources

- sklearn [preprocessing docs](https://scikit-learn.org/stable/modules/preprocessing.html#encoding-categorical-features) — encoders, `handle_unknown`
- HF NLP Course ch. 2 — from words to embeddings narrative
- W1-05 (TF-IDF classifier), W8-01 (embeddings as learned representations) — the neighbors of this file
