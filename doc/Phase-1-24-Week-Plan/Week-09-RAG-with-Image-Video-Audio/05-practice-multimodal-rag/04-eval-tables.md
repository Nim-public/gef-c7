# Eval Tables — Retrieval, Ragas, Latency

**What you'll learn:** the practice deliverable's stage 4: the three tables
the rubric grades — retrieval R@K per class, RAGAS-style answer metrics,
and the latency ledger — produced by one command, committed as artifacts.

## 1. Table 1: retrieval per query class

| Class | n | R@5 | R@10 | MedR |
|---|---|---|---|---|
| natural | 8 | 0.62 | 0.75 | 3 |
| charts | 9 | 0.55 | 0.78 | 4 |
| exact-term | 8 | 0.75 | 0.88 | 2 |

Built from the Week-07 harness with a `class` column — the class split is
the router's report card (weak classes → weak routes).

## 2. Table 2: answer metrics (Ragas-style, minimal)

| Metric | What it measures | Target |
|---|---|---|
| faithfulness | answer claims ⊆ context | ≥0.85 |
| answer_relevancy | answer ↔ question | ≥0.7 |
| context_precision | cited units actually relevant | ≥0.6 |

Minimal implementation without the full Ragas dependency (implement the
three metrics with your LLM-as-judge pattern from Week 05, or import
Ragas — both acceptable; *name which*):

```python
def faithfulness(answer: str, context_ids: set[str], audit: dict) -> float:
    if audit and not audit["ok"]:
        return 0.0
    claims = split_claims(answer)                       # sentence split
    return sum(1 for c in claims if cites_valid(c, context_ids)) / max(len(claims), 1)
```

## 3. Table 3: the latency ledger (from W9-04)

| Mode | p50 ms | p95 ms | $/answer |
|---|---|---|---|
| P1 | 397 | 655 | 0.002 |
| P3 | 2430 | 4180 | 0.020 |

Copied from the measured ledger — this table exists in the README so the
numbers are visible without opening reports.

## 4. One command, three tables

```bash
py scripts/eval_multimodal.py --out reports/eval-tables.md
```

The script runs the harness (retrieval), the battery (answers), and the
ledger (timing), rendering all three tables with a header (corpus
version, date, machine). Committed reports are derived data — regenerate,
never hand-edit.

## 5. Judge calibration — before the tables mean anything

LLM-as-judge scores drift with prompt wording. Calibrate once per eval
season:

```text
1. Hand-label 10 answers as faithful / not-faithful (your labels = truth).
2. Run the judge; compute agreement.
3. Agreement ≥ 0.8 → trust the table. Below → fix the judge prompt,
   not the threshold.
```

| Judge prompt style | Agreement (typical) | Failure mode |
|---|---|---|
| "is this answer good?" | 0.5–0.6 | vibes |
| "does every claim appear in context? cite or fail" | 0.8–0.9 | misses paraphrase |
| claim-split + per-claim check (your splitter) | 0.85+ | splitter quality |

The calibrated judge is what makes Table 2's numbers comparable across
weeks — without step 3, faithfulness trends measure your prompt edits,
not your system.

## 6. The tables' consumer — who reads what

| Table | Primary reader | Decision it feeds |
|---|---|---|
| retrieval per class | you | next week's first task (weakest class) |
| answer metrics | evaluators | faithfulness bar (capstone grade) |
| latency ledger | Week-10 agent | tool-call budget |

Design rule: each table exists for *someone's decision*. A table with no
named consumer is reporting theater — cut it or find its reader. All
three here earn their place: one drives your roadmap, one drives the
grade, one drives the agent design.

## Exercises

1. Produce the three tables on your corpus; check class-level retrieval
   against the router's gold labels — the weakest class names your next
   week's first task.
2. Metric audit: hand-verify faithfulness on 5 answers; if the judge
   disagrees twice, run the calibration protocol above before trusting
   the table.
3. Regression fixture: commit the three tables as the baseline; wire a CI
   job that re-runs `eval_multimodal.py` and flags regressions > thresholds
   — and note each table's consumer in its header.

## Pitfalls

- Ragas-style metrics without claim splitting — one-sentence answers score
  artificially high; the splitter is the metric's real work.
- Tables without the header (version/date/machine) — unreproducible, and
  the rubric notices.
- Baseline updated to make CI green — baselines move only via accepted
  eval runs, same rule as Week 07.

## Resources

- Week-05 eval harness (the judge pattern); Week-07 harness (retrieval
  metrics); W9-04 ledger.
- Ragas docs (if using the library) — map its metrics to this table's rows.
