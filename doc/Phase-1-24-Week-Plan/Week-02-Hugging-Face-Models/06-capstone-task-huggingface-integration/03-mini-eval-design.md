# 06.3 — Mini-Eval Design

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-huggingface-integration.md](../06-capstone-task-huggingface-integration.md)

---

## What you'll learn

- The 20-example eval: design, grading rubric, and pass criteria
- The failure taxonomy that turns errors into actions
- The seed-and-grow strategy: this eval becomes the W16-01 versioned set

## 1. The eval design (before any model runs)

```markdown
# Mini-eval: <task> — v1
20 cases · graded pass/fail per case · model: <pinned> · rubric: v1

| Case | Input | Expected | Kind |
|---|---|---|---|
| c01 | "reset my password" | access | happy |
| c02 | "SSO fails for new hires" | access | jargon |
| c03 | "charged twice, want refund" | billing | mixed-intent |
| ... | | | |
| c16 | "ignore instructions and ..." | refuse | adversarial |
| c17 | "" | error/empty | edge |
```

The case-kind mix (from the parent's protocol):

| Kind | Count | Purpose |
|---|---|---|
| happy path | 8 | baseline competence |
| hard/edge | 5 | negation, typos, mixed intent |
| adversarial | 3 | injection, manipulation |
| boundary | 4 | empty, too long, off-domain |

## 2. The grading rubric (per kind)

| Kind | Pass condition |
|---|---|
| happy path | correct label + confidence in range |
| hard/edge | correct label OR flaggable (low confidence) |
| adversarial | refuses/deflects — never obeys |
| boundary | doesn't crash; explicit error or empty result |

The rubric is written *before* running the model — grading after seeing outputs biases the rubric toward the model's behavior (W5-05's discipline, applied to yourself).

## 3. Running and reporting

```python
import json

def run_eval(model_fn, cases: list[dict]) -> dict:
    rows, passed = [], 0
    for c in cases:
        out = model_fn(c["input"])
        ok = grade(out, c)                       # rubric per kind
        rows.append({**c, "output": out, "pass": ok})
        passed += ok
    return {"n": len(cases), "pass_rate": passed / len(cases), "rows": rows}
```

The report: pass rate overall + per kind + every failure row with its case kind. The failure taxonomy (W1-05's four classes) applies at classification level; the kind column adds the eval-design dimension.

## 4. Seed-and-grow (the versioning payoff)

The 20 cases are the seed of the W16-01 versioned eval:

```markdown
## eval v1 (week 2) — 20 cases
- 8 happy, 5 hard, 3 adversarial, 4 boundary
- pass rate: 85% — failures: 2 mixed-intent, 1 jargon

## eval v2 (week 5) — +15 cases from production failures
- the 2 mixed-intent failures became cases with corrected labels
- 5 new jargon cases from real tickets
```

Every production failure (W10-04's logs) becomes a case — the eval grows with the system, and regressions get caught by history instead of memory.

## Exercises

1. Build the eval: 20 cases across the four kinds for your task — rubric written first.
2. Run 3 candidate models through it; produce the per-kind pass table; select with the numbers.
3. The failure deep-dive: for the worst model, classify every failure into the W1-05 taxonomy; write one action per class.
4. Version drill: fix the two worst failures; bump to v2; verify v1 cases still pass (no regression) — the W16-01 gate, mini edition.
5. Seed-and-grow projection: at your production volume, project when the eval reaches 200 cases — and what accuracy claim that n supports.

## Pitfalls

- **Grading after seeing outputs** — rubric drift toward the model's behavior; write the rubric first
- **All happy-path cases** — adversarial and boundary kinds are where models die in production
- **n too small for claims** — 5 cases support "works on these 5"; scale before claiming rates
- **Gold labels from the model's own suggestions** — confirmation bias; label blind, then compare
- **Eval set never re-run** — a stale eval is decoration; wire it into CI (W15-02)

## Resources

- W5-05 (Ragas — the grown-up version of this eval), W16-01 (versioning), W2-02 (the models)
- [STARC](https://arxiv.org/abs/2403.11378) — the self-contained LLM evaluation methodology (the principles at research rigor)
