# Week 6 — RAG for Tabular Data: Study Guide

> Full schedule: [../README.md](../../README.md)

**Sessions:** Sat 10 Oct, 7–10 PM IST (Session 1) · Sun 11 Oct, 7–10 PM IST (Session 2) · Office Hours Thu 15 Oct, 7–8 PM IST

**Weekly task:** [05-capstone-task-structured-retrieval.md](05-capstone-task-structured-retrieval.md)

---

## Why this week matters

Half the world's enterprise knowledge isn't prose — it's rows. "What were Q2 sales by region?" can't be answered by embedding a table into prose chunks: numbers, comparisons, and aggregations need a different retrieval brain. This week adds the *second retrieval mode* to your capstone: relational databases with SQL and Text2SQL, so Week 13's analytics agents and the final capstone can answer questions over both documents *and* data.

## What you will be able to do after this week

- [ ] Model data relationally: tables, types, primary/foreign keys, constraints
- [ ] Write DDL (create/alter), DML (insert/update/delete), and query SQL with joins, aggregation, and ordering
- [ ] Choose a database (SQLite/MySQL/Postgres) for a given workload — and run one locally
- [ ] Build a Text2SQL pipeline: question → SQL → execute → format → grounded answer
- [ ] Retrieve over CSV/JSON with hybrid techniques; know when *not* to embed a table
- [ ] Combine document-RAG and structured-RAG in one query flow

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-rdbms-sql-fundamentals.md](01-rdbms-sql-fundamentals.md) | Tables, keys, constraints, DDL/DML/queries, joins | 3–4 h |
| 2 | [02-database-choices.md](02-database-choices.md) | SQLite vs MySQL vs Postgres vs the vector stack | 1–2 h |
| 3 | [03-rag-over-structured-data.md](03-rag-over-structured-data.md) | Text2SQL, schema prompting, result formatting, pipeline | 3–4 h |
| 4 | [04-csv-json-hybrid-retrieval.md](04-csv-json-hybrid-retrieval.md) | Hybrid retrieval over structured data; CSV/JSON handling | 2–3 h |
| 5 | [05-capstone-task-structured-retrieval.md](05-capstone-task-structured-retrieval.md) | Add structured retrieval to the capstone (task) | 4 h |

## Environment setup

```powershell
pip install pandas sqlalchemy       # SQLAlchemy = one API over SQLite/MySQL/Postgres
# SQLite is in Python's stdlib — nothing else needed for this week
```

## Self-check before Week 7

1. A user asks "top 3 customers by revenue this year". Write the SQL, then the Text2SQL prompt (schema included) that would generate it.
2. Your Text2SQL returned `SELECT * FROM orders`. What three prompt additions stop that class of error?
3. When is a table better as *summaries + full-table-on-demand* than as embedded row chunks?
4. Which join type preserves customers with zero orders — and why does that matter for "customers who never ordered" questions?
5. Where does structured retrieval *end* and Week 10's agents *begin*? (What would the agent add?)
