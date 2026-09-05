# Persona Grids — Coverage Cells and Weights

**What you'll learn:** the persona grid: a matrix of user archetypes ×
intents that *designs* coverage before generation — the antidote to
synthetic data's natural bias toward whatever the generator finds easy.

## 1. The grid

| | ask a question | report a problem | request an action | give feedback |
|---|---|---|---|---|
| busy executive | cell 1 | cell 2 | cell 3 | cell 4 |
| technical user | cell 5 | cell 6 | cell 7 | cell 8 |
| first-time visitor | cell 9 | cell 10 | cell 11 | cell 12 |
| frustrated returner | cell 13 | cell 14 | cell 15 | cell 16 |

```python
GRID = {
    "personas": ["executive", "technical", "first-time", "frustrated"],
    "intents": ["question", "problem", "action", "feedback"],
    "weights": {"executive-question": 3, "technical-problem": 3, ...},
}
```

Each cell is a generation brief: persona × intent → queries with that
voice and that need. The weights come from your traffic (or the target
distribution you are building for) — the grid *designs* coverage, and
the weights *allocate* generation budget to it.

## 2. The persona definitions (voice, not stereotype)

| Persona | Voice constraints | Vocabulary hints |
|---|---|---|
| executive | terse, outcome-focused, no jargon | "bottom line", "by when" |
| technical | precise, tool-aware, version-sensitive | endpoint names, error codes |
| first-time | uncertain, asks for basics | "how do I even", "where is" |
| frustrated returner | short, references prior attempts | "already tried", "again" |

The persona rows are *voice constraints* for the generation prompt —
not personality theater. Each definition feeds the expansion prompt as
a style condition, and the validation checks the voice landed (file
04's distribution check).

## 3. The grid's coverage math

```python
def coverage_report(generated: list[dict], grid: dict) -> pd.DataFrame:
    df = pd.DataFrame(generated)
    cells = df.groupby(["persona", "intent"]).size()
    expected = pd.Series(grid["weights"])
    return (cells / expected).fillna(0)     # coverage ratio per cell
```

| Ratio | Meaning | Action |
|---|---|---|
| ≥1.0 | cell covered | stop generating for it |
| 0.5–1.0 | partially covered | top up |
| 0 | uncovered | the generator avoids it — prompt harder or hand-write |

The coverage ratio is the grid's progress bar — generation continues
until every cell ≥1.0 (or the cell is explicitly deprioritized). The
zero cells are the finding: what the generator avoids is often what
real users say.

## Exercises

1. Design a 4×4 grid for your capstone's users; write the voice
   constraints per persona; set the weights from traffic or targets.
2. Coverage drill: generate 3 queries per cell; compute the coverage
   ratio; top up the zero cells by hand.
3. Voice drill: sample one query per persona; a blind reader matches
   queries to personas ≥75% — the voice landed.