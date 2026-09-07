# Exercises — Pandas

> Subfolder index: [README.md](README.md) · Parent: [../03-pandas-structured-data.md](../03-pandas-structured-data.md)

Shared fixture for all labs: a synthetic orders dataset (100k rows × 12 columns, with realistic dirt — mixed dtypes, 2% NaNs, 1% duplicate keys, three regions, five products, 18 months of dates). Build it once with a seeded generator (W16-02 discipline) so results are reproducible.

---

## E1 — Ingestion forensics (files 01/02)

1. Load the fixture CSV three ways: default dtypes, explicit `dtype=`/`parse_dates=`, and `convert_dtypes()`. Diff the resulting `dtypes` and memory usage (deep).
2. Write `first_look` (file 01 §4) and run it — produce a one-page data-quality report: shape, dtypes, nulls, dupes, constant columns.
3. Downcast diet: convert to category/int32/float32 where valid — report the memory before/after and any precision loss (check a `sum` on downcast floats vs originals).

**Worked approach:** the dtype table from file 01 §2 is the checklist; the memory table is the proof.

## E2 — Selection drills (file 02)

1. Answer 10 questions using ONLY `.loc` (label-based): e.g., "revenue for order 50023", "all south-region rows", "the cell at row 'x', column 'b'".
2. Redo all 10 with `.iloc` — where did you need to convert labels to positions? (`get_indexer`.)
3. SettingWithCopy reproduction: chained write on a filtered frame; show the warning and the silent failure; fix three ways.

**Worked approach:** keep a "labels vs positions" note per operation — the mixed-up pair is the most common pandas bug you'll ever fix.

## E3 — Filtering and conditional logic (file 03)

1. Build 8 filters of increasing complexity (multi-condition, string contains with NaN handling, datetime ranges, isin across two columns).
2. Translate all 8 to `.query()`; verify identical output rows.
3. Vectorize a 15-line `axis=1` classifier into `np.select` + `.str` chains — benchmark on 1M rows and report the speedup.

**Worked approach:** the NaN trap appears in exercise 3 — decide explicitly whether missing values match each filter, and test it.

## E4 — Aggregation mastery (file 04)

1. Named-aggregation report: per region × product — total revenue, order count, avg units, max single order. One groupby, no MultiIndex in the output.
2. `transform` workout: add share-of-region and z-score-of-units columns — verify the per-group sums of shares equal 1.
3. Resample drill: DatetimeIndex → daily/weekly/monthly revenue + 7-day rolling mean — plot all three on one chart (W1-04 output discipline).
4. Pivot round-trip: wide pivot → `melt` back — prove losslessness (or find and explain the loss with duplicate pairs).

**Worked approach:** exercise 2's `transform` pattern (share-of-total) is the single most reused groupby idiom in analytics agents (W12-04).

## E5 — Join gauntlet (file 05)

1. Join orders ← customers under all four `how=` values; predict then verify row counts using key cardinalities.
2. `validate=` drill: add a duplicate key on one side — show `many_to_one` raising; fix by deduping and re-validate.
3. `merge_asof` lab: match 1,000 events to the latest price at-or-before each event timestamp; hand-verify 5 matches.
4. Anti-join: customers with zero orders — implement via `indicator=True` and via a NOT-EXISTS-style filter; compare.
5. Multi-key + suffix join: sales vs targets on (region, product, month) — handle the overlapping `target` column name explicitly.

**Worked approach:** exercise 1's row-count oracle turns every later join from hope into verification — keep the oracle function in your utils.

## E6 — Mini-project: the revenue report (parent §5, expanded)

Build the full chained report (assign → merge → groupby → sort) plus:

- a `first_look`-style quality report on the inputs
- three named checks: join row-count oracle, null-share per output group, revenue reconciliation (sum of groups == grand total)
- a markdown export of the report table (W1-04 output discipline)

**Exit artifact:** one function `build_report(orders, customers) -> (report_df, quality_report)` that a reviewer can run blind and trust.

## Self-assessment

- Can you predict a join's output row count from key cardinalities before running it?
- Can you explain why `transform` exists — with an example `agg` cannot express?
- Can you load any unknown CSV and produce a data-quality report in under 10 minutes?
