# 03 — Structured Data with Pandas

> Week 1 index: [README.md](README.md)

**Session 1 topic:** *Structured Data (Pandas): Selection, filtering, aggregation, joins.* Structured data is everywhere in enterprise AI — Text2SQL (Week 4), RAG over tables (Week 6), analytics agents (Week 12) all assume you can slice a DataFrame blindfolded.

---

## What you'll learn

- Series vs DataFrame; loading data; inspecting datasets
- Selecting with `[]`, `.loc`, `.iloc`, and boolean masks
- Filtering with vectorized conditions, `isin`, `between`, `str.contains`
- Aggregating with `groupby`, `agg`, `pivot_table`, `value_counts`
- Combining datasets with `merge`, `concat`, and knowing which join you want

## 0. Setup and the demo dataset

```powershell
pip install pandas
```

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id":  [1001, 1002, 1003, 1004, 1005, 1006],
    "customer":  ["Asha", "Ravi", "Asha", "Meera", "Ravi", "Sam"],
    "region":    ["south", "north", "south", "east", "north", "west"],
    "product":   ["GPU", "CPU", "GPU", "GPU", "RAM", "CPU"],
    "units":     [2, 10, 1, 4, 16, 8],
    "price":     [45000.0, 5500.0, 45000.0, 45000.0, 2000.0, 5500.0],
})
orders["revenue"] = orders["units"] * orders["price"]
```

First-look ritual for any new dataset:

```python
df.head()        # first rows
df.shape         # (rows, cols)
df.info()        # dtypes + non-null counts
df.describe()    # numeric summary
df["region"].value_counts()
df.isna().sum()  # missing values per column
```

## 1. Selection

```python
orders["customer"]                     # one column -> Series
orders[["customer", "revenue"]]        # multiple columns -> DataFrame
orders.iloc[0]                         # first ROW by position
orders.iloc[0, [1, 5]]                 # row 0, columns 1 and 5 by position
orders.loc[2, "customer"]              # by LABEL (index label here)
orders.loc[orders.index[:3], ["customer", "revenue"]]
```

**Rule of thumb:** `.iloc` = integer position, `.loc` = label + boolean mask. Never chain brackets (`df[cols][rows]`) — that's the path to `SettingWithCopyWarning`.

## 2. Filtering

```python
orders[orders["region"] == "south"]                    # single condition
orders[(orders["region"] == "south") & (orders["units"] > 1)]   # & | ~ (not and/or)
orders[orders["product"].isin(["GPU", "CPU"])] if "product" in orders else None
orders[orders["revenue"].between(5000, 50000)]
orders[orders["customer"].str.startswith("A")]

orders.query("region == 'south' and units > 1")        # same thing, readable
```

Everything is **vectorized** — conditions produce boolean Series, never Python loops:

```python
orders["expensive"] = orders["price"] > 10000          # new column, whole column at once
orders["discounted"] = orders["price"] * 0.9
```

## 3. Aggregation

```python
orders["revenue"].sum()                       # single number
orders["region"].value_counts()               # frequency table

orders.groupby("region")["revenue"].sum()
orders.groupby("region").agg(
    orders=("order_id", "count"),
    total_revenue=("revenue", "sum"),
    avg_units=("units", "mean"),
)
orders.groupby(["region", "product"], as_index=False)["revenue"].sum()
```

Multiple statistics per group, multiple columns:

```python
orders.groupby("customer").agg({
    "revenue": ["sum", "mean"],
    "units": "sum",
})
```

Pivot tables (spreadsheet-style) and crosstabs:

```python
pd.pivot_table(orders, index="region", columns="product",
               values="revenue", aggfunc="sum", fill_value=0)
