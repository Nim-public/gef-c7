# 03 — Pandas: Deep Dive

> Parent topic: [../03-pandas-structured-data.md](../03-pandas-structured-data.md) · Week 1 index: [../../README.md](../../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-dataframes-from-zero.md](01-dataframes-from-zero.md) | Series/dtypes, loading, first-look ritual, memory | 3 h |
| 2 | [02-selection-and-indexing.md](02-selection-and-indexing.md) | loc/iloc/at, indexes, chained-indexing traps | 3 h |
| 3 | [03-filtering-and-vectorization.md](03-filtering-and-vectorization.md) | Masks, query, string/datetime accessors | 2 h |
| 4 | [04-aggregation-groupby.md](04-aggregation-groupby.md) | groupby mechanics, agg, pivot, windows | 3 h |
| 5 | [05-joins-and-combining.md](05-joins-and-combining.md) | merge kinds, validate, concat, sanity checks | 3 h |
| — | [exercises.md](exercises.md) | Expanded labs + mini-project | 4 h |

## File map

- **01** — Series vs DataFrame, dtypes (the silent killer), loading options, the first-look ritual, memory profiling
- **02** — label vs position indexing, `.loc/.iloc/.at`, MultiIndex, setting values correctly, copy-on-write
- **03** — boolean masks composed with `&|~`, `query()`, `isin/between/str`, datetime filtering
- **04** — how groupby actually works (split-apply-combine), named aggregation, pivots, rolling windows
- **05** — all four join kinds on the same data, `validate=`, indicators, concat axis semantics, join sanity checks
- **exercises.md** — labs with worked approaches + the revenue-report mini-project
