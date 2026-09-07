# SQL Families — DDL / DML / DQL Hands-On

**What you'll learn:** the three SQL families in SQLite: DDL (define), DML (modify), DQL (query) — with the agent-safety rule that only DQL ever reaches the model's tool.

## 1. The families, mapped to the agent

| Family | Statements | Who runs it |
|---|---|---|
| DDL | CREATE, ALTER, DROP | *you*, at ingest (never the agent) |
| DML | INSERT, UPDATE, DELETE | *you*, at ingest (never the agent) |
| DQL | SELECT | the agent's tool (read-only, guarded) |

The W10 read-only-first rule at the SQL layer: the model's tool executes DQL only. DDL/DML belong to your ingestion scripts — the schema and the data are *yours*.

## 2. DDL — the shape (recap + new moves)

```sql
-- add a column after the fact (SQLite's limited ALTER):
ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'general';

-- rename (SQLite ≥ 3.25):
ALTER TABLE customers RENAME TO clients;

-- the one you never give the agent:
DROP TABLE order_items;   -- destructive; ingestion scripts only
```

SQLite's ALTER is limited (no drop-column pre-3.35, no constraint changes) — schema evolution happens in your ingestion scripts via the staging pattern (W9 file 04), not via agent calls.

## 3. DML — inserting the corpus

```python
cur = conn.execute(
    "INSERT INTO orders (customer_id, order_date) VALUES (?, ?)",
    (customer_id, date))
order_id = cur.lastrowid

# bulk insert with executemany (the ingestion workhorse):
conn.executemany(
    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
    [(oid, pid, qty) for pid, qty in items])

# update with a WHERE (the guard against table-wide updates):
conn.execute("UPDATE products SET unit_price = ? WHERE product_id = ?",
             (19.99, 7))
```

| DML rule | Why |
|---|---|
| parameterized (`?`) always | string-formatting is the injection door |
| every UPDATE/DELETE has a WHERE | an unguarded UPDATE rewrites the table |
| commit per logical unit | crashes leave consistent states |

## 4. DQL — the family the agent owns

```sql
-- the shapes the agent's Text2SQL will produce:
SELECT product_id, SUM(quantity) AS units
FROM order_items
GROUP BY product_id
ORDER BY units DESC
LIMIT 10;

SELECT o.order_date, SUM(oi.quantity * p.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.order_date BETWEEN '2025-06-01' AND '2025-06-30'
GROUP BY o.order_date
ORDER BY o.order_date;
```

The guarded tool (W12 file 02-04) allows exactly this family: SELECT-only, LIMIT required, allow-listed tables. The agent composes; the tool validates and executes.

## 5. The DQL tool's guard (the SQL validator, preview)

```python
FORBIDDEN = ("insert", "update", "delete", "drop", "alter",
             "create", "attach", "pragma")

def validate_dql(sql: str) -> str | None:
    low = sql.lower().strip()
    if not low.startswith("select"):
        return "blocked: only SELECT statements are allowed"
    if any(w in low for w in FORBIDDEN):
        return "blocked: write/DDL operations are disabled"
    if "limit" not in low:
        return "blocked: add a LIMIT clause (max 100)"
    return None
```

| Check | Blocks |
|---|---|
| starts with SELECT | everything but queries |
| forbidden keywords | write attempts hidden in CTEs/subqueries |
| LIMIT required | runaway full-table scans |

The validator is file 03's full guard in miniature — the agent's DQL tool imports it. The FORBIDDEN list includes `pragma` and `attach` because SQLite's pragmas can change behavior and attach foreign databases — the injection surface is broader than the classic CRUD.

## Exercises

1. Write DDL for a `refunds` table (order reference, amount CHECK > 0, reason); insert 5 seeded refunds.
2. DML drill: attempt an unguarded `UPDATE products SET unit_price = 0`; observe the table-wide damage on a scratch copy — the WHERE rule proven by its absence.
3. DQL drill: write the two query shapes above from memory against your corpus; verify row counts against pandas (file 05's bridge).
4. Validator drill: run the §5 guard against 6 malicious SQL shapes (write, drop, no-limit, pragma, attach, CTE-wrapped write); every one refused.