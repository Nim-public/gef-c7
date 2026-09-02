# 01 — Registries & CI/CD for Prompts and Agents

> E8 index: [README.md](README.md)

**Core topics:** *Model/prompt registries, lineage, and CI/CD that gates every behavior-changing artifact.*

---

## What you'll learn

- The registry: versioned artifacts (models, adapters, prompts, tool descriptions, eval sets) with lineage
- Prompt CI/CD: evals as the merge gate (W15-02's datasets, enforced)
- Rollback: restoring behavior in minutes, not days
- The deployment manifest: the single config that pins *everything*

## 1. The registry (what gets versioned)

| Artifact | Version source | Storage |
|---|---|---|
| model / adapter | HF revision (W2-01) / registry (MLflow) | registry |
| system prompts | git tag (W3-02) | repo |
| tool descriptions | git tag | repo |
| eval dataset | semantic version (W16-01) | registry |
| routing config | git tag | repo |
| schema (grammars, W22-02) | git tag | repo |

**Lineage** = every deployed behavior maps to exact artifact versions:

```python
# deploy manifest — the single source of truth (W11-02's config, productionized)
manifest = {
    "agent": "triage",
    "model": {"id": "gpt-4o-mini", "revision": "2024-11-20"},
    "prompts": {"system": "prompts/triage.system.md@v7"},
    "tools": {"search_knowledge": {"revision": "a1b2c3"}},
    "router": {"config": "routing.yaml@v4"},
    "eval_set": "capstone-agent-regression@v3.1",
    "safety_battery": "battery@v2",
}
```

W3-02's versioning and W16-01's eval versioning converge here: the manifest pins *all* of them, and CI checks the manifest against the registry before deploy.

## 2. Prompt/agent CI/CD (the gate)

```yaml
# .github/workflows/agent-cd.yml
on:
  pull_request:
    paths: ["prompts/**", "tools/**", "routing.yaml", "src/agent/**"]
jobs:
  eval-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/unit -q                     # W15-01 §4 (fast, stubbed)
      - run: python eval/run_regression.py --dataset v3.1   # W15-02 hosted evals
      - run: python security/battery.py               # E7-03 red-team regression
      - run: python eval/check_budgets.py --baseline eval/baseline.json  # W15-05
```

The gate: **no eval regression, no budget blowout, no security bypass = no merge.** Everything you built in W15/W16-01 composes into these four steps; the CI config is the enforcement of the discipline you've practiced since W3-02.

### Rollback (the reason registries exist)

```python
def rollback_to(manifest_version: str):
    m = registry.load(manifest_version)
    deploy(m)         # prompts from git tag, model revision, router config — all pinned
```

A bad deploy reverts in minutes because *every* artifact is addressable. Practice the rollback until it's boring (W15-01's drill: break the agent, revert, verify).

## 3. MLflow-style model registry (for fine-tuned artifacts)

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
with mlflow.start_run(run_name="lora-v1-capstone"):
    mlflow.log_param("base_model", "Qwen/Qwen2.5-0.5B-Instruct")
    mlflow.log_param("lora_r", 16)
    mlflow.log_metric("task_success", 0.87)
    mlflow.log_metric("general_parity_delta", -0.01)   # W16-04's parity check!
    mlflow.log_artifacts("out/lora-v1/adapter", artifact_path="adapter")
    mlflow.register_model("runs:/<run_id>/adapter", "capstone-analyst")
```

Registry entry = weights + lineage (base, data, hyperparams) + eval metrics — the W16-04 parity results are *part of the artifact*. Staging→production promotion is a gated transition (the §2 eval gate, again).

## 4. The environment ladder

| Env | Models | Prompts | Evals | Data |
|---|---|---|---|---|
| dev | local SLM / cheap API (W2-05) | working copies | quick suite (stubbed) | synthetic (W16-02) |
| staging | pinned prod models | release candidates | full suite + red-team (E7) | masked real |
| prod | pinned, routed (W15-04) | registry vN | online dashboards (E8-04) | real, governed |

Promotion = the manifest moving up the ladder through the same gates. No environment skips.

## Exercises

1. Build the manifest loader + registry check; introduce a mismatch (prompt tag vs git) and verify CI blocks the deploy.
2. Rollback drill: deploy v7 → break something (worse prompt) → deploy v8 → measure regression (W15-02) → rollback to v7 → verify parity restored. Time it — target < 10 minutes.
3. MLflow registry: register your W16-04 LoRA adapter with lineage + parity metrics; promote staging→prod through a review gate.
4. Prompt-PR simulation: open a PR that changes only `triage.system.md`; walk the CI — which of the four gates run, and which catch a planted regression?
5. Write your environment ladder (§4) for the capstone: models, evals, and data per environment — with the promotion gates named.

## Pitfalls

- **Registry without enforcement** — the manifest exists but deploys don't check it; CI is where registries become real
- **Hotfixes bypassing the ladder** — the 2 a.m. "just tweak the prompt" that skips evals is how regressions ship (W3-02's versioning discipline under pressure)
- **Model revision unpinned at deploy** — `gpt-4o-mini` today ≠ next month's; pin dates/versions (W2-01)
- **Lineage gaps for fine-tuned models** — adapter without base/data/hyperparams is unreproducible (W16-04's registry entry)
- **Rollback untested** — practice it; a rollback that fails during an incident doubles the incident

## Resources

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html) — stages, lineage, aliases
- W15-02 (LangSmith datasets/CI), W16-01 (versioning), W3-02 (prompt hygiene) — composed here
- OpenAI [model deprecation docs](https://platform.openai.com/docs/models) — why pinning is mandatory
- Feature-flag services (LaunchDarkly/Unleash) — the manifest's runtime toggle layer
