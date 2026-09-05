# Datasets & Evaluations — Hosted Regression Runs

**What you'll learn:** LangSmith datasets and evaluations: your eval set
uploaded as a dataset, runs scored on the platform, and the hosted
results reconciled with your local harness — one truth, two views.

## 1. The dataset upload

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("gef-c7-eval-v2", description="15-case set")

for case in EVAL_SET_V2:
    client.create_example(
        inputs={"query": case["query"]},
        outputs={"gold": case["gold"]},
        dataset_id=dataset.id,
        metadata={"class": case["class"], "version": "v2"},
    )
```

| Field | Note |
|---|---|
| `inputs.query` | the case's query |
| `outputs.gold` | the gold answer/label |
| `metadata` | class + version — the eval header, hosted |

The dataset is your eval set, mirrored. The version discipline carries:
a new eval-set version creates a new dataset (or a tagged revision) —
the hosted and local sets must never diverge silently.

## 2. The hosted evaluation run

```python
def predict(inputs: dict) -> dict:
    result = run_agent(inputs["query"])
    return {"answer": result.answer, "citations": result.citations}

def exact_match(outputs: dict, reference_outputs: dict) -> bool:
    return reference_outputs["gold"] == outputs["answer"]

results = client.evaluate(
    predict,
    data="gef-c7-eval-v2",
    evaluators=[exact_match],
    experiment_prefix="w15-regression",
)
```

| Piece | Role |
|---|---|
| `predict` | your agent, invoked per case |
| `evaluators` | your scoring functions (exact-match, citation gate) |
| `experiment_prefix` | the run family, comparable across versions |

The hosted run executes your agent against the dataset with your
scorers — the W10 harness, hosted. The scores attach to runs (the
feedback column) and the platform draws the trend charts your soak tier
produced by hand.

## 3. Reconciling hosted and local (one truth, two views)

| Rule | Why |
|---|---|
| the local parquet is authoritative | retention and schema are yours |
| hosted runs are *views* of the same cases | the dataset mirrors the parquet |
| reconciliation = a join on run/case ids | drift is a bug |
| baselines update locally first | the hosted view reflects, never decides |

The reconciliation is the parity test, hosted edition: the hosted
experiment's scores must match the local harness's within tolerance —
same agent, same cases, same scorers. Divergence means the *dataset* or
the *scorers* drifted between the two views.

## 5. The hosted-eval pin note (the mirror's manifest)

```markdown
# Hosted evaluations (W15)
- dataset: gef-c7-eval-v2 (mirrors local v2 — parity job in CI)
- scorers: imported from eval harness (no re-implementation)
- experiments: w15-regression* (comparable across versions)
- reconciliation: nightly join on case ids; drift = failure
- baselines: updated locally first; hosted reflects
```

The mirror's manifest: what is hosted, what is local, what reconciles
when. The parity job (dataset-contents diff) runs in CI — the mirror
rule is enforced, not aspirational.

## Exercises

1. Upload the eval set; run the hosted evaluation; download the results
   and reconcile against the local harness (join on case ids).
2. Drift drill: edit one case in the hosted dataset only; the
   reconciliation must flag the divergence — the mirror rule, proven.
3. Trend drill: run three experiments (three agent versions); compare
   the hosted trend chart with your soak chart — same shape or explain.
4. Pin drill: write the manifest; the parity job in CI; the drift drill
   committed as its evidence.

## Pitfalls

- Two eval sets growing independently — the mirror rule and the
  reconciliation job are the guard.
- Scoring functions diverging between hosted and local — share the
  scorer code; import, don't re-implement.
- Hosted-only baselines — baselines update locally first; the platform
  reflects the decision.