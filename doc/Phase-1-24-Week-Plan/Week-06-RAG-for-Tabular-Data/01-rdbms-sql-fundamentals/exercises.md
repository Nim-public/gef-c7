# Exercises — RDBMS & SQL Fundamentals

Expanded set with worked approaches. Run from the repo root; the corpus
is seeded (file 01 §3) into `data/warehouse.db`.

## 1. Relational modeling (from 01-relational-modeling)

**Task:** write the DDL for a `refunds` table (order reference, amount
CHECK > 0, reason TEXT); insert 5 seeded refunds; attempt the violations.

**Worked approach:** the refunds table exercises FK + CHECK + the
composite-key decision (one refund per order-item, or many?). Justify
in one comment line per constraint.

**Pass criterion:** 5 refunds inserted; each violation attempt raises
the expected SQLite error; the error messages recorded (file 03's
repair-loop vocabulary).

## 2. The three families (from 02-sql-families)

**Task:** DML drill — attempt an unguarded `UPDATE products SET
unit_price = 0` on a scratch copy; observe table-wide damage; then write
the guarded version.

**Worked approach:** copy `data/warehouse.db` to `data/scratch.db`
first; the damage is the lesson. The guarded version uses WHERE + a
transaction.

**Pass criterion:** the damage observed and documented; the guarded
update touches exactly one row.

## 3. Joins (from 03-joins-and-coalesce)

**Task:** build both join queries; verify INNER drops the empty order
and LEFT keeps it with NULLs; the count-trap drill; the COALESCE
rewrite.

**Worked approach:** insert one item-less order deliberately; the two
queries' row counts differ by exactly the empty-order count. COUNT(*)
vs COUNT(col) explained in one sentence.

**Pass criterion:** both behaviors demonstrated; the COALESCE pattern
produces 0/unknown instead of NULL.

## 4. The 8-query ladder (from 04-aggregation-ladder)

**Task:** climb Q1–Q8 without help; self-score against the gold SQL;
the WHERE-vs-HAVING drill on "products with more than 10 units".

**Worked approach:** the ladder is the Text2SQL eval's blueprint —
self-scoring now shows which shapes the agent will be asked to
generate later. The two interpretations of Q4's phrasing differ in row
sets; run both.

**Pass criterion:** 8/8 queries correct (or the diff understood); the
WHERE/HAVING pair demonstrated.

## 5. The bridge (from 05-pandas-sql-bridge)

**Task:** read the order-items join into pandas; compute monthly revenue
in pandas; verify equality with SQL's GROUP BY result to the cent; the
loading drill (staging + promote).

**Worked approach:** the pandas-vs-SQL equality check is the bridge's
acceptance test — two computation paths, one number. The loading drill
proves constraints hold across the bridge.

**Pass criterion:** pandas total == SQL total; the staged load rejected
anything violating CHECKs.

## 6. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| DDL with justified constraints | refunds table + drill | 3 |
| DML damage observed, guarded fix | scratch-db drill | 3 |
| Joins: zero-match + count trap | query outputs | 3 |
| Ladder: 8/8 or understood diffs | self-score | 4 |
| Bridge: pandas==SQL to the cent | verification | 3 |

**Pass bar:** 13/16 to proceed to file 02 (database choices). The ladder
(4-pointer) is the subfolder's capstone — these 8 shapes are the Text2SQL
eval's gold set.