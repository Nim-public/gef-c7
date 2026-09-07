# 06.1 — Task Selection

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-huggingface-integration.md](../06-capstone-task-huggingface-integration.md)

---

## What you'll learn

- The task-selection matrix applied to your scope — with elimination reasoning
- The "biggest unknown" test: choosing the task that de-risks the most
- Scope alignment: the task must serve the v1 capability (file 08.1), not demonstrate a framework

## 1. The matrix applied

From the parent file's matrix, score each candidate task for your scope:

| Criterion (weight) | Sentiment | NER+masking | Summarization | Embeddings | Translation |
|---|---|---|---|---|---|
| Serves the v1 capability (×3) | | | | | |
| Data available this week (×2) | | | | | |
| Model maturity on Hub (×2) | | | | | |
| Evaluation feasible (×2) | | | | | |
| Feeds later weeks (×1) | | | | | |

Score 1–5 per cell, weight, sum — the highest total wins *and* the runner-up becomes the fallback if the winner's model disappoints (W2-06 §3's protocol).

## 2. The biggest-unknown test

The selection question: **which task, if it fails, kills the capstone?** That's the one to de-risk now:

- If your corpus is unusable without entity masking → NER is the blocker → select NER
- If triage accuracy is the product → sentiment/classification is the blocker → select it
- If the demo depends on cross-language support → translation is the blocker → select it

The selection is a *risk-management* decision dressed as a modeling decision — the W1-08 scope doc's feasibility section already ranked your unknowns; this table consumes that ranking.

## 3. Scope alignment (and misalignment)

| Misalignment | Symptom | Fix |
|---|---|---|
| Task demonstrates a framework, not the product | "I used Whisper because it's cool" | return to the matrix |
| Task serves a v2 feature | good tech, wrong order | defer to the sprint plan (W16-06) |
| Task has no eval path | can't prove it works | add labels (file 03) or switch |
| Task duplicates W1-05's baseline | wasted effort | merge with the baseline work |

## Exercises

1. Fill the matrix for your top-3 candidate tasks; show the scoring and the winner.
2. Write the elimination paragraph: why each loser lost, in one sentence each — the reasoning reviewers ask for.
3. The blocker test: for your chosen task, write the one-paragraph "if this fails, the capstone changes like this" — the risk statement.
4. Scope cross-check: read your W1-08 scope's feasibility section — does the chosen task address the top unknown? If not, reconcile.
5. Task-statement drill: write the deployment contract (input/output/error behavior) for the chosen task before any code (file 04's contract discipline).

## Pitfalls

- **Framework-first selection** — "I want to try Whisper" is not a task selection criterion (W3-05's lever discipline)
- **Scope misalignment** — a task that demos well but serves nothing in v1 is a detour
- **Ignoring the evaluation feasibility row** — a task you can't evaluate can't be improved
- **Multiple tasks at once** — the task is ONE (the parent's rule); breadth comes in later sprints
- **No fallback** — every selection names the runner-up and the trigger to switch

## Resources

- W1-08 (scope), W2-06 parent (the protocol), W2-01 (discovery) — composed here
- W16-01 (the eval discipline the task must feed)
