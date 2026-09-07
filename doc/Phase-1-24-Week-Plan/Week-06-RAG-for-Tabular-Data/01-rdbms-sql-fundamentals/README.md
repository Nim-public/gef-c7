# Deep-Dive: RDBMS & SQL Fundamentals

Parent overview: [`../01-rdbms-sql-fundamentals.md`](../01-rdbms-sql-fundamentals.md)

The relational foundation, deepened: entity modeling with justified
constraints, the three SQL families, joins with zero-match behavior,
the 8-query aggregation ladder, and the pandas↔SQL bridge — the SQL
skills the Text2SQL agent (Week 06 file 03) will rely on.

## File map

| File | What it covers |
|---|---|
| [`01-relational-modeling.md`](01-relational-modeling.md) | Tables, keys, constraints justified |
| [`02-sql-families.md`](02-sql-families.md) | DDL/DML/DQL, the read-only rule |
| [`03-joins-and-coalesce.md`](03-joins-and-coalesce.md) | Inner/left, zero-match, COALESCE |
| [`04-aggregation-ladder.md`](04-aggregation-ladder.md) | GROUP BY → CTEs, 8-query ladder |
| [`05-pandas-sql-bridge.md`](05-pandas-sql-bridge.md) | read_sql/to_sql, dtype traps |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-relational-modeling.md` — design the warehouse deliberately.
2. `02-sql-families.md` — DDL/DML yours, DQL the agent's.
3. `03-joins-and-coalesce.md` — joins that count correctly.
4. `04-aggregation-ladder.md` — climb to CTEs.
5. `05-pandas-sql-bridge.md` — cross the worlds safely.

## Prerequisites

- Week 02 (Python environments) — `py`, venv, pandas installed.