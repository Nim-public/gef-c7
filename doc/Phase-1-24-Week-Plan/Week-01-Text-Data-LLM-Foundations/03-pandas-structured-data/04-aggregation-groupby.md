# 03.4 — Aggregation & groupby Mechanics

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

---

## What you'll learn

- groupby as split-apply-combine — the mental model that predicts its behavior
- Named aggregation, multiple functions, per-column control
- `pivot_table`/`crosstab` and reshaping (`melt`, `stack/unstack`)
- Window functions (`rolling`, `expanding`) and time-based grouping

## 1. Split-apply-combine — the mental model

```
df ──split by key──► [group1 rows, group2 rows, ...]
        ──apply f to each──► [partial1, partial2, ...]
        ──combine──► result frame
```

Every groupby question reduces to: *what is the key, what function applies to which columns, what shape returns?*

```python
orders.groupby("region")["revenue"].sum()                       # Series out
orders.groupby("region").agg(revenue=("revenue", "sum"),        # DataFrame out (named!)
                             n=("order_id", "count"))
```

**Named aggregation** is the production form — explicit output names, no MultiIndex surprises:

```python
orders.groupby("region", as_index=False).agg(
    total_revenue=("revenue", "sum"),
    avg_units=("units", "mean"),
    n_orders=("order_id", "count"),
)
```

## 2. The groupby gotchas, demonstrated

```python
g = orders.groupby("region")
# 1. NaN keys are DROPPED silently:
orders_with_nan = pd.concat([orders, pd.DataFrame([{"region": None, "revenue": 1}])])
g2 = orders_with_nan.groupby("region", dropna=False)     # ← keep them, deliberately

# 2. filter GROUPS (not rows):
big = g.filter(lambda sub: sub["revenue"].sum() > 50000)  # whole groups kept/dropped

# 3. transform: per-group value broadcast back to rows
orders["region_avg"] = g["revenue"].transform("mean")     # same length as df!
```

`transform` vs `agg` vs `filter` — the trio: agg shrinks (one row per group), transform broadcasts (same length), filter selects whole groups. Every "per-group share of total" computation is `groupby.transform` — e.g., `df["share"] = df["revenue"] / g["revenue"].transform("sum")`.

## 3. Reshaping: pivot, melt, stack/unstack

```python
piv = orders.pivot_table(index="region", columns="product",
                         values="revenue", aggfunc="sum", fill_value=0)

long = piv.reset_index().melt(id_vars="region",                    # wide → long
                              var_name="product", value_name="revenue")
```

`pivot_table` = groupby + reshape (with margins=`True` for totals); `melt` is its inverse (wide→long). Long format is what plotting libraries and databases want; wide is what humans read. `stack/unstack` move between the shapes on MultiIndexed frames.

## 4. Time-based grouping and windows

```python
daily = orders.set_index("created_at")
weekly = daily.resample("W")["revenue"].sum()            # calendar-aware grouping
trend  = daily["revenue"].rolling(7).mean()               # 7-day trailing mean
cum    = daily["revenue"].expanding().sum()               # running total
```

`resample` requires a DatetimeIndex (W6-03's date rules apply at ingest). `rolling(7)` gives trend lines for the W12-04 analytics agent's charts — one line, no loop.

## 5. The revenue-report pattern (everything composed)

```python
report = (
    orders.assign(revenue=lambda d: d["units"] * d["price"])
          .merge(customers, on="customer", how="left", validate="many_to_one")
          .groupby(["segment", "region"], as_index=False)
          .agg(total_revenue=("revenue", "sum"), n_orders=("order_id", "count"))
          .sort_values("total_revenue", ascending=False)
)
```

Method chaining (assign → merge → groupby → sort) with lambda-`assign` keeps every step auditable — the idiomatic style the parent file introduced, now with mechanics understood.

## Exercises

1. Diagnose by group: for each region, top product by revenue (groupby + `idxmax`/sort + `groupby.head(1)`).
2. `transform` workout: add columns for per-group z-scores and share-of-group-total without merging a summary table back.
3. Pivot round-trip: pivot to wide, `melt` back to long — verify the round-trip is lossless on your data (what breaks with duplicate index/column pairs?).
4. Resample drill: daily revenue → weekly sums → 4-week rolling mean → plot (W1-04's file output discipline).
5. The share-of-total bug: compute per-region share with `sum()` twice (once per group, once global) — find the version that's wrong and explain the double-counting.

## Pitfalls

- **`as_index` surprises** — group keys become the index; `as_index=False` or `reset_index()` when downstream code expects columns
- **NaN groups dropped silently** — `dropna=False` when missing keys are meaningful
- **`agg` on non-numeric columns** — `sum` on strings concatenates; select columns explicitly
- **Resample without a sorted DatetimeIndex** — sort first
- **Rolling windows on unsorted time** — rolling assumes order; sort before computing

## Resources

- pandas [groupby user guide](https://pandas.pydata.org/docs/user_guide/groupby.html) — split-apply-combine, transformations
- pandas [reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html) — pivot/melt/stack
- W1-03 parent, W6-01 (GROUP BY/HAVING analogies), W12-04 (analytics consumer) — composed here
