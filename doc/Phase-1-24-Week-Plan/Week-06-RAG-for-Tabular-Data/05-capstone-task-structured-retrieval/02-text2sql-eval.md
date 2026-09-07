# Text2SQL Eval — Gold-SQL Methodology

**What you'll learn:** the gold-SQL methodology: per-case gold queries
(written by hand, verified by execution), result-set scoring (values,
not strings), and the per-band accuracy report — the ladder (file 01-04)
as the graded eval.

## 1. The gold-SQL set

```python
GOLD_SQL = {
    "q1": {"sql": "SELECT SUM(oi.quantity * p.unit_price) AS revenue "
                  "FROM order_items oi JOIN products p "
                  "ON p.product_id = oi.product_id",
           "gold_result": 48213.75,
           "band": "basic"},
    "q7": {"sql": "SELECT p.sku FROM products p LEFT JOIN order_items oi "
                  "ON oi.product_id = p.product_id WHERE oi.product_id IS NULL",
           "gold_result": ["SKU-013", "SKU-015"],
           "band": "hard"},
    ...
}
```

| Field | Rule |
|---|---|
| `sql` | written by hand, verified by execution |
| `gold_result` | the *result set*, not the query string |
| `band` | basic/intermediate/hard (the ladder) |

The gold is the *result set* — two different SQL formulations producing
the same rows both score. String-matching SQL would penalize valid
alternatives and reward memorized phrasing.

## 2. The result-set scorer

```python
def results_match(gold: list[dict], produced: list[dict],
                  tol: float = 0.01) -> bool:
    if len(gold) != len(produced):
        return False
    for g, p in zip(sorted(gold, key=str), sorted(produced, key=str)):
        for k in g:
            gv, pv = g[k], p.get(k)
            if isinstance(gv, float):
                if abs(gv - float(pv)) > tol:
                    return False
            elif str(gv) != str(pv):
                return False
    return True
```

| Aspect | Handled |
|---|---|
| row count | exact |
| order | sorted before compare (ORDER BY is optional) |
| floats | tolerance 0.01 (rounding differences) |
| strings | exact after normalization |

The scorer compares *result sets* with float tolerance — the SQL can
differ; the answer's numbers must not.

## 3. The per-band accuracy report

```text
# Text2SQL accuracy — gold-SQL v1 — 3 runs, majority
| band        | cases | accuracy | notes |
|---|---|---|---|
| basic       | 3     | 1.00     | — |
| intermediate| 3     | 0.67     | Q5 join order error |
| hard        | 2     | 0.50     | Q8 share math |
| overall     | 8     | 0.75     | — |
```

The per-band report is the capability map (file 01-04's pin note)
populated — the bands where accuracy drops name the schema-prompt
examples to add.

## 5. The gold-SQL pin note (the eval's manifest)

```markdown
# Gold-SQL eval (W06 capstone)
- set: 8 ladder queries + 2 edge-case queries (empty, outlier)
- gold: result sets (values, tolerance 0.01), not query strings
- scoring: results_match() — order-insensitive, float-tolerant
- report: per-band accuracy (basic/intermediate/hard)
```

The pin note is the gold-SQL eval's manifest — the set, the scoring
rules, and the report format. The result-set scorer is the anti-
memorization device: any correct SQL scores.

## Exercises

1. Write gold SQL + result sets for all 8 ladder queries; verify each
   gold by execution.
2. Scorer drill: produce an alternative SQL for Q5 (different join
   order); the result-set scorer must accept it.
3. Band-report drill: run the Text2SQL agent on the ladder; produce the
   per-band accuracy; the weakest band names the schema-prompt fix.
4. Pin drill: write the note; the gold files committed.