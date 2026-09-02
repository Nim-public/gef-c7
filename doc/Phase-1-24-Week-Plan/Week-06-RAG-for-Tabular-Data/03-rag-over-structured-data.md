# 03 — RAG over Structured Data: Text2SQL & the Pipeline

> Week 6 index: [README.md](README.md)

**Session 2 topics:** *Data Retrieval & RAG: Data retrieval, Data formatting and RAG & RAG pipeline.*

---

## What you'll learn

- Why embedding rows usually loses, and what replaces it: **Text2SQL**
- The schema-aware prompt that generates safe, correct, dialect-right SQL
- Validation + execution + error-feedback loops around generated SQL
- Formatting query results into grounded, citable answers
- The full structured-RAG pipeline, end to end

## 1. The pattern inversion

Week 4's RAG: *embed documents, retrieve semantically*. Tabular questions break every assumption:

| Question | What it needs |
|---|---|
| "Total revenue by region?" | aggregation — no chunk contains the answer; it's *computed* |
| "Top 3 customers this year" | sort + limit + a date filter — vectors rank, they don't compute |
| "How many orders in March vs April?" | exact filtering + comparison |
| "Customers who never ordered" | `LEFT JOIN ... IS NULL` — relational reasoning |

The retriever here isn't a vector index — it's **the database itself**, and the LLM's job is to *write the query*:

```
question ─► [schema + question → LLM] ─► SQL ─► validate ─► execute (read-only)
                                                              │ rows
                              answer ◄─ grounded LLM call ◄─ formatted results
```

## 2. The schema prompt (where Text2SQL is won or lost)

The model must see the schema, dialect, and rules — not discover them:

```python
SCHEMA = """
Database: SQLite. Read-only.
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, segment TEXT, since DATE);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                     product TEXT, units INTEGER, price REAL, created_at DATE);

Rules:
- Output ONE SQLite SELECT statement. No INSERT/UPDATE/DELETE/DROP. No semicolon-chaining.
- Today's date is {today}. Use date(created_at) >= date('now', '-30 days') for "last 30 days".
- Prefer explicit column lists over SELECT *.
- Use table aliases. Limit to {row_limit} rows unless asked otherwise.
- If the question can't be answered from these tables, output exactly: -- UNANSWERABLE
"""

def text_to_sql(question: str) -> str:
    prompt = f"{SCHEMA}\n\nQuestion: {question}\nSQL:"
    return client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content.strip().rstrip(";")
```

Design notes:

- **"Today is …"** — date-relative questions ("last month", "this year") are the #1 Text2SQL failure; the model has no clock (file W1-07). Compute "this year" boundaries yourself and hand them over if precision matters
- **`-- UNANSWERABLE` sentinel** — schema-insufficient questions must fail *loudly*, mapping to your existing "I don't have that information" escape
- **Few-shot the tricky shapes** (file W3-01): 2–3 example (question → SQL) pairs covering your date math and your hardest join

## 3. Validation: never execute raw LLM output

```python
import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|pragma)\b", re.I)

def validate_sql(sql: str, max_rows: int = 200) -> str:
    sql = sql.strip().rstrip(";")
    if not sql.upper().startswith(("SELECT", "WITH")):
        raise ValueError("not a read query")
    if FORBIDDEN.search(sql):
        raise ValueError("write/statement keyword present")
    if sql.count(";") > 0:
        raise ValueError("multi-statement rejected")
    if re.search(r"\bselect\b", sql, re.I) and not re.search(r"\blimit\b|\bwith\b", sql, re.I):
        sql += f" LIMIT {max_rows}"          # belt: also enforced at execution
    return sql
```

