# 03.3 — Filtering & Vectorization

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

---

## What you'll learn

- Boolean-mask composition with `& | ~` (and why `and`/`or` fail)
- `.query()`, `isin`, `between`, string and datetime accessors
- Vectorized conditional logic: `np.where`, `np.select`, `.map`, `.apply` (and when apply is justified)
- Datetime filtering patterns

## 1. Boolean masks — the composition rules

```python
import pandas as pd, numpy as np

df = pd.DataFrame({
    "region": ["south", "north", "south", "east"],
    "units": [2, 10, 1, 4],
    "price": [45000.0, 5500.0, 45000.0, 45000.0],
})

m = (df["region"] == "south") & (df["units"] > 1)      # & | ~ — element-wise
df[m]
df[~df["region"].isin(["east"])]                        # negation via ~
```

**Why `and` fails:** `and` calls `bool()` on the whole Series — ambiguous truth value. `&` applies element-wise. Always parenthesize: `&` binds tighter than comparison operators.

## 2. `.query()` and accessor filtering

```python
df.query("region == 'south' and units > 1")             # readable, uses numexpr when installed
df.query("region in @allowed_regions")                  # local variables via @
df[df["region"].str.startswith("s", na=False)]          # string accessor — na=False for nulls
df[df["units"].between(1, 5)]
```

String accessor traps: `.str.contains("refund")` on a column with `NaN` raises unless `na=False`; case-insensitivity via `case=False`; regex via `regex=True` (default).

## 3. Datetime filtering

```python
df["created_at"] = pd.to_datetime(df["created_at"])
df[df["created_at"].dt.to_period("M") == "2026-11"]     # whole month
df[df["created_at"].dt.date == pd.Timestamp("2026-11-05").date()]
df.set_index("created_at").loc["2026-11"]               # partial-string indexing on DatetimeIndex
```

Partial-string indexing (`loc["2026-11"]`) is the clean way to select date ranges — one of the few places label slicing shines (W13-03 file 03's date lesson at pandas level).

## 4. Conditional logic — vectorized

```python
# simple binary
df["high_value"] = np.where(df["revenue"] > 50000, "high", "standard")

# multiple cases — np.select (ordered, first match wins)
conditions = [df["revenue"] > 100000, df["revenue"] > 50000]
df["band"] = np.select(conditions, ["enterprise", "mid"], default="small")

# pandas-native
df["band"] = pd.cut(df["revenue"], bins=[0, 50000, 100000, np.inf],
                    labels=["small", "mid", "enterprise"])

# row-wise function — LAST resort
df.apply(lambda r: classify(r), axis=1)                 # 100× slower; avoid in hot paths
```

`np.select` is the multi-case workhorse; `.apply(axis=1)` is the performance smell — if you must, `.map` on Series or vectorize via masks.

## 5. Vectorization vs loops — the measurement

```python
def with_apply(df):
    return df.apply(lambda r: r["units"] * r["price"], axis=1)

def vectorized(df):
    return df["units"] * df["price"]

# %timeit both on 1M rows: vectorized ~1ms, apply ~10s — 1000×
```

Exercises 2 and 5 make you measure this — the lesson sticks only with a stopwatch.

## Exercises

1. Filter builder: given a dict of constraints ({"region": [...], "min_units": 3}), build the mask programmatically — compose any subset of conditions.
2. `.query()` vs masks: translate 5 mask filters to `.query()`; verify identical results; note where `@variables` help readability.
3. String-filter trap: `.str.contains("GPU")` on a column with NaN — reproduce the TypeError; fix with `na=False`; then discuss whether NaN should match.
4. Datetime drill: build a 2-year daily frame; filter "last business week", "this quarter", "same month last year" — each with one line.
5. `.apply` refactor: take a 20-line `axis=1` function (string ops + math) and vectorize it with `np.select` + `.str` — benchmark before/after on 1M rows.

## Pitfalls

- **`and`/`or` between Series** — ValueError; `&`/`|` with parentheses, always
- **`.str` on mixed dtypes** — non-string entries raise; `.astype("string")` first or `na=False`
- **NaN comparisons** — `df["x"] > 5` excludes NaN silently; decide and handle explicitly
- **Chained assignment after filtering** — W3-02's rule: write via `.loc` in one shot
- **`apply(axis=1)` in loops of loops** — compound slowness; vectorize the inner logic first

## Resources

- pandas [indexing basics](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-operators)
- [np.select](https://numpy.org/doc/stable/reference/generated/numpy.select.html) — multi-case vectorization
- W1-03 parent, W3-03 file 03 (dtypes), W6-01 (SQL WHERE analogies) — composed here
