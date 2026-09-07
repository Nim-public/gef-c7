# Router Implementation — Rules + Classifier, Logged Decisions

**What you'll learn:** the tabular router (file 04-03) deployed for the
capstone task: rules + zero-shot classifier over the full data corpus,
with every decision logged for the miss analysis.

## 1. The deployed router

```python
class TabularRouter:
    def __init__(self, shapes: dict[str, str], clf):
        self.shapes = shapes              # file_id → routed shape
        self.clf = clf
        self.decisions: list[dict] = []

    def route(self, query: str, file_id: str) -> str:
        shape = self.shapes[file_id]
        decision = {"query": query, "shape": shape}
        if shape == "sql":
            route = "sql"
        elif (r := route_rules(query, shape)):
            route = r
        else:
            route = route_zero_shot(query)
        decision["route"] = route
        self.decisions.append(decision)
        log_decision(decision)
        return route
```

| Design | Purpose |
|---|---|
| shapes pre-computed at ingest | the shape decision is per-file |
| decisions logged per query | the miss analysis (W9-05) |
| the ladder's rungs | rules → zero-shot → (agent implicit) |

The router composes the two decisions: the *shape* (SQL vs paste vs
hybrid, per file) and the *query* (which rung answers it). The logged
decisions feed the miss analysis — every misroute is reviewable.

## 2. The miss analysis (the W9-05 discipline, tabular)

| Miss type | Example | Fix locus |
|---|---|---|
| rules miss | keyword absent but intent obvious | widen the regex band |
| classifier miss | paraphrase flips the label | add few-shot examples |
| shape miss | SQL route on a semantic question | the shape thresholds (file 04-01) |

Each miss type names its fix locus — the same diagnosis-tree thinking
as the Ragas metrics (file 01-01), applied to routing.

## 3. The routing accuracy report

```text
# Router accuracy — 25 queries — 3 runs — [date]
| rung | n | accuracy | notes |
|---|---|---|---|
| rules | 9 | 1.00 | keyword cases |
| zero-shot | 11 | 0.82 | 2 paraphrase misses |
| agent (fall-through) | 5 | 0.80 | one hallucinated route |
| overall | 25 | 0.88 | threshold recalibrated after |
```

The report is the router's scorecard — per rung, with the overall and
the recalibration note. The threshold changes are version-bumped (the
W16 file 01-04 governance).

## 5. The router pin note (the deployed router's manifest)

```markdown
# Tabular router (W06 capstone)
- shape decisions: pre-computed at ingest (rows/cols/numeric thresholds)
- rungs: rules → zero-shot (threshold calibrated) → agent
- decisions: logged per query (query, shape, rung, route)
- report: per-rung accuracy + miss analysis
```

The pin note is the deployed router's manifest — the shape map, the
rungs, the logging, and the report. The logged decisions are the miss
analysis's input.

## Exercises

1. Implement `TabularRouter`; run 25 queries; produce the per-rung
   accuracy table.
2. Miss-analysis drill: classify every miss into the §2 types; fix the
   modal type; remeasure.
3. Logging drill: verify every decision row lands in the store; the
   miss analysis runs from the logged rows alone.
4. Pin drill: write the note; the threshold recalibration recorded.