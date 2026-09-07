# Aggregation — GROUP BY, HAVING, Subqueries, CTEs

**What you'll learn:** the aggregation ladder: GROUP BY basics, HAVING vs WHERE, correlated subqueries, and CTEs — climbed as 8 queries of increasing difficulty, the exact shapes the Text2SQL eval will demand.

## 1. GROUP BY — the shapes

```sql
-- 1. total per group
SELECT customer_id, SUM(quantity) AS units
FROM order_items GROUP BY customer_id;

-- 2. count + filter with WHERE (rows) before grouping
SELECT product_id, SUM(quantity) AS units
FROM order_items WHERE quantity > 1
GROUP BY product_id;

-- 3. HAVING filters GROUPS after aggregation
SELECT product_id, SUM(quantity) AS units
FROM order_items
GROUP BY product_id
HAVING SUM(quantity) > 10;
```

| Clause | Filters | Runs |
|---|---|---|
| WHERE | rows | before grouping |
| HAVING | groups | after aggregation |

WHERE-vs-HAVING is the classic Text2SQL error: "products with more than 10 units sold" needs HAVING (a group property); "orders of more than 10 units" needs WHERE (a row property). The schema prompt states it; the eval battery tests it.

## 2. The 8-query ladder

```sql
-- Q1 total revenue
SELECT SUM(oi.quantity * p.unit_price) AS revenue FROM order_items oi
JOIN products p ON p.product_id = oi.product_id;

-- Q2 revenue per month
SELECT substr(o.order_date, 1, 7) AS month,
       SUM(oi.quantity * p.unit_price) AS revenue
FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY month ORDER BY month;

-- Q3 top 3 products by revenue
... ORDER BY revenue DESC LIMIT 3;

-- Q4 customers with more than 3 orders (HAVING)
SELECT customer_id, COUNT(*) AS n FROM orders
GROUP BY customer_id HAVING n > 3;

-- Q5 revenue per customer WITH names (join + group)
SELECT c.name, SUM(oi.quantity * p.unit_price) AS revenue
FROM customers c JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY c.name ORDER BY revenue DESC;

-- Q6 month-over-month change (window or self-join)
-- Q7 products never ordered (LEFT JOIN + IS NULL)
SELECT p.sku FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
WHERE oi.product_id IS NULL;

-- Q8 revenue share per product (subquery for the total)
SELECT p.sku,
       ROUND(100.0 * SUM(oi.quantity * p.unit_price) /
             (SELECT SUM(quantity * unit_price) FROM order_items oi
              JOIN products p2 ON p2.product_id = oi.product_id), 1) AS pct
FROM order_items oi JOIN products p ON p.product_id = oi.product_id
GROUP BY p.sku;
```

The ladder is the Text2SQL eval's blueprint — Q1–Q3 are the basic band, Q6–Q8 the hard band. The W12 capstone task's gold-SQL set is this ladder, seeded.

## 3. CTEs — the readable complex query

```sql
WITH monthly AS (
    SELECT substr(o.order_date, 1, 7) AS month,
           SUM(oi.quantity * p.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY month
)
SELECT month, revenue,
       ROUND(100.0 * revenue / (SELECT SUM(revenue) FROM monthly), 1) AS pct
FROM monthly ORDER BY month;
```

CTEs name intermediate results — the LLM produces dramatically better SQL when the schema prompt shows one CTE example (the W12-03 schema-prompt rule: examples teach shape).

## Exercises

1. Climb the ladder: write Q1–Q8 against your corpus without help; score yourself against the gold SQL.
2. WHERE-vs-HAVING drill: write both interpretations of "products with more than 10 units"; run both; the differing row sets are the lesson.
3. CTE drill: rewrite your Q8 as a CTE; compare readability and identical results.

## 5. The ladder as the eval blueprint (the gold-SQL set)

| Query | Band | Tests |
|---|---|---|
| Q1–Q2 | basic | single table, aggregate, group |
| Q3 | basic | order + limit |
| Q4–Q5 | intermediate | HAVING, joins + group |
| Q6 | hard | time series |
| Q7 | hard | anti-join (IS NULL) |
| Q8 | hard | subquery in SELECT, share math |

The ladder *is* the capstone task's gold-SQL set (file 05-02): eight shapes, banded by difficulty, each with a verifiable numeric gold. The Text2SQL agent's eval reports accuracy per band — "Q1–Q3 at 100%, Q6–Q8 at 40%" is a readable capability map.

## 6. The ladder pin note (the gold-SQL set's record)

```markdown
# Aggregation ladder (W06)
- 8 queries, banded basic/intermediate/hard
- gold SQL committed: tests/gold-sql/q1..q8.sql
- scoring: exact result-set match (values, not formatting)
- per-band accuracy = the Text2SQL capability map
```

The pin note records the ladder as the eval asset — the gold SQL is committed, the scoring is result-based, and the per-band accuracy is the capability map the Text2SQL agent reports.

## Exercises (continued)

4. Band drill: give Q1 and Q8 to the Text2SQL agent (W12 file 03); the per-band accuracy difference is the capability map, measured.
5. Pin drill: write the note; commit the gold SQL files.