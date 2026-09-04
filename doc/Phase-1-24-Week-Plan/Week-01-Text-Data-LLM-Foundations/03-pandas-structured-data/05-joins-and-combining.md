# 03.5 — Joins & Combining Frames

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

---

## What you'll learn

- The four join kinds on one shared dataset — with row-count predictions
- `validate=`, `indicator=`, and the join sanity-check ritual
- `concat` semantics (axis, indexes) and the common surprises
- SQL↔pandas join translation (the W6 bridge)

## 1. The four kinds, on shared data

```python
import pandas as pd

orders = pd.DataFrame({"oid": [1, 2, 3], "cust": ["A", "B", "C"], "amt": [10, 20, 30]})
customers = pd.DataFrame({"cust": ["A", "B", "D"], "tier": ["gold", "silver", "gold"]})

inner = orders.merge(customers, on="cust", how="inner")   # rows 1,2 — 2 rows
left  = orders.merge(customers, on="cust", how="left")    # rows 1,2,3 — 3 rows, C's tier=NaN
right = orders.merge(customers, on="cust", how="right")   # A,B,D — 3 rows, D's amt=NaN
outer = orders.merge(customers, on="cust", how="outer")   # A,B,C,D — 4 rows
```

**Predict the row count before merging** — inner ≤ min(left,right) for unique keys; outer = union. Every join is followed by the sanity check (§3).

## 2. The join sanity-check ritual

```python
m = orders.merge(customers, on="cust", how="left")
assert len(m) >= len(orders), "row count shrank — key collision or bad join"
print("unmatched:", m["tier"].isna().sum())               # NaN segment = unmatched left rows
print("dupes:", m["oid"].duplicated().sum())
```

Three numbers after every join: output rows, unmatched count, duplicate keys. Unmatched NaNs tell you which side lied about referential integrity.

## 3. `validate=` and `indicator=`

```python
orders.merge(customers, on="cust", how="left",
             validate="many_to_one")        # raises if customers.cust isn't unique!

m = orders.merge(customers, on="cust", how="left", indicator=True)
m[m["_merge"] == "left_only"]               # rows with no match — audit them
```

- `validate` asserts the join shape ("many_to_one" = many orders per one customer) — a *free referential-integrity check* that turns silent data corruption into a loud error
- `indicator=True` adds the `_merge` column (left_only/both/right_only) — the audit column for unmatched-row reports

## 4. Non-trivial joins

```python
# different key names
orders.merge(customers, left_on="cust_name", right_on="name")

# overlapping column names
orders.merge(customers, on="cust", suffixes=("_o", "_c"))

# join on multiple keys
sales.merge(targets, on=["region", "product"])

# join on nearest date (as-of) — the time-series join
trades.merge(prices, on="ticker", how="left")     # then:
pd.merge_asof(trades.sort_values("ts"), prices.sort_values("ts"),
              on="ts", by="ticker", direction="backward")
```

`merge_asof` is the least-known high-value join: match each event to the *most recent price/state at or before its timestamp* — the standard join for event-vs-timeseries data, impossible with plain `on=`.

## 5. `concat` — stacking and its surprises

```python
jan = pd.DataFrame({"oid": [1], "amt": [10]}, index=[0])
feb = pd.DataFrame({"oid": [2], "amt": [20]}, index=[0])

pd.concat([jan, feb])                    # index [0, 0] — DUPLICATED labels!
pd.concat([jan, feb], ignore_index=True) # index [0, 1] — what you usually want

pd.concat([jan, feb], axis=1)            # side-by-side — aligns on INDEX, beware!
```

- Vertical concat ignores the old index unless `ignore_index=True` — then `.loc[label]` breaks (W3-02's label discipline)
- Horizontal concat **aligns on index**: unmatched indexes produce NaN columns — sort/normalize indexes first
- Column mismatches fill NaN — check `df.columns` differences before concatenating monthly files

## 6. SQL ↔ pandas join translation (the W6 bridge)

| SQL | pandas |
|---|---|
| `INNER JOIN` | `merge(how="inner")` |
| `LEFT JOIN` | `merge(how="left")` |
| `FULL OUTER JOIN` | `merge(how="outer")` |
| `WHERE b.key IS NULL` | `m[m["_merge"] == "left_only"]` |
| `UNION ALL` | `pd.concat(..., ignore_index=True)` |
| `CROSS JOIN` | `df1.merge(df2, how="cross")` |

## Exercises

1. Row-count oracle: before each of 4 joins, compute the expected count from key cardinalities — verify every prediction on real frames.
2. `validate` drill: introduce a duplicate customer key; show `many_to_one` raising — then decide the fix (dedupe or correct the validate level).
3. `merge_asof` lab: trades + a price table at irregular times — match each trade to the latest prior price; verify 5 spot checks by hand.
4. `concat` audit: concat 12 monthly CSVs with 2 differing columns — find the NaN pattern produced, and fix by normalizing schemas first (W6-02).
5. Anti-join pattern: customers with **zero** orders — via `indicator=True` and via `merge(...) IS NULL` — compare readability and correctness.

## Pitfalls

- **Join key dtype mismatch** — `"001"` vs `1` silently matches nothing; normalize dtypes before merging (W6-01)
- **NaN join keys** — NaN ≠ NaN; rows with NaN keys never match — pre-check nulls in key columns
- **Column-name collisions without suffixes** — `_x`/`_y` defaults lose semantic meaning; use explicit `suffixes=`
- **axis=1 concat on unaligned indexes** — index-alignment surprises; align or reindex deliberately
- **Assuming uniqueness** — duplicate keys multiply rows; `validate=` and the row-count oracle catch it

## Resources

- pandas [merging guide](https://pandas.pydata.org/docs/user_guide/merging.html) — joins, concat, `merge_asof`
- W1-03 parent, W6-01 (SQL joins), W6-02 (cross-store joins by id) — composed here
