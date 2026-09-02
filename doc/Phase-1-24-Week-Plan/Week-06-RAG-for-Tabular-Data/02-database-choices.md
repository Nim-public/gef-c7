# 02 — Database Choices

> Week 6 index: [README.md](README.md)

**Session 1 topic:** *Various Database choices — SQLite, MySQL examples.*

---

## What you'll learn

- The relational landscape (SQLite/MySQL/Postgres) mapped to workloads
- How the relational stack and the vector stack (LanceDB, Week 4) coexist — they're complements, not rivals
- The read-only safety pattern for LLM-generated SQL

## 1. The relational line-up

| | **SQLite** | **MySQL** | **PostgreSQL** |
|---|---|---|---|
| Model | embedded (file) | client/server | client/server |
| Setup | stdlib, zero install | install server + user | install server + user |
| Concurrency | single-writer | many | many (MVCC) |
| Scale | GBs, one machine | GBs–TBs, many apps | TBs, heavy analytics |
| Extensions | minimal | mature ecosystem | **pgvector**, JSONB, full-text |
| Used by | mobile apps, local tools, **your capstone** | web apps everywhere | modern default server DB |

Decision heuristics for this program:

- **Prototype / single-user / capstone** → SQLite: `capstone.db` is one file you can commit (carefully), back up, and email. No daemon, no credentials.
- **Multi-user web app, team database** → MySQL or Postgres. Same SQL you learned (with dialect differences: `LIMIT` vs `FETCH FIRST`, date functions, `AUTO_INCREMENT` vs `SERIAL`).
- **Anything "serious + Postgres-adjacent"** → Postgres: `pgvector` turns it into a hybrid relational+vector store (one `CREATE EXTENSION vector` — relevant when you want metadata filters and ANN in one engine; Week 9's multimodal stack revisits this idea with LanceDB).

Dialect reality check: ANSI SQL is the shared core (SELECT/joins/aggregates — file 01), but every engine accents it. When Text2SQL generates dialect-wrong syntax, the fix is **telling it the dialect in the prompt** (file 03).

## 2. Where the vector stack fits (coexistence map)

By now your capstone has two storage systems. Both, deliberately:

```
                  your capstone data plane
┌─────────────────────────────┬───────────────────────────────┐
│  Relational (SQLite/PG)     │  Vector (LanceDB / FAISS)     │
│  rows, keys, joins, SQL     │  chunk embeddings + metadata  │
│  transactions, updates      │  ANN search, filters          │
│  Text2SQL (file 03)         │  semantic search (W4/W5)      │
└─────────────────────────────┴───────────────────────────────┘
        ▲ cross-references by id: chunk.source_row = orders.id ▲
```

- Prose knowledge → vector side; structured records → relational side (file 04 covers the overlap cases like CSVs)
- Cross-referencing is the superpower: a retrieved chunk citing `source: orders#1001` lets the *structured* side fetch the live row

## 3. The read-only pattern (non-negotiable)

Generated SQL runs with the least power possible:

```python
# SQLite: open read-only at the connection level
conn = sqlite3.connect("file:capstone.db?mode=ro", uri=True)
conn.execute("DROP TABLE orders")     # sqlite3.OperationalError: attempt to write a readonly database
```

```sql
-- MySQL/Postgres: dedicated user
CREATE USER 'rag_reader'@'localhost' IDENTIFIED BY '<env-var-password>';
GRANT SELECT ON capstone.* TO 'rag_reader'@'localhost';
```

Plus two engineering rails around it (file 03 implements both): **statement allow-listing** (must start with `SELECT`; reject `;`-stacked statements) and **query timeout + row limits** (a cartesian-product `SELECT` on 10M rows is a denial-of-service against yourself).

## 4. Choosing, concretely, for the capstone

| Question | If yes |
|---|---|
| One user, laptop, ≤ a few GB? | SQLite (this week's default) |
| Need `pgvector` + server anyway? | Postgres |
| Team writes concurrently via web app? | MySQL/Postgres |
| Pure vector workload, no relations? | LanceDB alone (Week 4 was fine) |
| "Will this scale?" | Any of them at capstone scale; the *pattern* (schema + constraints + read-only LLM access) is what you're learning |

## Exercises

1. Port this week's schema to both SQLite and MySQL (`CREATE TABLE` differences: types, autoincrement, date defaults). Record the dialect diffs you hit.
2. Concurrency probe: two processes writing the same SQLite file — observe the lock behavior. What does this teach about SQLite's server-less design?
3. Stand up Postgres (or MySQL) in Docker (`docker run -e POSTGRES_PASSWORD=... postgres`), recreate your schema, connect via SQLAlchemy. Same queries, same results?
4. Create a read-only user in your server DB; try `DROP TABLE` as that user. Then try it through your Text2SQL prompt — does the DB error bubble up usefully?
5. Write the one-paragraph storage-decision section for your capstone README: what's relational, what's vector, what's both, and why.

## Pitfalls

- **Dialect drift between dev (SQLite) and prod (MySQL/PG)** — generated SQL that ran locally can fail on dates/casing; test generated SQL on the target engine
- **Committing DB files with real data to git** — SQLite files are binaries with everything in them; use fixtures/synthetic data
- **Assuming the vector DB replaces SQL** — filters/aggregations/joins are relational superpowers; vector search complements them (file 04 bridges)
- **One shared admin user for app + LLM** — blast radius; separate users, least privilege
- **Dialect in prompt vs dialect in docs** — the schema prompt (file 03) must name the engine explicitly

## Resources

- [SQLite docs](https://sqlite.org/whentouse.html) — *"SQLite is not a toy"* page, required reading
- PostgreSQL [tutorial](https://www.postgresql.org/docs/current/tutorial.html) · MySQL [getting started](https://dev.mysql.com/doc/mysql-getting-started/en/)
- [pgvector](https://github.com/pgvector/pgvector) — vector search inside Postgres
- SQLAlchemy [ORM/ Core basics](https://docs.sqlalchemy.org/en/20/tutorial/) — the portable-API layer
