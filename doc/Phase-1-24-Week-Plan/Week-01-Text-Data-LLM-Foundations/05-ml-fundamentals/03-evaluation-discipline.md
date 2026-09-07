# 05.3 — Evaluation Discipline

> Subfolder index: [README.md](README.md) · Parent: [../05-ml-fundamentals.md](../05-ml-fundamentals.md)

---

## What you'll learn

- Confusion matrix arithmetic — precision/recall/F1 computed by hand until automatic
- Threshold selection as a product decision (not a default)
- Leakage: the three kinds, demonstrated
- Overfitting curves: produced, read, and acted on

## 1. The confusion matrix by hand

```python
y_true = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
y_pred = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0]

TP = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))   # 3
FP = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))   # 2
FN = sum(t == 1 and p == 0 for t, p in zip(y_true, y_pred))   # 1
TN = sum(t == 0 and p == 0 for t, p in zip(y_true, y_pred))   # 4

precision = TP / (TP + FP)      # 3/5  = 0.6  — of flagged, how many real?
recall    = TP / (TP + FN)      # 3/4  = 0.75 — of real, how many flagged?
f1        = 2 * precision * recall / (precision + recall)   # ≈ 0.667
accuracy  = (TP + TN) / len(y_true)                          # 0.7 — misleading with imbalance
```

Read the numbers as **product statements**: precision 0.6 = "4 in 10 alerts are false — what does that cost the reviewer?"; recall 0.75 = "1 in 4 real cases missed — what does that cost the business?" The metric choice *is* the product decision (W1-05 parent's table, sharpened).

## 2. Threshold selection as a decision

The classifier outputs scores; the threshold converts them to decisions:

```python
import numpy as np

scores = np.array([0.9, 0.85, 0.8, 0.6, 0.45, 0.4, 0.2, 0.15, 0.1, 0.05])

def evaluate(thresh):
    preds = (scores >= thresh).astype(int)
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, preds))
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, preds))
    fn = sum(t == 1 and p == 0 for t, p in zip(y_true, preds))
    return {"precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1)}

for t in (0.3, 0.5, 0.7, 0.85):
    print(t, evaluate(t))
```

Sweep the threshold, tabulate precision/recall pairs, and pick using the *cost asymmetry* of your application: a support-ticket router tolerates false positives (wasted review) more than false negatives (lost customer). Document the chosen threshold with its precision/recall pair — it's part of the model's contract (W10-05).

## 3. The three kinds of leakage

| Kind | Mechanism | Demo |
|---|---|---|
| **Feature leakage** | a feature that encodes the answer | predicting "closed" tickets including the `resolution` column |
| **Preprocessing leakage** | fitting scalars/vectorizers on full data | W1-05's `make_pipeline` fix |
| **Temporal leakage** | training on the future | W16-03's date-ordered splits |

```python
# temporal leakage demonstration
train_2026 = data[data["date"].dt.year == 2026]     # trains on the future
test_2025  = data[data["date"].dt.year == 2025]     # tests on the past — score inflated
```

Run the demonstration on your data: the leaked version scores higher *and is wrong*. The fix is pipeline-shaped (fit inside the pipeline), not vigilance.

## 4. Overfitting curves — produced and read

```python
train_scores, val_scores = [], []
for depth in range(1, 15):
    m = DecisionTreeClassifier(max_depth=depth).fit(X_tr, y_tr)
    train_scores.append(m.score(X_tr, y_tr))
    val_scores.append(m.score(X_val, y_val))
# plot: train ↑ monotonic, val rises then falls — the gap IS overfitting
```

Reading the curves: the best `max_depth` is the val-score peak, not the train-score end. The remedies (fewer params, more data, regularization, early stopping — W16-03) map one-to-one to which side of the gap you're on.

## Exercises

1. Metric arithmetic: from the confusion matrix alone, compute precision/recall/F1/accuracy and state each as a product sentence.
2. Threshold sweep: produce the precision/recall table at 10 thresholds; identify the operating point for (a) a fraud system (FN costly) and (b) a spam filter (FP costly). Justify both.
3. Leakage trio: construct a dataset demonstrating each of §3's leakage kinds, with the inflated-vs-honest score for each.
4. PR-curve reading: plot precision vs recall across thresholds on an imbalanced set; explain why the curve *shape* matters more than the area for small positive classes.
5. Overfitting forensics: for the depth sweep, also record the gap (train − val); find the depth where the gap exceeds 10 points — that's your complexity ceiling.

## Pitfalls

- **Accuracy on imbalanced data** — 99% accuracy on a 1% fraud rate = catching nothing; per-class metrics only
- **Threshold left at 0.5 by default** — the operating point is a product decision; sweep it
- **Metrics computed once, context-free** — report n, prevalence, and the confusion matrix beside every metric
- **Leakage via dedup** — near-duplicate rows split across train/test (W16-02's check) inflate scores
- **Val set used for threshold *and* architecture tuning** — double-dipping; reserve the test set for the final read

## Resources

- scikit-learn [model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html) — the metric catalog
- W1-05 parent, W16-01 (versioned evals), W5-05 (judge calibration) — the neighbors
- Kohavi et al. on pitfalls in controlled experiments — the leakage mindset at scale
