# 01 — RDBMS & SQL: Deep Dive

> Parent topic: [../01-rdbms-sql-fundamentals.md](../01-rdbms-sql-fundamentals.md) · Week 6 index: [../README.md](../README.md)

The relational foundation for the capstone's structured-data half — tables, keys, constraints, the SQL families, and the join patterns that Text2SQL (file 03) generates against.

**Key content from the parent topic:**

- **Relational modeling**: tables with typed columns, primary/foreign keys, CHECK constraints — integrity enforced by the database
- **SQL families**: DDL (CREATE/ALTER), DML (INSERT/UPDATE/DELETE), DQL (SELECT with joins/aggregation)
- **The capstone rule**: the LLM gets read-only DQL; writes go through validated application code
- **Joins**: INNER, LEFT (the zero-match tool), and the COALESCE pattern for null handling
- **Indices**: on filtered/joined columns; the cost is write time + space

The parameter-counting skill (W8-01) applies here: `layer_params(n_in, n_out)` becomes `index_size(columns, rows)` — the same arithmetic, different domain.

For the full implementation, the 8-query ladder, the pandas bridge, and the exercises, see the parent file.