(Plus the *real* enforcement from file 02: a read-only connection, so even a bypassed validator can't write. Defense in depth: prompt rules → validator → read-only user → row cap.)

## 4. Execution with error feedback (the repair loop)

Generated SQL fails — wrong column, dialect slip, ambiguous alias. The fix is a **feedback loop**, not hope:

```python
def run_query(question: str, retries: int = 2) -> dict:
    sql = text_to_sql(question)
    for attempt in range(retries + 1):
        try:
            rows = conn.execute(sql).fetchall()
            cols = [d[0] for d in conn.execute(sql).description]
            return {"sql": sql, "rows": rows, "cols": cols}
        except sqlite3.Error as e:
            sql = client.chat.completions.create(          # show the model its own error
                model="gpt-4o-mini", temperature=0,
                messages=[{"role": "user", "content":
                    f"{SCHEMA}\nQuestion: {question}\n\nThis SQL failed:\n{sql}\n"
                    f"Error: {e}\nReturn corrected SQL only. SQL:"}],
            ).choices[0].message.content.strip()
    raise RuntimeError(f"SQL failed after retries: {sql}")
```

## 5. Formatting results into grounded answers

Raw tuples aren't answers. Give the model the results *as data* and let it narrate — with the SQL attached for auditability:

```python
def answer_structured(question: str) -> str:
    r = run_query(question)
    table = "\n".join([", ".join(map(str, row)) for row in r["rows"][:20]])
    prompt = f"""Answer the user's question using ONLY this query result.
Mention the number of result rows if relevant. Be concise.

SQL executed:
{r['sql']}

Columns: {r['cols']}
Rows:
{table}

Question: {question}"""
    return client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content + f"\n\n_Query: `{r['sql']}`_"
```

- Result rows get the same `<context>`-style delimiting discipline as Week 4 (W3-02 injection rules — a cell *value* can contain injection text too!)
- Numbers need **units and scale** in the prompt ("revenue in INR") or the model writes confident nonsense around correct numbers
- Empty result set → "No matching records" (not a hallucinated "0")

## Exercises

1. Build the pipeline (schema prompt → validate → execute → format) on your capstone's tables. 10 questions → log generated SQL → hand-verify each against file 01's SQL.
2. Error-repair demo: delete a column from the schema prompt only. Count how many of the 10 queries fail, and how many the retry loop repairs.
3. Attack the validator: craft questions that tempt `UPDATE`/multi-statement/`SELECT * FROM customers` (PII!). Verify all three defenses trip.
4. Date gauntlet: "last 30 days", "this quarter", "since Diwali". Which survive? Improve the date-handling rules in the schema prompt until 3/3 pass.
5. Hybrid routing (capstone seam): a router that sends "how many / top / average / revenue" questions → Text2SQL; "how do I / what is / explain" questions → Week 5's vector RAG. Prototype the router as one classification call (W2-02 zero-shot or W1-07 logprobs) — this is exactly the Week 13 agent's first decision node.

## Pitfalls

- **Schema prompt ≠ actual schema** — drift between prompt and DB is the silent killer; generate the schema block *from* the DB (`PRAGMA table_info`) rather than hand-copying
- **Aggregating on NULLs** — `SUM` skips NULLs silently; `COALESCE` in the SELECT makes counts honest
- **Dates as text** — `"03/04/2026"` sorts before `"03/05/2026"`; store ISO dates
- **One giant prompt doing SQL *and* the answer** — two calls (SQL gen, then answer-from-results) are testable separately; the combined one hides failure stages
- **Believing the formatted answer over the query** — the *result rows* are truth; keep the SQL in the UI (the `_query_` line above)

## Resources

- SQLite Text2SQL references: [b-mc2/sql-create-context](https://huggingface.co/datasets/b-mc2/sql-create-context) & [spider](https://huggingface.co/datasets/xlangai/spider) datasets (the classic Text2SQL eval sets — Week 16 revisits)
- OpenAI Cookbook, *Natural language to SQL* patterns
- LangChain [SQL agent/QA docs](https://python.langchain.com/docs/tutorials/sql/) — the library-ified version of this file (W13/W14 use these)
- [SQLGlot](https://github.com/tobymao/sqlglot) — parse/validate/transpile SQL across dialects (production-grade validator)