pd.crosstab(orders["region"], orders["product"])
```

For time series (you'll need this for eval dashboards in Week 16): `resample("W").sum()`, `rolling(7).mean()`.

## 4. Missing data

```python
orders.isna().sum()                  # count NaNs
orders.dropna(subset=["customer"])   # drop rows missing a key column
orders.fillna({"units": 0, "price": orders["price"].median()})
orders["region"].fillna("unknown")
```

Decide *deliberately*: drop, fill with constant, fill with statistic, or flag-and-keep. Silent defaults create silent bias.

## 5. Joins

SQL-style joins, one call:

```python
customers = pd.DataFrame({
    "customer": ["Asha", "Ravi", "Meera", "Sam"],
    "segment":  ["enterprise", "smb", "enterprise", "smb"],
    "since":    [2021, 2023, 2022, 2024],
})

orders.merge(customers, on="customer", how="inner")   # only matched customers
orders.merge(customers, on="customer", how="left")    # keep all orders, NaN segment if unknown
orders.merge(customers, on="customer", how="outer")   # keep everything from both sides
```

| `how` | keeps |
|---|---|
| `"inner"` | rows with matches in **both** tables (default) |
| `"left"` | all rows from the left table + matches from right |
| `"right"` | all rows from the right table |
| `"outer"` | all rows from both tables |

Variants you'll actually hit:

```python
orders.merge(customers, left_on="cust_name", right_on="name")   # different key names
orders.merge(customers, on="customer", suffixes=("_o", "_c"))   # overlapping column names
pd.concat([jan_df, feb_df], ignore_index=True)                  # stack rows
pd.concat([df1, df2], axis=1)                                   # side-by-side columns
orders.merge(customers, on="customer", validate="many_to_one")  # assert join shape!
```

`validate=` catches duplicate-key surprises early — cheap insurance on real data.

### Sanity-check every join

```python
m = orders.merge(customers, on="customer", how="left")
len(m), m["segment"].isna().sum()     # row growth? unmatched keys?
```

## Worked mini-project: revenue report

```python
report = (
    orders
    .assign(revenue=lambda d: d["units"] * d["price"])
    .merge(customers, on="customer", how="left")
    .groupby(["segment", "region"], as_index=False)
    .agg(total_revenue=("revenue", "sum"), orders=("order_id", "count"))
    .sort_values("total_revenue", ascending=False)
)
print(report)
```

Method chaining like this (assign → merge → groupby → sort) is the idiomatic pandas style you'll see in production code.

## Why LLM engineers care (concrete program hooks)

- **Week 4 Text2SQL**: you'll generate SQL for questions pandas can answer — knowing both sides makes you good at evaluating generated SQL
- **Week 6 tabular RAG**: tables must be cleaned, typed, and profiled before embedding
- **Week 12 phiData analytics agent**: the agent's toolkit is pandas operations
- **Week 16 evals**: evaluation datasets live in DataFrames; metrics are groupbys

## Exercises

1. Top 2 customers by total revenue, with their segment attached.
2. Revenue per region as a pivot table (regions as rows, products as columns, zeros filled).
3. Add a `high_value` boolean column (revenue > 50,000) and compute the share of high-value orders per region.
4. Build a `customers` table with one customer who has no orders; show how `inner` vs `left` join changes the result.
5. Load any CSV with `pd.read_csv(..., parse_dates=[...])`, profile it with `describe(include="all")` and `isna().sum()`, and write three sentences about data quality.

## Pitfalls

- **Chained indexing** `df[a][b] = x` — use `.loc` in one shot
- **`&`/`|` not `and`/`or`** between conditions, with parentheses
- **Join row-count explosion** — duplicate keys on both sides multiply rows; use `validate=`
- **dtype surprises** — IDs as ints vs strings block joins; check with `df.dtypes`
- **`groupby` silently dropping NaN keys** — pass `dropna=False` when it matters
- **Iterating row-by-row** (`iterrows`) — 100× slower than vectorized ops

## Resources

- pandas [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) and [User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [Modern Pandas](https://tomaugspurger.github.io/modern-01-intro) tutorial series (method chaining)
- `pd.options.mode.copy_on_write = True` — turns copy pitfalls into errors on modern pandas
