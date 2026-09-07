# 03.2 — Selection & Indexing

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

---

## What you'll learn

- `.loc` vs `.iloc` vs `.at` — the three accessors and their contracts
- Setting values correctly (the chained-indexing trap, demonstrated)
- MultiIndex for hierarchical data
- Copy-on-write: the modern rules

## 1. The three accessors

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}, index=["x", "y", "z"])

df.loc["y"]              # by LABEL (index/columns names)
df.iloc[1]               # by POSITION (0-based)
df.at["y", "a"]          # single scalar by label — fastest
df.iat[1, 0]             # single scalar by position
```

| Accessor | Takes | Returns | Speed |
|---|---|---|---|
| `.loc` | labels, boolean arrays, slices (inclusive!) | anything | fast |
| `.iloc` | integer positions, slices (exclusive end) | anything | fast |
| `.at`/`.iat` | single label/position | scalar | fastest |

The slice gotcha: `df.loc["x":"y"]` is **inclusive** of `"y"` (label slices include the endpoint); `df.iloc[0:1]` is exclusive. Position vs label — the source of most selection bugs.

## 2. Setting values — the right way

```python
# WRONG (chained indexing): may write a temporary copy
df[df["a"] > 1]["a"] = 99          # SettingWithCopyWarning, value often NOT set

# RIGHT: one .loc shot with both dimensions
df.loc[df["a"] > 1, "a"] = 99
```

Chained indexing triggers `SettingWithCopyWarning` because pandas can't prove you're writing the original object. The `.loc[row_mask, col] = value` form is unambiguous — one call, one object, guaranteed write.

With copy-on-write (pandas ≥ 2.0 default direction), chained writes raise or silently no-op — the rules got stricter, so learn the correct form once:

```python
pd.options.mode.copy_on_write = True     # opt in explicitly in 2.x; default in 3.x
```

## 3. SettingWithCopy, demonstrated

```python
sub = df[df["a"] > 1]        # a VIEW or copy — pandas decides
sub["a"] = 0                 # warning: may not propagate to df
# fix: sub = df[df["a"] > 1].copy()  — be explicit, then modify freely
```

Rule: **explicit `.copy()` when you intend an independent frame**; otherwise write through `.loc` on the original.

## 4. The index — labels you can rely on

```python
df = df.set_index("order_id")        # label-based rows
df.loc[1001]                          # the order row
df = df.reset_index()                 # back to RangeIndex; old index becomes a column

df2 = df.set_index(["region", "product"])   # MultiIndex
df2.loc[("south", "GPU")]                    # hierarchical access
```

- Index enables O(1) label lookup (`df.loc[key]`) — the pandas analog of a dict
- After filtering, the index keeps *original* labels — `iloc` positions and labels diverge; know which you're using
- Sorted index → `df.loc["a":"m"]` range queries are fast; `sort_index()` first

## 5. MultiIndex (hierarchical selection)

```python
mi = df.set_index(["region", "product"]).sort_index()
mi.loc[("south", "GPU")]                    # exact
mi.loc["south"]                             # whole region group
mi.xs("GPU", level="product")               # cross-section by level
```

MultiIndex is how pivot results come back — being able to select by level is required for W6-04's pivots and E8-03's grouped ledgers.

## Exercises

1. Selection tournament: given a 1M-row frame, time `df.loc[mask, col].sum()` vs `df.query(...)` vs `df[mask][col].sum()` — one table, one conclusion.
2. SettingWithCopy drill: reproduce the warning with chained indexing; fix three ways (`.loc` one-shot, explicit `.copy()`, copy-on-write mode) — verify identical results.
3. MultiIndex navigation: build a 3-level index (region/product/month); practice `.loc` tuples, `.xs`, and partial indexing; note which operations require a sorted index.
4. Index-reset bug hunt: filter a frame, then `.iloc[0]` — show the position/label mismatch; fix with `reset_index`.
5. `at` vs `loc` scalar benchmark on 100k single-cell writes — when is `at` worth it?

## Pitfalls

- **`loc` slices are inclusive, `iloc` exclusive** — off-by-one selection with no error
- **Writing via chained indexing** — the classic silent no-op; `.loc` one-shot only
- **Boolean mask length mismatch** — pandas raises, but only if lengths differ *exactly*; index-aligned masks are the rule
- **Labels ≠ positions after filtering** — `df.iloc[0]` is not "the first row I inserted"
- **Sorting assumptions** — `loc` range slices require a sorted index, else they raise or misbehave

## Resources

- pandas [indexing and selecting](https://pandas.pydata.org/docs/user_guide/indexing.html) — the definitive reference
- [copy-on-write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html) — modern ownership rules
- W1-03 parent, W6-01 (SQL's WHERE/LIMIT analogies) — composed here
