# 01 — RDBMS & SQL Fundamentals

> Week 6 index: [README.md](README.md)

**Session 1 topics:** *Introduction to RDBMS: Concepts of Tables, Data types, Indices & constraints. SQL Queries: Data Definition, Data Manipulation, Data Query, Joins.*

---

## What you'll learn

- Relational modeling: tables, keys, relationships, constraints
- The three SQL families: DDL, DML, and query (SELECT) — with joins and aggregation
- Indices: what they buy, what they cost
- Enough hands-on SQL that Text2SQL (file 03) becomes *checkable* — you must be able to verify what the LLM writes

## 1. Relational concepts

A **table** = rows (entities) × columns (attributes), each column with a fixed **type**. Tables relate through keys:

```sql
CREATE TABLE customers (                    -- DDL: define structure
    id INTEGER PRIMARY KEY,                 -- uniqueness + index for free
    name TEXT NOT NULL,
    segment TEXT CHECK (segment IN ('smb', 'enterprise')),
    since DATE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),   -- foreign key: the relationship
    product TEXT NOT NULL,
    units INTEGER CHECK (units > 0),
    price REAL NOT NULL,
    created_at DATE DEFAULT (date('now'))
);
```

**Constraints** (`PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`) are integrity enforced by the database, not by your app code. They matter doubly in LLM pipelines: they make *bad generated SQL* fail loudly instead of corrupting data.

Types that matter for LLM work: `INTEGER`/`REAL` (numbers → comparisons work), `TEXT` (exact match needs care), `DATE` (the "#1 Text2SQL bug generator" — see file 03), `NULL` (three-valued logic; `= NULL` never matches — use `IS NULL`).

**Indices**: speed lookups on a column, cost write time + space:

```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_created ON orders(created_at);
```

Rule: index columns you filter/join/sort on. For this week's scale, keys + one or two hot columns is plenty.

## 2. The three SQL families

| Family | Statements | Role |
|---|---|---|
| **DDL** — Data Definition | `CREATE`, `ALTER`, `DROP` | structure |
| **DML** — Data Manipulation | `INSERT`, `UPDATE`, `DELETE` | contents |
| **DQL** — Data Query | `SELECT` (+ joins, aggregates) | reading — where Text2SQL lives |

**Capstone rule:** your LLM gets **read-only** DQL. Write access goes through validated, parameterized application code — a hallucinated `UPDATE` without a `WHERE` clause is a data-loss incident. (Enforce with a read-only DB user; see file 02.)

## 3. Querying: the 80% you need

```sql
-- projection + filter + order
SELECT id, product, units * price AS revenue
FROM orders
WHERE created_at >= '2026-01-01' AND product = 'GPU'
ORDER BY revenue DESC
LIMIT 10;

-- aggregation (the Text2SQL workhorse)
SELECT region, COUNT(*) AS orders, SUM(units * price) AS revenue
FROM orders
GROUP BY region
HAVING SUM(units * price) > 100000       -- HAVING filters groups; WHERE filters rows
ORDER BY revenue DESC;
```

### Joins — the four kinds, one example

```sql
-- every order + its customer's segment
SELECT o.id, c.name, c.segment, o.units * o.price AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id;      -- INNER: only matches

-- keep ALL customers, even order-less ones (Nullif­ed order columns)
SELECT c.name, COUNT(o.id) AS n_orders, COALESCE(SUM(o.units * o.price), 0) AS revenue
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY revenue DESC;
```

- `INNER JOIN` — rows with matches in both
- `LEFT JOIN` — all left rows + matches (the "customers with zero orders" tool)
- `RIGHT/FULL` — rare in practice; know they exist
- Alias everything (`orders o`) — Text2SQL output is far more readable with aliases, and so is your review

Subqueries and CTEs (read these — generated SQL uses them constantly):

```sql
WITH top_regions AS (
    SELECT region, SUM(units * price) AS rev FROM orders GROUP BY region
)
SELECT * FROM top_regions WHERE rev > 100000 ORDER BY rev;
```

## 4. SQLite hands-on (stdlib, zero install)

```python
import sqlite3

conn = sqlite3.connect("capstone.db")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript(open("schema.sql").read())

conn.executemany(
    "INSERT INTO orders (customer_id, product, units, price) VALUES (?, ?, ?, ?)",
    [(1, "GPU", 2, 45000.0), (2, "CPU", 10, 5500.0)],
)
conn.commit()

for row in conn.execute(
    "SELECT c.name, SUM(o.units * o.price) FROM orders o "
    "JOIN customers c ON c.id = o.customer_id GROUP BY c.id ORDER BY 2 DESC"):
    print(row)
```

Pandas interop (Week 1 file 03 pays off):

```python
import pandas as pd
df = pd.read_sql("SELECT * FROM orders", conn)      # DataFrame ↔ SQL is a two-way door
df.to_sql("orders", conn, if_exists="replace", index=False)
```

## Exercises

1. Model your capstone domain as 3+ tables with keys and two constraints. Justify each constraint in one line.
2. Write 8 queries of increasing difficulty on it: filter, aggregate+group, inner join, left join with COALESCE, HAVING, subquery, CTE, ORDER+LIMIT.
3. The "zero orders" question: rewrite the LEFT JOIN so customers with no orders appear with revenue 0 — then as a NOT EXISTS subquery. Which is clearer?
4. Insert 50 synthetic rows (Week 1 f-strings + random); break a CHECK constraint deliberately and read the error.
5. Load a CSV with pandas → `to_sql` → answer 3 business questions in SQL that would be painful in pandas groupby chains. Feel the boundary between the two tools.

## Pitfalls

- **`WHERE` vs `HAVING`** — filtering rows before grouping vs groups after; generated SQL confuses them constantly (review hook!)
- **NULL comparisons** — `WHERE col = NULL` silently matches nothing; `IS NULL` / `COALESCE`
- **Implicit cross joins** — comma-joins without a proper `ON` → row-count explosion; always check result counts (Week 1 discipline)
- **String vs numeric columns** — `'45000'` sorts alphabetically; force dtypes at insert (pandas `to_sql` does this from the DataFrame)
- **Write access for generated SQL** — no, seriously, read-only connections (file 03 enforces it)

## Resources

- SQLite [docs](https://sqlite.org/docs.html) + [SQL as understood by SQLite](https://sqlite.org/lang.html) — the dialect you'll run
- sqlbolt.com — interactive SQL course, joins section is exactly this file
- Mode SQL tutorial — analytics-flavored practice
- W3Schools SQL — quick syntax reference (fine for lookup, not for depth)
