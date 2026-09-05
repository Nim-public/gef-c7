# LLM-as-Judge — Trajectory Scoring and Calibration

**What you'll learn:** the judge that grades trajectories beyond rules:
what it scores, the rubric that keeps it stable, and the calibration
protocol from Week 09's answer-judge, extended to trajectories.

## 1. What the judge grades (and what it must not)

| Graded by judge | Graded by rules (file 01) |
|---|---|
| tool-choice sensibility ("did retrieve make sense here?") | loop detection, budget stop |
| observation use ("did the answer use what it found?") | citation validity, schema gates |
| process quality on long-tail runs | outcome classification |
| recovery grace ("did the error hint help?") | error counts |

The split is the point: **rules grade facts, the judge grades judgment.**
A judge asked to also count citations would be an uncalibrated regex.

## 2. The rubric — fixed dimensions, 0–2 each

```python
RUBRIC = [
    ("tool_choice", "Were tool calls appropriate for the query?"),
    ("evidence_use", "Does the answer reflect the observations?"),
    ("recovery", "Were errors handled gracefully (or none occurred)?"),
    ("concision", "No redundant steps or repeats?"),
]   # each scored 0 (bad) / 1 (mixed) / 2 (good); total 0–8
```

```python
def judge_prompt(trace: list[dict], answer: str) -> str:
    lines = [f"step {t['step']}: {t['tool']}({t['args']}) -> {t.get('obs', t.get('obs_error',''))[:200]}"
             for t in trace]
    return (f"Rubric: {RUBRIC}\nScore each dimension 0/1/2 with one-line reason.\n"
            f"Trace:\n" + "\n".join(lines) + f"\nAnswer: {answer}")
```

The rubric is committed, versioned, and never edited mid-season — scores
are comparable only within a rubric version (the eval-header discipline
again).

## 3. The calibration protocol (from Week 09, extended)

```text
1. Hand-label 10 trajectories on each rubric dimension (your scores = truth).
2. Run the judge twice (temperature 0, same prompt).
3. Agreement: per-dimension within ±1, total within ±2.
4. ≥80% agreement → trust. Below → fix the rubric wording, not the threshold.
```

| Judge failure | Symptom | Fix |
|---|---|---|
| lenient drift | all totals 7–8 | add anchored examples to the rubric |
| harsh on recovery | recovery ≈0 even on good runs | separate "error occurred" from "handled badly" |
| position bias | long traces scored low | score trace sections independently |

Judge self-consistency (step 2) is cheap and often skipped: a judge that
disagrees with *itself* by ±3 has no resolution, whatever its agreement
with you.

## 4. The judge's report — where scores land

| Run | tool_choice | evidence_use | recovery | concision | total |
|---|---|---|---|---|---|
| r_0042 | 2 | 2 | 2 | 1 | 7 |
| r_0043 | 2 | 1 | 2 | 2 | 7 |
| r_0044 | 1 | 1 | 0 | 1 | 3 (flagged) |

Flagged runs (total <5 or any dimension =0) route to hand review — the
judge is a *router for human attention*, not a verdict. That framing
keeps it honest: the 10% sample you hand-check is the audit of the judge
itself.

## Exercises

1. Hand-label 10 trajectories on the four dimensions; run the judge twice;
   produce the agreement table per §3.
2. Rubric-wording drill: take your lowest-agreement dimension, add one
   anchored example ("a 2 looks like this, a 1 looks like this"), remeasure.
3. Judge-as-router: flag the bottom 10% of your 25 runs by judge total;
   hand-check them — measure how many flags were justified (the judge's
   precision, measured).

## Pitfalls

- Judging *answers* instead of trajectories — the loop's behavior is the
  artifact; answers have their own judge (W9-04).
- One aggregate judge score — dimensions are diagnoses; totals are for
  sorting review queues.
- Rubric edits between eval runs — version it, or your trend lines lie.

## Resources

- Your Week-09 judge (the calibration protocol's origin).
- [`../06-practice-first-mcp-agent/`](../06-practice-first-mcp-agent/) —
  the harness output lands in its metrics table.
