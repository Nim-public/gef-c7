# The pandas ↔ SQL Bridge — read_sql / to_sql

**What you'll learn:** the bridge between the SQL world and the pandas world: `read_sql` for analysis, `to_sql` for loading, and the dtype/index traps that corrupt data crossing it.

## 1. SQL → pandas (the analysis direction)

```python
import pandas as pd, sqlite3

conn = sqlite3.connect("data/warehouse.db")

df = pd.read_sql(
    "SELECT o.order_date, p.sku, oi.quantity, p.unit_price "
    "FROM orders o JOIN order_items oi ON oi.order_id = o.order_id "
    "JOIN products p ON p.product_id = oi.product_id", conn)
df["order_date"] = pd.to_datetime(df["order_date"])   # TEXT → datetime
df["revenue"] = df["quantity"] * df["unit_price"]
```

| Trap | Symptom | Fix |
|---|---|---|
| dates as TEXT | `df.order_date.dt` fails | `pd.to_datetime` after read |
| INTEGER → float (NULLs) | ids show as 10.0 | `astype("Int64")` (nullable) |
| params with `?` vs `%s` | driver errors | use the `params=(...)` list |

`read_sql` returns everything as loose dtypes (SQLite has no schema-enforced types at the connection); the *explicit* dtype conversion after the read is part of the bridge contract.

## 2. Parameterized reads

```python
q = ("SELECT p.sku, SUM(oi.quantity) AS units FROM order_items oi "
     "JOIN products p ON p.product_id = oi.product_id "
     "WHERE oi.order_id IN (SELECT order_id FROM orders WHERE order_date >= ?) "
     "GROUP BY p.sku ORDER BY units DESC")
df = pd.read_sql(q, conn, params=("2025-07-01",))    # never f-strings
```

Parameterized reads are the SQL-injection wall carried into pandas — f-string interpolation of user values into `read_sql` is the same door the W12 validator blocks.

## 3. pandas → SQL (the loading direction)

```python
products_df = pd.DataFrame({
    "sku": [f"SKU-{i:03d}" for i in range(1, 16)],
    "unit_price": [round(5 + i * 1.7, 2) for i in range(15)],
    "category": "general",
})
products_df.to_sql("products_stage", conn, if_exists="replace", index=False)

# promote with SQL (constraints enforced by the real table):
conn.execute("INSERT INTO products SELECT product_id, sku, unit_price FROM products_stage")
```

| `to_sql` trap | Symptom | Fix |
|---|---|---|
| `index=True` default | a junk `index` column | `index=False` |
| `if_exists="fail"` default | second run crashes | staging + promote pattern |
| dtype inference | TEXT where you wanted REAL | stage table + typed INSERT |

The staging pattern: `to_sql` into a `_stage` table (no constraints), then `INSERT INTO ... SELECT` into the constrained real table — the constraints are enforced by SQL, not by pandas' guesses.

## 4. The bridge in the dual pipeline (W12 file 04)

| Direction | Use |
|---|---|
| SQL → pandas | the agent's `run_sql_query` returning frames for charts |
| pandas → SQL | your ingestion scripts loading new data |

The W12 analytics toolkit's `render_chart` executes SQL through this bridge — the chart is derived from executed queries over constrained data, not from pandas guesses.

## 5. The bridge pin note (the dtype contract's record)

```markdown
# pandas↔SQL bridge (W06)
- driver: sqlite3 stdlib, parameterized reads only
- read: pd.read_sql + explicit dtype conversion (dates, nullable ints)
- write: to_sql → staging table → INSERT INTO ... SELECT (constraints hold)
- index=False on every to_sql
```

The pin note is the bridge's contract — the dtype conversions and the staging pattern are the data-integrity rules for everything crossing between the worlds. The W12 analytics toolkit inherits this contract.

## 6. The bridge drill record (the two-path equality proof)

```text
SQL path:    SELECT month, SUM(...) → [2025-05: 412.50, 2025-06: 388.20, ...]
pandas path: df.groupby(month).revenue.sum() → identical values
delta:       0.00 on every month
```

The record is the bridge's acceptance proof — the same aggregation
computed through both worlds, equal to the cent. The W9-04 evaluation
philosophy (two computation paths agreeing) applied to the SQL/pandas
boundary.

## 7. The bridge quiz (self-tested)

**Task:** answer without notes: (a) why parameterize `read_sql` even
locally? (b) why does `to_sql` go to a staging table? (c) why do ids
become floats after a read with NULLs? (d) why does the monthly revenue
match to the cent across both paths? One paragraph each.

**Worked approach:** the quiz is the bridge contract's compression
test — the answers name the traps by mechanism (type inference,
constraint enforcement, nullable dtypes, determinism).

**Pass criterion:** four paragraphs mechanically correct; added to the
recap sheet family.

## Exercises (continued)

5. Record drill: produce §6's two-path proof for the monthly revenue;
   commit it beside the pin note.