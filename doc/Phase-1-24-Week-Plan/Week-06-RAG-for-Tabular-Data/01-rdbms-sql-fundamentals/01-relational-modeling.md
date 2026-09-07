# Relational Modeling — Tables, Keys, Constraints

**What you'll learn:** design the capstone's warehouse tables deliberately: entity modeling, primary/foreign keys, and the constraints that make bad data impossible — each justified by the failure it prevents.

## 1. The capstone's entities

| Entity | Example | Grain |
|---|---|---|
| customers | acme-corp | one company |
| orders | order #1042 | one purchase |
| order_items | 2 × widget-A in order 1042 | one line item |
| products | widget-A | one SKU |

The classic orders schema: `customers 1─n orders 1─n order_items n─1 products`. Every capstone corpus question ("top products by margin", "revenue by quarter") is a walk across these joins.

## 2. The DDL, constraints justified

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id  INTEGER PRIMARY KEY,
    sku         TEXT NOT NULL UNIQUE,
    unit_price  REAL NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date  TEXT NOT NULL,              -- ISO-8601: 'YYYY-MM-DD'
    CHECK (date(order_date) = order_date)
);

CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);
```

| Constraint | Failure it prevents | Without it |
|---|---|---|
| `PRIMARY KEY` | duplicate identities | two rows for one order |
| `REFERENCES` (FK) | orphan line items | items pointing at deleted orders |
| `NOT NULL` | missing identity fields | orders with no date |
| `CHECK (quantity > 0)` | zero/negative quantities | revenue inflated by -5 items |
| `UNIQUE (sku)` | duplicate products | margin summed twice |

Each constraint is a *data-quality contract* — the LLM's SQL queries then operate on data that cannot lie about its shape.

## 3. The synthetic corpus (deterministic, seeded)

```python
import sqlite3, random, datetime

rng = random.Random(42)                     # seeded — reproducible corpus
conn = sqlite3.connect("data/warehouse.duckdb".replace("duckdb", "db"))
conn.executescript(DDL)                     # the §2 script

names = [f"customer-{i:03d}" for i in range(20)]
skus  = [f"SKU-{i:03d}" for i in range(15)]
for day in range(120):                      # ~4 months of orders
    date = (datetime.date(2025, 5, 1) + datetime.timedelta(days=day)).isoformat()
    for _ in range(rng.randint(1, 4)):
        cur = conn.execute(
            "INSERT INTO orders (customer_id, order_date) VALUES (?, ?)",
            (rng.randint(1, 20), date))
        oid = cur.lastrowid
        for pid in rng.sample(range(1, 16), rng.randint(1, 4)):
            conn.execute("INSERT INTO order_items VALUES (?, ?, ?)",
                         (oid, pid, rng.randint(1, 5)))
conn.commit()
```

The seeded corpus gives every Text2SQL experiment the same data — the W10 determinism discipline applied to the warehouse.

## 4. Keys and the agent's citations

| Key type | Agent relevance |
|---|---|
| `customer_id` | joins orders to customers; the LLM's WHERE clauses use them |
| composite PK (order, product) | prevents duplicate line items from double-counting revenue |
| ISO dates | date-range queries parse unambiguously ("Q3" → BETWEEN) |

The modeling decisions above are what make Text2SQL *possible*: ISO dates, integer keys, and constrained quantities give the LLM a schema whose semantics are guessable.

## Exercises

1. Write the DDL for one more entity (e.g., `refunds` referencing orders) with two justified CHECK constraints.
2. Constraint drill: attempt each §2 violation through sqlite3; capture the exact error message — these become the repair loop's vocabulary (W6 file 03).
3. Corpus drill: rebuild the seeded corpus twice; assert identical row counts and identical query results — determinism proven.