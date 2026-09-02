# 05 — ML Fundamentals: Models That Learn From Data

> Week 1 index: [README.md](README.md)

**Session 2 topic:** *ML Models: Functions that learn data patterns; tasks: classification, regression, generation.* This is the conceptual bridge to everything the LLM does — same principles, different function class.

---

## What you'll learn

- The one-sentence definition of machine learning
- The three task families and how to recognize them
- How a model learns: loss functions and gradient descent (intuition + minimal demo)
- Train/validation/test discipline and evaluation metrics
- Your first real models with scikit-learn, trained on *text* features

## 1. What ML actually is

A model is a **function with adjustable parameters** `f(x; θ)`. Learning = searching for θ that minimizes a **loss** measuring how wrong the function is on training examples.

```
data (x, y) ──► model f(x; θ) ──► prediction ŷ ──► loss(ŷ, y) ──► adjust θ ──► repeat
```

Everything else — neural networks, transformers, LLMs — is a fancier `f` and a smarter search. Nothing about the loop changes.

Three ingredients every ML problem must have:

1. **Inputs (features)** — what you condition on
2. **Outputs (targets/labels)** — what you predict
3. **Examples** — enough (x, y) pairs to judge wrongness

## 2. The task taxonomy

| Task | Output `y` | Examples | Typical loss |
|---|---|---|---|
| **Classification** | category | spam/ham; sentiment; intent; ticket priority | cross-entropy |
| **Regression** | number | price; ETA; toxicity score | MSE / MAE |
| **Generation** | structured content (often text) | summary; translation; code; chat reply | next-token cross-entropy |
| (clustering / ranking) | none / order | dedup; search results | task-specific |

LLMs are **generation** models, but most LLM *applications* wrap a classification or regression problem (routing, scoring, filtering) — that's why you need all three.

## 3. How learning works

### Loss functions

- **Cross-entropy** (classification): punishes confident wrong answers logarithmically
- **MSE** (regression): mean of squared errors; punishes big misses
- **Next-token cross-entropy** (language models): for each position, how surprised was the model by the actual next token? *(This single loss, scaled up, is GPT training.)*

### Gradient descent — the whole algorithm

1. compute predictions on a batch
2. compute loss
3. compute gradient of loss w.r.t. each parameter (∂loss/∂θ — calculus does this)
4. nudge parameters downhill: `θ ← θ − η·gradient` (η = learning rate)
5. repeat for many batches/epochs

```python
import numpy as np

X = np.array([1, 2, 3, 4, 5], dtype=float)
y = np.array([2.1, 4.3, 6.2, 8.1, 9.8])     # ~ 2x

w, b, lr = 0.0, 0.0, 0.01
for step in range(200):
    pred = w * X + b
    error = pred - y
    loss = np.mean(error ** 2)
    gw, gb = 2 * np.mean(error * X), 2 * np.mean(error)
    w, b = w - lr * gw, b - lr * gb
    if step % 40 == 0:
        print(f"step {step:3d}  loss {loss:.4f}  w {w:.3f}  b {b:.3f}")

print(f"learned: y = {w:.2f}x + {b:.2f}")
```

That's gradient descent in 12 lines — the same loop trains GPT, just with billions of parameters and a bigger loss.

## 4. The evaluation discipline

**Split before you look at anything.**

```python
from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

- **train** — fit parameters
- **validation** — tune choices (hyperparameters, thresholds)
- **test** — touch once, at the end

Metrics by task:

| Task | Metrics |
|---|---|
| classification | accuracy (balanced data), **precision/recall/F1** (imbalanced), confusion matrix |
| regression | MAE, RMSE, R² |
| generation | task-specific: BLEU/ROUGE, judge-LLM scores (Week 16) |

**Overfitting** = train score high, test score low (memorized noise). **Underfitting** = both low. Remedies: more data, simpler model, regularization, early stopping (Week 16 revisits this for fine-tuning).

## 5. Hands-on: your first models — on text

Text → numbers via **TF-IDF** (word counts reweighted by rarity), then classic ML:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

texts = [
    "my password is not working", "cannot login to my account",
    "vpn keeps disconnecting", "wifi drops every few minutes",
    "please reset my credentials", "the portal says access denied",
    "invoice amount is wrong", "refund not received yet",
    "billing charged me twice", "update my payment method",
    "need a new invoice copy", "credit card was overcharged",
]
labels = ["access", "access", "network", "network", "access", "access",
          "billing", "billing", "billing", "billing", "billing", "billing"]

X_tr, X_te, y_tr, y_te = train_test_split(texts, labels, test_size=0.25,
                                          random_state=7, stratify=labels)

model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000))
model.fit(X_tr, y_tr)

print(classification_report(y_te, model.predict(X_te)))

model.predict(["internet is down again"])       # -> ['network'] (probably)
model.predict_proba(["internet is down again"]) # per-class probabilities
```

You just built the core of a support-ticket router — Week 13's LangGraph project does the same job with an LLM, and Week 1's version is the baseline you'll compare against.

```python
from sklearn.linear_model import LinearRegression

X = [[1], [2], [3], [4], [5]]
y = [2.1, 4.3, 6.2, 8.1, 9.8]
reg = LinearRegression().fit(X, y)
reg.predict([[6]])     # ~ [12.0]
```

## 6. Where LLMs fit in this picture

| Classic ML | LLM |
|---|---|
| features engineered by hand (TF-IDF) | raw tokens (file 01) |
| small function class (linear, trees) | transformer function class (file 06) |
| trained per task from scratch | pre-trained once, adapted (prompting, fine-tuning) |
| labels required per task | instruction following generalizes across tasks |

Same skeleton though: `f(x; θ)`, a loss, gradient descent, splits, and honest metrics. Week 16 (fine-tuning + evals) is this file again, bigger.

## Exercises

1. Re-run the ticket classifier with `ngram_range=(1,1)` vs `(1,2)`; compare F1. Why do bigrams help?
2. Deliberately overfit: train on 6 examples with `max_iter=1000`, no regularization change, evaluate on the rest. Observe and explain.
3. Add a 4th category ("hardware") with 3 examples. How does the confusion matrix change, and why?
4. Regression: generate `y = 3x + noise`, fit `LinearRegression`, plot data vs predictions with matplotlib.
5. Compute precision/recall *by hand* for one class from the confusion matrix; verify against `classification_report`.

## Pitfalls

- **Data leakage** — fitting the vectorizer before the split leaks test info; use `make_pipeline` so the split protects you
- **Accuracy on imbalanced data** — 95% "not spam" accuracy is useless; look at per-class F1
- **Tuning on the test set** — test set is burned after one look
- **Forgetting `stratify`** on small/imbalanced splits
- **Conflating generation quality with classification metrics** — different tools

## Resources

- scikit-learn [Getting Started](https://scikit-learn.org/stable/getting_started.html) + [User Guide](https://scikit-learn.org/stable/user_guide.html)
- StatQuest (YouTube): Gradient Descent, Confusion Matrix, ROC curves
- 3Blue1Brown, *Gradient descent, how neural networks learn*
- Géron, *Hands-On Machine Learning*, ch. 1–4 — the reference text
