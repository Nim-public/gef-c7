# Schema Prompts — Generated-from-DB, Dialect Rules, Date Grounding

**What you'll learn:** the schema prompt — where Text2SQL is won or
lost: generated directly from the database catalog, carrying the
dialect rules and date semantics, with the examples that teach the
model the query shapes.

## 1. Generated-from-DB, never hand-typed

```python
def build_schema_prompt(conn) -> str:
    parts = ["Database schema (SQLite dialect):"]
    for (name, sql) in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table'"):
        parts.append(f"{sql};")
    parts.append("Date columns are ISO-8601 TEXT. For months use "
                 "substr(col, 1, 7). For date ranges use BETWEEN.")
    return "\n\n".join(parts)
```

| Rule | Why |
|---|---|
| read `sqlite_master` | the prompt cannot drift from the real schema |
| include the DDL verbatim | the LLM sees exact column names/types |
| state the dialect | the DATE_FORMAT/strftime class of errors dies |
| ground the dates | "Q3" → BETWEEN '2025-07-01' AND '2025-09-30' |

The hand-typed schema prompt drifts the moment a column is added —
generating it from the catalog makes drift impossible. The drift is the
W11 parity lesson, applied to prompts.

## 2. Date grounding (the most common Text2SQL failure)

| User phrase | Grounded SQL |
|---|---|
| "this quarter" | `BETWEEN date('now', 'start of month', '-3 months') AND ...` |
| "last 30 days" | `>= date('now', '-30 days')` |
| "Q3 2025" | `BETWEEN '2025-07-01' AND '2025-09-30'` |
| "in June" | `substr(order_date,1,7) = '2025-06'` |

The date rules are stated in the schema prompt *with examples* — the
model learns the corpus's date semantics (ISO TEXT, not native DATE)
from the prompt instead of guessing.

## 3. The schema prompt's structure

```text
[1] dialect declaration       "SQLite. Use strftime, ||, LIMIT."
[2] full DDL                  from sqlite_master
[3] date semantics            ISO TEXT + the four grounding patterns
[4] one worked CTE example    (file 01-04's Q8)
[5] counting rules            COALESCE, COUNT(col) vs COUNT(*)
[6] the task                  "Write ONE SELECT statement. LIMIT 100."
```

Each block is a failure class from file 01's ladder, pre-answered. The
worked example teaches shape better than any instruction — the few-shot
principle from W14 file 01-03, applied to SQL.

## Exercises

1. Generate the schema prompt from your DDL; diff it against the
   hand-written version; adopt the generated one.
2. Date-grounding drill: query "revenue in June" three phrasings; all
   three must resolve to the same BETWEEN clause.
3. Dialect drill: remove the dialect declaration; give a monthly-revenue
   question; observe the MySQL dialect error; restore.