# 06.2 — Model Selection Protocol

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-huggingface-integration.md](../06-capstone-task-huggingface-integration.md)

---

## What you'll learn

- The five-step selection protocol, run end to end
- The shortlist construction with documented elimination
- The pinning artifact (revision, tokenizer, template) that makes the selection auditable

## 1. The protocol (from the parent, expanded)

```markdown
## Step 1 — Filter (Hub search)
task = <your task> · license IN (apache-2.0, mit, ...) · language = <yours>
sort = downloads → note the top 10

## Step 2 — Shortlist 3
per model: params, input limit, card limitations, org credibility
eliminate: license problems, size violations, abandoned repos

## Step 3 — Widget tests
10 sample inputs through each model's widget → eyeball quality

## Step 4 — Harness run
the same 10 inputs through pipeline() in your code → record outputs

## Step 5 — Pin
winner + revision recorded in models/README.md → W2-06's deliverable
```

## 2. The elimination documentation

Every eliminated candidate gets a one-line reason — the reasoning *is* the artifact:

```markdown
### Shortlist
| Model | Params | License | Verdict | Reason |
|---|---|---|---|---|
| model-a | 66M | apache-2.0 | ✅ selected | best on our 10 inputs |
| model-b | 109M | mit | runner-up | slower, similar quality |
| model-c | 124M | cc-by-nc | ❌ | non-commercial license |
```

The elimination reasons prevent re-litigating the selection every sprint — and they're the first thing a reviewer reads.

## 3. The pinning artifact

```python
# models/README.md excerpt
MODEL_ID = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
REVISION = "735b0a1"                    # validated on eval set v1, 2026-11-20
TRANSFORMERS_VERSION = "4.46.0"
```

The pin means: identical behavior across machines, CI runs, and months. W2-01's cache archaeology (file 01.3) verifies the pin resolves to the exact snapshot you validated.

## 4. When the winner disappoints

The fallback ladder (from the parent's protocol step 4):

1. **Better inputs** — clean/preprocess (W1-02), fix the prompts/labels
2. **Different template/settings** — truncation, aggregation strategy, thresholds
3. **Runner-up model** — the shortlist exists for this
4. **Fine-tune** (W16-03) — 200+ labeled examples on the winner
5. **Different task formulation** — back to file 01's matrix

The ladder is ordered by cost — climb only as far as the eval evidence demands.

## Exercises

1. Run the protocol on your task; produce the shortlist table with eliminations.
2. The widget-vs-harness gap: find a model that looks great in the widget but fails your inputs — document the delta (the deployment-truth lesson).
3. Pin verification: load the pinned revision on two machines/days — assert identical outputs on 20 inputs.
4. The ladder climb: force a failure (worst-case input); walk the ladder one rung; document where the fix appeared.
5. Write the selection section of `models/README.md` — the table, the pins, the evidence links (W2-06's deliverable format).

## Pitfalls

- **Selection without elimination documentation** — "we tried some models" is not a protocol
- **Pinning the wrong revision** — the sha must match the evaluated snapshot, not `main`
- **Skipping the widget step** — it catches tokenizer/format issues in seconds that take hours to debug in code
- **Selection amnesia** — without the table, every future model debate restarts from zero
- **Winner's curse** — the best-on-eval model may be overfit to your 10 samples; the 20-case mini-eval (file 03) is the check

## Resources

- W2-01 (discovery), W2-06 parent (the protocol), W16-01 (versioning) — composed here
- [Model cards](https://huggingface.co/docs/hub/model-cards) — the audit source
- Your own `models/README.md` — the living record
