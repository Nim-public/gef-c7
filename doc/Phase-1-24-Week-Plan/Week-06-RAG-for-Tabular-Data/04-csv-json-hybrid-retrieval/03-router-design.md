# Router Design — Rules, Then Zero-Shot, Then Agent

**What you'll learn:** the tabular router's ladder: rules classify the
obvious shapes, a zero-shot classifier handles phrasing variance, and
the full agent takes the genuinely ambiguous — the W9-05 ladder applied
to tabular data.

## 1. The ladder

```python
# rung 1: rules — the measurable properties decide
def route_rules(query: str, data_shape: str) -> str | None:
    if re.search(r"\b(sum|total|average|count|how many)\b", query, re.I):
        return "sql"
    if data_shape == "paste" and len(query) < 100:
        return "paste"
    return None

# rung 2: zero-shot classifier — phrasing variance
ZERO_SHOT_LABELS = ["sql-aggregation", "semantic-row-search", "paste-lookup"]

def route_zero_shot(query: str) -> str:
    return classifier(query, ZERO_SHOT_LABELS)

# rung 3: the full agent — tools decide at runtime
```

| Rung | Latency | Cost | Accuracy profile |
|---|---|---|---|
| rules | ~0 | free | rigid, precise on keywords |
| zero-shot | ~150 ms | ~150 tok | phrasing variance |
| agent | seconds | full loop | genuinely ambiguous cases |

The ladder is the W14-04 model-routing pattern, applied to *routing*
instead of model selection: rules first, classifier for variance, the
agent for the rest.

## 2. The zero-shot classifier

```python
from transformers import pipeline

clf = pipeline("zero-shot-classification",
               model="facebook/bart-large-mnli")

def route_zero_shot(query: str) -> str:
    res = clf(query, candidate_labels=ZERO_SHOT_LABELS)
    if res["scores"][0] < 0.5:
        return "agent"                     # uncertain → the full loop
    return {"sql-aggregation": "sql",
            "semantic-row-search": "hybrid",
            "paste-lookup": "paste"}[res["labels"][0]]
```

| Score | Route |
|---|---|
| ≥0.5 | the classified route |
| <0.5 | escalate to the agent |

The confidence gate is the W13 calibration discipline: below the
threshold, the ambiguous case goes to the agent (the strong default).
The threshold is calibrated from labeled queries (the W16 file 01-04
protocol).

## 3. The routing battery (per ladder rung)

| Query | Rung | Route | Assert |
|---|---|---|---|
| "total revenue by month" | rules | sql | SUM keyword |
| "hi" | rules | paste/chat | greeting pattern |
| "which product is waterproof" | zero-shot | hybrid | semantic label |
| "weird compound question about stuff" | agent | agent | fall-through |

The battery asserts the route per rung — rules cases hit rung 1,
variance cases rung 2, ambiguous cases rung 3. The route decisions are
logged (the W9-05 discipline) for the miss analysis.

## 5. The router pin note (the ladder's manifest)

```markdown
# Tabular router (W06)
- rung 1: rules (SUM/total/how-many → sql; greetings → paste)
- rung 2: zero-shot (bart-large-mnli, threshold 0.5, calibrated)
- rung 3: the agent (fall-through)
- decisions logged per rung for the miss analysis
```

The pin note is the ladder's manifest — the rungs, the threshold, and
the logging. The miss analysis (W9-05) consumes the logged decisions.

## 4. The router pin note (the ladder's manifest)

**Task:** extend `reports/sdk-versions.md` with the router ladder: the
rung implementations, the zero-shot threshold, the escalation policy,
and the logged-decisions location.

**Worked approach:** the router's pin records the ladder's rungs and
the calibration — the same manifest discipline as every policy
artifact.

**Pass criterion:** note committed; the battery command green as
recorded.

## Exercises

1. Implement rung 1; run 10 keyword queries; verify 10/10 correct
   routes.
2. Zero-shot drill: run 10 paraphrased queries through rung 2; measure
   accuracy vs hand labels; set the 0.5 threshold from the score
   distribution.
3. Ladder drill: run the full ladder on the mixed set; produce the
   route-accuracy table per rung.
4. Pin drill: write the note; the logged decisions cited.