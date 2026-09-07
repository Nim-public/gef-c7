# The Decision Tree — SQL vs Paste vs Hybrid per Data Shape

**What you'll learn:** the routing decision for tabular data: which
data shape goes to SQL, which gets pasted into context, and which needs
the hybrid bridge — the W12 dual-pipeline decision, per data shape.

## 1. The decision tree

```text
tabular data arrives
├─ too big for context (>50 rows or >10 cols)?
│   ├─ yes → SQL (Text2SQL over ingested tables)
│   └─ no ↓
├─ needs aggregation (SUM/AVG/COUNT)?
│   ├─ yes → SQL (numbers are computed, never estimated)
│   └─ no ↓
├─ needs semantic search ("which row mentions…")?
│   ├─ yes → HYBRID (serialize rows → vector retrieval)
│   └─ no ↓
└─ small lookup table (<20 rows)? → PASTE into the prompt
```

| Shape | Route | Why |
|---|---|---|
| wide/deep tables | SQL | context can't hold them |
| aggregates | SQL | exact math from rows |
| semantic row-finding | hybrid | "which product mentions waterproof" |
| tiny lookup tables | paste | zero retrieval cost |

The tree is the W12-04 dual-pipeline routing, refined by *data shape*
rather than query phrasing — the shape is measurable at ingest time.

## 2. The routing implementation

```python
def route_data(data_path: str) -> str:
    df = peek(data_path)                       # header + row count only
    rows, cols = len(df), len(df.columns)
    numeric_cols = df.select_dtypes("number").shape[1]
    if rows > 50 or cols > 10:
        return "sql"                           # ingest and use Text2SQL
    if numeric_cols >= 3:
        return "sql"                           # aggregation likely
    return "paste"                             # small enough for context
```

| Measured property | Threshold | Route |
|---|---|---|
| rows | >50 | sql |
| columns | >10 | sql |
| numeric columns | ≥3 | sql |
| everything else | — | paste |

The router is measurable at ingest — no model call needed for the
shape decision. The semantic-search route is chosen per *query*, not
per file (a pasted table can still be searched if it grows).

## 3. The per-route guarantees

| Route | Guarantee | Guard |
|---|---|---|
| SQL | exact aggregates, constrained | validator + ro connection |
| paste | full visibility of every cell | context budget respected |
| hybrid | semantic row-finding | serialization quality (file 02) |

Each route's guarantee is what the other routes cannot offer: SQL
computes, paste shows everything, hybrid finds semantically. The
routing errors are measurable — a "paste" of a 10k-row table blows the
budget; an SQL route on a semantic question returns nothing useful.

## 5. The decision-tree pin note (the router's record)

```markdown
# Data-shape routing (W06)
- thresholds: rows>50, cols>10, numeric_cols≥3 → sql
- else: paste (context-resident)
- hybrid: chosen per query (semantic row-finding)
- measured at ingest: no model call for the shape decision
- battery: 6 files, boundary drill, misroute drill
```

The pin note is the router's record — thresholds, routes, and the
battery. The shape decision is deterministic; the battery proves the
edges.

## Exercises

1. Implement `route_data`; run it on 6 data files of varying shapes;
   verify the routes against hand decisions.
2. Boundary drill: a 49-row vs 51-row table — the route flips; verify
   the flip and document the threshold.
3. Misroute drill: force the wrong route (SQL on a semantic question);
   record the failure mode — the tree's edges, proven by their
   violation.
4. Pin drill: write the note; the battery results cited.