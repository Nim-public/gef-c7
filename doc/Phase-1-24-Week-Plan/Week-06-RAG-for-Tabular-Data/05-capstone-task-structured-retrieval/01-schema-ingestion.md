# Schema & Ingestion — Constraints, Synthetic Data Discipline

**What you'll learn:** the capstone task's foundation: the constrained
warehouse schema (file 01, extended), the synthetic data generator with
edge cases by design, and the ingestion idempotency that makes the
rebuild safe.

## 1. The extended schema (beyond file 01's base)

```sql
CREATE TABLE refunds (
    refund_id   INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(order_id),
    amount      REAL NOT NULL CHECK (amount > 0),
    reason      TEXT NOT NULL,
    refund_date TEXT NOT NULL CHECK (date(refund_date) = refund_date)
);

CREATE TABLE customer_notes (
    note_id     INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    note        TEXT NOT NULL           -- free text → also vector-indexed
);
```

| Addition | Why |
|---|---|
| `refunds` | negative-revenue queries; the SQL-vs-RAG boundary case |
| `customer_notes` | free text in a relational table → the hybrid bridge |

`customer_notes` is the deliberate boundary case: free text living in a
*relational* table. It routes to vector retrieval (serialized), while
its FK links back to SQL — the cross-store join (file 04) has a natural
home.

## 2. The synthetic generator with edge cases by design

```python
def generate_corpus(seed: int = 42) -> dict:
    rng = random.Random(seed)
    return {
        "orders": gen_orders(rng, 300),
        "empty_orders": gen_orders(rng, 5, items=False),   # the zero-match case
        "high_value": gen_orders(rng, 3, min_total=5000),  # the outlier case
        "refunds": gen_refunds(rng, 12),
        "notes": gen_notes(rng, 30),                       # includes PII-shaped text
    }
```

| Edge case | Tests |
|---|---|
| empty orders | the LEFT JOIN count trap |
| high-value outliers | "top product" stability |
| refunds | net-revenue queries (SUM minus refunds) |
| PII-shaped notes | the red-team battery's masking |

The edge cases are *designed* — each one exists to trigger a specific
failure mode the eval set grades. The PII-shaped notes feed the W15
masking drills with realistic data.

## 3. Ingestion idempotency (the rebuild-safe pattern)

```python
def rebuild_warehouse(seed: int = 42):
    for table in ("order_items", "orders", "products", "customers",
                  "refunds", "customer_notes"):
        conn.execute(f"DELETE FROM {table}")
    # ... re-run the generator; the counts must match the manifest
```

| Property | Check |
|---|---|
| rebuild determinism | same seed → same counts, same query results |
| delete order | children before parents (FK order) |
| post-rebuild validation | the row-count parity vs the manifest |

The rebuild is the ingestion's acceptance test: two rebuilds produce
identical databases (the determinism drill from file 01).

## Exercises

1. Extend the schema with `refunds` and `customer_notes`; the CHECKs
   and FKs verified by violation attempts.
2. Generator drill: produce the corpus with all edge-case families; the
   counts recorded; the rebuild determinism proven.
3. PII drill: confirm the notes' PII-shaped text triggers the masking
   layer (W15 file 03) when serialized for vector search.