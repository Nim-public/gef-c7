# 03.1 — DataFrames From Zero

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

---

## What you'll learn

- Series and DataFrame internals (what the object actually is)
- Dtypes: the silent correctness killer
- Loading options that prevent 90% of ingestion bugs
- The first-look ritual and memory profiling

## 1. Series and DataFrame — what they are

```python
import pandas as pd
import numpy as np

s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="units")
print(s.index, s.dtype)          # Index(['a','b','c']), int64 — index + values + dtype

df = pd.DataFrame({
    "region": pd.Series(["south", "north"], dtype="string"),
    "units": pd.Series([2, 10], dtype="int64"),
})
print(df.dtypes)                  # every column has an explicit dtype
```

A DataFrame is a **dict of Series sharing an index** — every column operation is vectorized over that shared axis. The index is *not* row position; it's a label (W13-01's graph state lessons apply: immutable-ish, keyed access).

## 2. Dtypes — the silent correctness killer

```python
raw = pd.DataFrame({"id": ["001", "002"], "qty": ["5", "10"], "when": ["2026-01-05", "2026-01-06"]})
print(raw.dtypes)
# id      object      ← string-looking, fine — but "00123" preserved only as string
# qty     object      ← numbers as strings! comparisons sort alphabetically
# when    object      ← dates as strings; no date math

fixed = raw.astype({"id": "string", "qty": "int64", "when": "datetime64[ns]"})
```

The failure each dtype causes downstream:

| Wrong dtype | Failure |
|---|---|
| IDs as int | leading zeros lost; joins fail on type mismatch (W6) |
| dates as string | `"03/04"` vs `"3/4"` sorts wrong; no `resample` |
| numbers as object | `sum()` concatenates or errors |
| mixed types in one column | object dtype → slow, error-prone |

Load-time fix: `pd.read_csv(..., dtype={...}, parse_dates=[...], na_values=[...])` — set dtypes *at the door*, not after debugging.

## 3. Loading options that matter

```python
df = pd.read_csv(
    "data/orders.csv",
    sep=",", encoding="utf-8",
    dtype={"order_id": "string", "sku": "string"},
    parse_dates=["created_at"],
    na_values=["", "NA", "-", "null"],
    true_values=["yes"], false_values=["no"],
    nrows=None,                       # set during debugging
)
```

Also worth knowing: `pd.read_json(..., lines=True)` for JSONL (W1-04), `pd.read_sql` (W6), `parse_dates` + `dayfirst=True` for locale formats (W6-03's date lesson).

## 4. The first-look ritual (memorize it)

```python
def first_look(df: pd.DataFrame) -> None:
    print("shape:", df.shape)
    print(df.dtypes.to_string())
    print("nulls:\n", df.isna().sum()[df.isna().sum() > 0])
    print("dups:", df.duplicated().sum())
    print(df.describe(include="all").T[["count", "unique", "top", "freq"]].to_string())
```

Five prints that catch: wrong row counts (bad joins upstream), dtype surprises, null concentrations, duplicate keys, constant columns. Make it a reflex before any transformation.

## 5. Memory profiling (why dtypes matter at scale)

```python
df = pd.read_csv("big.csv")
print(df.memory_usage(deep=True).sum() / 1e6, "MB")

# the classic win: object strings → category
df["region"] = df["region"].astype("category")     # 10-50× smaller for low-cardinality
```

| Dtype | Bytes/row (typical) |
|---|---|
| float64 | 8 |
| int64 | 8 |
| object string | 50+ (pointer + heap) |
| category | 4–8 + dictionary |

Downcasting (`float64→float32`, `int64→int32`, object→category) cuts memory 2–10× — which is why W15-03's serving benchmarks and W4's indexes care about dtypes.

## Exercises

1. Load any CSV three ways (default dtypes / explicit dtypes / parse_dates) — diff the `df.dtypes` and find one downstream behavior change per dtype.
2. Build `first_look` and run it on 3 real-ish datasets; write 3 data-quality observations each.
3. Memory diet: downcast a 1M-row DataFrame's columns (category/int32/float32) — before/after memory table.
4. Deliberate dtype bug: sort a string-number column and an int column — show the different orderings.
5. Profile: `df.info(memory_usage="deep")` before and after object→category conversion on a 1M-row synthetic set.

## Pitfalls

- **`read_csv` type inference surprises** — mixed columns become object; pin with `dtype=`
- **NaN is float** — an int column with one NaN silently becomes float; use nullable dtypes (`Int64`)
- **Index assumptions** — after `concat`/`filter`, the index isn't 0..n; `reset_index(drop=True)` when position matters
- **`object` vs `string` dtype** — prefer `"string"` (pandas nullable string) for IDs/text keys
- **Deep-copy assumptions** — slices are views or copies depending on access pattern; `copy_on_write` mode (W1-05 parent's tip) makes the rules explicit

## Resources

- pandas [dtype basics](https://pandas.pydata.org/docs/user_guide/basics.html#dtypes) · [read_csv reference](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- W1-03 parent (joins/aggregation), W6-01 (SQL dtypes), W16-03 (loaders) — composed here
