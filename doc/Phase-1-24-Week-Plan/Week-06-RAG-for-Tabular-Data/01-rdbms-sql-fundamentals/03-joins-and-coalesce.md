# Joins — Inner, Left, Zero-Match Cases, COALESCE

**What you'll learn:** the two joins that cover 95% of agent queries — INNER and LEFT — with the zero-match behavior that changes row counts, and the COALESCE patterns that keep results readable.

## 1. INNER JOIN — rows that match

```sql
SELECT o.order_id, c.name, oi.quantity, p.sku
FROM orders o
JOIN customers c      ON c.customer_id = o.customer_id
JOIN order_items oi   ON oi.order_id = o.order_id
JOIN products p       ON p.product_id = oi.product_id
WHERE o.order_date >= '2025-06-01';
```

INNER drops any row without a match on either side — an order with no items, an item with no product, a customer deleted from the table: all silently vanish. For the capstone's constrained corpus (FKs enforced), INNER is safe; for loose data, it hides rows.

## 2. LEFT JOIN — keep the left side

```sql
-- every order, even ones with no items yet:
SELECT o.order_id, COUNT(oi.product_id) AS item_count
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id;
```

LEFT keeps every left-side row; unmatched right columns come back NULL. The zero-match case is where counts lie: `COUNT(oi.product_id)` counts non-NULL matches (0 for empty orders), while `COUNT(*)` counts 1 (the row itself). The agent's Text2SQL gets this wrong constantly — it is a battery case (file 04 of the capstone task).

## 3. The zero-match cases, demonstrated

```sql
-- an order with no items:
INSERT INTO orders (customer_id, order_date) VALUES (1, '2025-08-30');

-- INNER: the order vanishes
SELECT COUNT(*) FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_id = <new_id>;            -- 0 rows

-- LEFT: the order survives, with NULLs
SELECT o.order_id, oi.product_id
FROM orders o LEFT JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_id = <new_id>;            -- 1 row, product_id NULL
```

| Query | INNER result | LEFT result |
|---|---|---|
| order without items | row dropped | row kept, NULLs |
| COUNT(*) vs COUNT(col) | — | 1 vs 0 — the count trap |

## 4. COALESCE — NULLs made readable

```sql
SELECT o.order_id,
       COALESCE(SUM(oi.quantity), 0)                AS units,
       COALESCE(c.name, 'unknown-customer')         AS customer,
       ROUND(COALESCE(SUM(oi.quantity * p.unit_price), 0), 2) AS revenue
FROM orders o
LEFT JOIN customers c   ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
LEFT JOIN products p     ON p.product_id = oi.product_id
GROUP BY o.order_id;
```

| COALESCE use | Effect |
|---|---|
| `COALESCE(SUM(...), 0)` | empty orders show 0, not NULL |
| `COALESCE(name, 'unknown')` | deleted customers stay legible |
| inside ROUND | arithmetic on NULL poisons the result — coalesce first |

The agent instruction that pairs with this: "wrap aggregates in COALESCE so empty groups read as 0" — the W12 schema-prompt rule, taught here by example.

## Exercises

1. Build both join queries over your corpus; verify INNER drops the empty order and LEFT keeps it with NULLs.
2. Count-trap drill: `COUNT(*)` vs `COUNT(oi.product_id)` on the same LEFT JOIN — explain the differing numbers in one sentence.
3. COALESCE drill: rewrite a query whose NULLs propagate (`SUM * price` with NULLs) into the COALESCE pattern; compare outputs.
4. Agent drill: give the Text2SQL tool a join question; check whether the generated SQL uses LEFT or INNER appropriately for "all orders, even empty ones".

## 5. The join-type reference (the other two, for completeness)

| Join | Keeps | Agent use |
|---|---|---|
| INNER | matching rows only | the default for facts |
| LEFT | all left + matches | "all X, even without Y" |
| CROSS | every combination | rare — Cartesian products |
| SELF | a table joined to itself | chains: employee→manager |

CROSS and SELF appear rarely in agent queries, but the self-join shows up in hierarchies (orders referring to other orders). The four-shape table from the parent file is now complete with their zero-match behavior — INNER drops, LEFT keeps, CROSS explodes, SELF relates.

## 6. The join pin note (the counting contract)

```markdown
# Join counting rules (W06)
- LEFT JOIN + COUNT(col): counts matches only (0 for empty)
- LEFT JOIN + COUNT(*): counts rows (1 for empty) — the trap
- aggregates wrapped in COALESCE: empty groups read 0
- every LEFT JOIN query's intent stated: "even without Y" or not
```

The pin note is the counting contract — the Text2SQL schema prompt (file 03) carries these rules verbatim, because the LLM's count-trap errors are the most common wrong-number class in tabular RAG.

## Exercises (continued)

5. Reference drill: write the self-join for a "referred_by" customer column (customer → referring customer); list who referred whom.
6. Pin drill: write the note; the schema prompt inherits the counting rules.