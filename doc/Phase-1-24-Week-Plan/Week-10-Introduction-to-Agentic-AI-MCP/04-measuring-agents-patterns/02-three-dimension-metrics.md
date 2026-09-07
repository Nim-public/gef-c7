# Three-Dimension Metrics — Success, Efficiency, Process

**What you'll learn:** the three-axis scorecard for agent runs: did it
work (success), what did it cost (efficiency), and *how* did it behave
(process). Single-number agent metrics hide exactly the failures you
need to see.

## 1. The three dimensions, defined

| Dimension | Metric | Question | Computed from |
|---|---|---|---|
| Success | task success rate, refusal correctness | did it work / refuse honestly? | outcome + gold labels |
| Efficiency | steps, tokens, duration | what did it cost? | trajectory store |
| Process | tool-choice accuracy, error recovery, loop rate | did it behave well? | trace analysis |

```python
def score_card(runs: list[dict], gold: dict[str, bool]) -> dict:
    n = len(runs)
    return {
        "success_rate": mean(r["outcome"] == "success" and gold.get(r["query"], False)
                             for r in runs),
        "refusal_correct": mean(r["outcome"] == "refused"
                                and not gold.get(r["query"], True) for r in runs),
        "efficiency": {"p50_steps": median([r["steps"] for r in runs]),
                        "p50_tokens": median([r["tokens_in"] + r["tokens_out"]
                                              for r in runs])},
        "process": {"loop_rate": mean(looks_looped(r["trace"]) for r in runs),
                     "error_recovery_rate": recovery_rate(runs)},
    }
```

Success is *gold-labeled*, not self-reported: a run the agent calls
success but gold calls false is a failure — the label source is the eval
set from file 06, not the model.

## 2. Per-class scorecards (the router connection)

Your queries have classes (W9 patterns); agent metrics must split the
same way:

| Class | n | Success | p50 steps | p50 tokens | Loop rate |
|---|---|---|---|---|---|
| charts | 9 | 0.78 | 3 | 4.1k | 0.00 |
| exact-term | 8 | 0.88 | 2 | 2.9k | 0.00 |
| long-tail | 8 | 0.50 | 5 | 7.3k | 0.12 |

The aggregate would read 0.72 and hide everything; the split shows the
long tail is where loops live (0.12) and where the budget actually binds.
Class-split scorecards are the agent version of W9's retrieval tables —
same discipline, new dimension.

## 3. Efficiency: the token ledger, agent edition

| Component | Per successful run | Dominated by |
|---|---|---|
| System + schemas | ~900 tok × steps | tool count |
| Observations | ~180 tok × steps | your truncation |
| Retrieved context | ~2.9k × retrieval calls | W9 budget |
| Answer | ~200–400 | task |

The lever hierarchy, from your own numbers: retrieved context ≫
observations ≫ schemas. The agent's cost problem is almost always "it
re-retrieves too much", not "the loop is too long".

## 4. Process metrics that predict incidents

| Process metric | Threshold | When it fires |
|---|---|---|
| loop rate | >5% of runs | tool descriptions rotting |
| error recovery rate | <80% | error hints stale |
| budget-exhausted (degraded) rate | >10% | budget too tight or tasks too hard |
| tool never used | any tool, 50+ runs | dead tool → surface review (file 03's v2 policy) |

Each threshold maps to a fix owned elsewhere in the week — the process
dimension is the *early-warning* layer; success/efficiency are the
lagging indicators.

## Exercises

1. Build the scorecard over your 25 stored trajectories; split by class;
   write the two-sentence reading of the table.
2. Threshold drill: lower the episode budget until the degraded rate hits
   10%; record where that is — the empirical floor for your budget choice.
3. Dead-tool check: from 50 runs, list per-tool usage; any zero-usage
   tool gets a surface-review row (keep, improve description, or drop).

## Pitfalls

- One aggregate success number — the class split is where the failures
  live; aggregates are for slides, splits for engineering.
- Efficiency without the component ledger — "7k tokens" tells you nothing;
  "5.2k of it is retrieved context" tells you what to fix.
- Process thresholds copy-pasted from other projects — set them from your
  own baseline distribution (first 25 runs), then hold the line.

## Resources

- [`../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md`](../../Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag/04-eval-tables.md)
  — the class-split table format.
- File 06 — the gold-labeled eval set these metrics assume.
