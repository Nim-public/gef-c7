# Repair Loops — Error Feedback Retries

**What you'll learn:** the repair loop: when generated SQL errors, the
error message becomes the *next prompt's input* — bounded, instructive,
and measured. The W10 failure-phrasing discipline applied to SQL.

## 1. The loop

```python
def text2sql_with_repair(question: str, schema_prompt: str, conn,
                         max_attempts: int = 3) -> dict:
    feedback = ""
    for attempt in range(1, max_attempts + 1):
        sql = llm_sql(schema_prompt, question, feedback)
        if (err := validate_dql(sql)):
            feedback = f"Your SQL was rejected: {err}. Rewrite it."
            continue
        try:
            rows = execute(sql, conn)
            return {"sql": sql, "rows": rows, "attempts": attempt}
        except Exception as e:
            feedback = (f"SQLite error: {e}. Check table/column names "
                        f"against the schema. Rewrite the query.")
    return {"error": f"failed after {max_attempts} attempts",
            "last_sql": sql, "degraded": True}
```

| Attempt | Input to the LLM |
|---|---|
| 1 | schema prompt + question |
| 2 | + the SQLite error, phrased as guidance |
| 3 | + the second error (or give up honestly) |

The loop is the W10 hand-rolled ReAct's repair path, SQL-specialized:
errors are *observations* (file 05-02's formatting), the attempt counter
is the bound (file 01-03), and the failure is honest.

## 2. The error→hint mapping (the vocabulary from file 01)

| SQLite error | Hint |
|---|---|
| `no such table: ordres` | "did you mean orders? Tables: orders, products…" |
| `no such column: Date` | "date columns are ISO TEXT named order_date" |
| `near "FROM": syntax error` | "check clause order: SELECT … FROM … WHERE … GROUP BY" |
| `misuse of aggregate` | "aggregates need GROUP BY or a single-row SELECT" |

Each hint translates the engine's error into the *actionable* form —
the W10 file 05-04 phrasing rules (constraint, shape, next action). The
mapping table is data (a dict), versioned with the schema prompt.

## 3. The loop's metrics (the repair effectiveness)

| Metric | Definition | Healthy |
|---|---|---|
| first-pass rate | correct on attempt 1 | >70% |
| repair success | attempt-2 success / failed-at-1 | >60% |
| exhaustion rate | failed after max attempts | <5% |
| attempts histogram | the distribution | median 1 |

```python
def repair_metrics(runs: list[dict]) -> dict:
    total = len(runs)
    first = sum(1 for r in runs if r["attempts"] == 1)
    exhausted = sum(1 for r in runs if r.get("degraded"))
    return {"first_pass": first / total, "exhausted": exhausted / total}
```

The metrics are the repair loop's report card — a rising exhaustion
rate means the schema prompt is drifting from the schema, or the
questions outgrew the examples.

## 5. The repair pin note (the loop's manifest)

```markdown
# Text2SQL repair loop (W06)
- bound: 3 attempts (the W10 file 01-03 rule)
- hint map: 4 error classes → actionable hints (versioned)
- metrics: first-pass >70%, exhaustion <5%
- battery: the 8-query ladder through the loop
```

The pin note is the loop's manifest — the bound, the hint map, the
metrics thresholds, and the battery. The hint map's version stamps the
error→hint translations.

## Exercises

1. Implement the loop; run the 8-query ladder (file 01-04) through it;
   produce the attempts histogram.
2. Hint drill: for each §2 error class, force the error; verify the hint
   steers the retry to success — the mapping table, validated.
3. Exhaustion drill: ask an unanswerable question (a table that doesn't
   exist); the loop must exhaust honestly with the degraded flag.
4. Pin drill: write the note; the histogram committed.