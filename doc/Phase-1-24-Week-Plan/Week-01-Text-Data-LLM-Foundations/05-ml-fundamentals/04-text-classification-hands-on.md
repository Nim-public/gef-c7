# 05.4 — Text Classification Hands-On

> Subfolder index: [README.md](README.md) · Parent: [../05-ml-fundamentals.md](../05-ml-fundamentals.md)

---

## What you'll learn

- The full pipeline: data → TF-IDF → logistic regression → error analysis → deployment contract
- Error analysis as the product step (not an afterthought)
- The baseline role: your classical model is the bar every LLM solution must beat (W12-04's comparison discipline)

## 1. The dataset (build it deliberately)

```python
tickets = [
    ("my password is not working", "access"),
    ("cannot login to my account", "access"),
    ("vpn keeps disconnecting", "network"),
    ("wifi drops every few minutes", "network"),
    ("please reset my credentials", "access"),
    ("the portal says access denied", "access"),
    ("invoice amount is wrong", "billing"),
    ("refund not received yet", "billing"),
    ("billing charged me twice", "billing"),
    ("update my payment method", "billing"),
    ("need a new invoice copy", "billing"),
    ("credit card was overcharged", "billing"),
]
labels = ["access", "access", "network", "network", "access", "access",
          "billing", "billing", "billing", "billing", "billing", "billing"]
```

For the real version: 150–300 examples, ≥30 per class, *your* domain's phrasing, with 10% deliberately hard (mixed intents, typos, wrong category hints). The dataset *is* the eval — build it before the model (W16-01).

## 2. The pipeline (leakage-proof by construction)

```python
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True),
    LogisticRegression(max_iter=1000, C=10),
)
model.fit(X_tr, y_tr)
```

Why the pipeline object: the vectorizer's vocabulary is fitted on train only — the split discipline (file 05.3) enforced by construction. `ngram_range=(1, 2)` lets "not working" and "working from home" differ — bigrams carry the negation signal that unigrams lose.

## 3. Error analysis (the actual work)

```python
pred = model.predict(X_te)
for text, gold, got in zip(X_te, y_te, pred):
    if gold != got:
        print(f"GOLD={gold} PRED={got}\n  {text}\n")
```

The error taxonomy to build (each becomes an action):

| Error class | Example | Action |
|---|---|---|
| vocabulary gap | "SSO fails" → access (model saw "login") | more/better examples, or synonym expansion |
| mixed intent | "can't pay — app crashes" | multi-label or routing design change (W14-04) |
| annotation inconsistency | same text labeled twice differently | fix the labels, not the model |
| genuinely ambiguous | "portal down" (technical? access?) | define the category boundary in the guide |

**The rule: error analysis produces dataset fixes before model fixes.** 30 minutes of label cleanup usually beats any hyperparameter sweep.

## 4. The deployment contract

```python
def classify_ticket(text: str) -> dict:
    probs = model.predict_proba([text[:2000]])[0]
    classes = model.named_steps["logisticregression"].classes_
    best = probs.argmax()
    return {"label": classes[best], "confidence": round(float(probs[best]), 3),
            "model": "tfidf-logreg-v1", "low_confidence": probs[best] < 0.5}
```

The contract mirrors W1-05's deployment shape and W5-04's confidence hook: label + score + version + the low-confidence flag that routes to human review. Version the model (vectorizer + classifier + the dataset hash) — W16-01's lineage applies to the baseline too.

## 5. The comparison discipline (vs LLMs)

| Question | Classical baseline | LLM |
|---|---|---|
| fixed labels, high volume | wins (ms latency, ~free) | overkill |
| labels evolve weekly | loses (retrain) | wins (prompt) |
| needs explanations | limited (feature weights) | wins |
| cost at 1M/day | ~$0 | $ |

Run the comparison yourself (W2-02's benchmark pattern) — the numbers, not the fashion, pick the tool. This table *is* the W15-04 router's justification.

## Exercises

1. Grow the dataset to 150 examples across 4 categories; measure accuracy vs training size — plot the learning curve; where does it flatten?
2. Error-taxonomy workshop: label every error in your test set with one of the four §3 classes; fix the largest class; re-measure.
3. Probability calibration: plot predicted confidence vs observed accuracy in bins — is 0.8 confidence actually right 80% of the time? (W5-04's confidence hook depends on this.)
4. The LLM comparison: run the same 40 test tickets through a zero-shot LLM prompt (W3-01) — build the full cost/accuracy/latency table from file W1-05 §5.
5. Multi-label upgrade: a ticket can be billing AND technical — switch to `MultiLabelBinarizer` + one-vs-rest; report per-label F1.

## Pitfalls

- **Training on the test set "just to see"** — the number is burned; generate fresh cases instead
- **Class imbalance ignored** — 80% billing data → the model predicts billing for everything; stratify and per-class metrics
- **Vectorizer refit at serving time** — the deployment vectorizer must be the training one, frozen (W16-03's template rule)
- **Confidence used uncalibrated** — an uncalibrated 0.9 is not "90% sure"; calibrate before the router trusts it (W5-04 ex. 5)
- **Baseline skipped** — the LLM solution without a classical baseline can't prove its own value (W12-04's comparison discipline)

## Resources

- scikit-learn [working with text data](https://scikit-learn.org/stable/tutorial/text_analytics/representations.html) — the tutorial behind §2
- W1-05 parent, W12-04 (comparison), W15-04 (routing rationale) — composed here
- [calibration_curve](https://scikit-learn.org/stable/modules/calibration.html) — exercise 3's tool
