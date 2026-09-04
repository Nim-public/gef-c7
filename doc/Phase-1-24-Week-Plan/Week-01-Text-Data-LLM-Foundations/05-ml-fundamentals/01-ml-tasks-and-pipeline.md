# 05.1 — ML Tasks & the Pipeline Discipline

> Subfolder index: [README.md](README.md) · Parent: [../05-ml-fundamentals.md](../05-ml-fundamentals.md)

---

## What you'll learn

- The task taxonomy with a decision procedure for picking one
- The three data ingredients and the split discipline
- The end-to-end pipeline shape every project in this program shares

## 1. Task taxonomy — the decision procedure

| Question | Task | Output |
|---|---|---|
| Is the answer one of a fixed set? | **classification** | label (+ score) |
| Is the answer a number on a scale? | **regression** | value (+ uncertainty) |
| Is the answer structured content? | **generation** | text/JSON/image |
| Is the answer "which of these is best?" | **ranking** | ordered list |

The capstone uses all four: intent routing (classification), latency prediction (regression), grounded answers (generation), source ranking (retrieval = ranking). The evaluation tooling differs per task — which is why W16-01 slices evals by task.

## 2. The three data ingredients

1. **Inputs (x)** — what the model conditions on
2. **Targets (y)** — what correctness means
3. **Distribution** — the population the examples represent

The most common production failure is an **ingredients mismatch**: training on one distribution, serving another (W5-02's domain-shift rule). The defense is data provenance (W7-01): record where every example came from.

## 3. The split discipline as engineering

```python
from sklearn.model_selection import train_test_split

X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=42, stratify=y_tmp)
```

| Set | Touched when | Burned by |
|---|---|---|
| train | every experiment | nothing — it's consumed |
| validation | every hyperparameter choice | careless tuning |
| test | **once** per release | any peeking |

Add the time dimension for temporal data: split by *date*, not randomly — future information leaking backward is the classic time-series leakage (W6-03's date lesson, ML edition).

## 4. The pipeline shape (everything composes)

```
raw data ─► clean (W1-02) ─► features (TF-IDF/embeddings) ─► model ─► metrics ─► decision
                │                 │                          │
                └── versioned ────┴── versioned ────────────┘   (W16-01)
```

Every stage is a versioned artifact with tests (W15-01) — the sklearn `Pipeline` object enforces exactly this: fitting the vectorizer inside the pipeline prevents leakage by construction.

## Exercises

1. Task classification: take 10 product ideas (yours + common apps) — assign task types and note the metric each needs.
2. Split discipline drill: demonstrate temporal leakage — train on 2025 data evaluated on 2024, vs proper ordering — quantify the inflated score.
3. Distribution audit: compare train/test feature distributions (means, cardinalities) on any real dataset — find the shift.
4. Write the pipeline diagram (§4) for your capstone's *baseline* — every stage labeled with its versioning story.

## Pitfalls

- **Solving generation with classification** (or vice versa) — the task choice constrains everything downstream
- **Random splits on temporal data** — leakage by design; sort by time first
- **No stratification on imbalanced targets** — tiny classes may vanish from test entirely
- **Distribution mismatch undocumented** — the serving-time surprise that eval didn't predict (W5-02's domain-shift rule)

## Resources

- scikit-learn [model selection guide](https://scikit-learn.org/stable/model_selection.html) — splits, CV
- W1-05 parent, W16-01 (eval versioning), W6-03 (temporal data) — composed here
