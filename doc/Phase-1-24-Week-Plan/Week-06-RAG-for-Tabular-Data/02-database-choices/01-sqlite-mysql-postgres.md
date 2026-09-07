# SQLite vs MySQL vs Postgres — Decision Heuristics and Dialect Diffs

**What you'll learn:** the three relational engines compared on the axes
that matter for the capstone: setup, concurrency, dialect differences,
and the decision heuristics that pick between them.

## 1. The comparison table

| Axis | SQLite | MySQL | PostgreSQL |
|---|---|---|---|
| setup | zero (stdlib) | server install | server install |
| storage | one file | server daemon | server daemon |
| concurrency | single writer | multi-user | multi-user, MVCC |
| types | flexible (type affinity) | strict-ish | strict, rich (JSONB, arrays) |
| full-text | FTS5 built-in | MATCH…AGAINST | tsvector/tsquery |
| extensions | none needed | plugins | PostGIS, pgvector |
| agent fit | the capstone default | web-app legacy | analytics-heavy scale |

| Heuristic | Pick |
|---|---|
| single-process demo, zero ops | SQLite |
| existing web stack (LAMP) | MySQL |
| analytics, JSONB, pgvector, scale | PostgreSQL |

SQLite's zero-install property is why it is the capstone default: the
entire warehouse is one file in `data/`, version-controllable in its
schema, and the stdlib driver needs no server.

## 2. The dialect diffs that bite Text2SQL

| Feature | SQLite | MySQL | PostgreSQL |
|---|---|---|---|
| current date | `date('now')` | `CURDATE()` | `CURRENT_DATE` |
| string concat | `\|\|` | `CONCAT()` | `\|\|` or `CONCAT` |
| case-insensitive LIKE | LIKE (ASCII) | LIKE (collation) | ILIKE |
| limit | `LIMIT n` | `LIMIT n` | `LIMIT n` |
| month from date | `substr(d,1,7)` / `strftime('%Y-%m',d)` | `DATE_FORMAT(d,'%Y-%m')` | `to_char(d,'YYYY-MM')` |
| auto-increment | `INTEGER PRIMARY KEY` | `AUTO_INCREMENT` | `SERIAL`/`IDENTITY` |

The month-extraction row is the Text2SQL trap: the model mixes
dialects (`DATE_FORMAT` on SQLite) and the query errors. The schema
prompt states the dialect explicitly — "SQLite dialect: use
`strftime('%Y-%m', col)` for months" — and the repair loop (file 03)
catches the rest.

## 3. The dialect test (the schema prompt's evidence)

```python
DIALECT_PROBES = [
    "SELECT date('now')",                        # sqlite
    "SELECT substr('2025-06-15', 1, 7)",         # sqlite
    "SELECT DATE_FORMAT('2025-06-15', '%Y-%m')", # mysql — fails on sqlite
]

def dialect_probe(sql: str, conn) -> tuple[bool, str]:
    try:
        conn.execute(sql).fetchall()
        return True, "ok"
    except Exception as e:
        return False, str(e)
```

The probes run at connection setup — the agent's tool *knows* which
dialect it serves, and the schema prompt is generated from the probes'
results rather than assumed.

## 4. The dialect drill record (the probes' evidence)

```text
probe 1: date('now')            → ok (SQLite)
probe 2: substr('2025-06-15',1,7) → '2025-06' (SQLite)
probe 3: DATE_FORMAT(...)       → OperationalError: no such function
conclusion: MySQL dialect constructs fail loudly; the schema prompt
states the SQLite dialect and the repair loop teaches the substitution
```

The drill record is the dialect table's evidence — the probes run, the
failures captured, the conclusion drawn. It is the schema prompt's
dialect section, verified rather than assumed.

## 5. The engine pin note (the choice's record)

```markdown
# Warehouse engine (W06)
- choice: SQLite (stdlib driver, file: data/warehouse.db)
- dialect: SQLite — strftime for dates, || for concat, LIMIT
- rationale: zero-ops single-process demo; FKs + CHECKs enforced;
  FTS5 available if keyword search needs it
- dialect probes: live-tested (MySQL DATE_FORMAT fails, strftime works)
- revisit: multi-user concurrent writes → Postgres
```

The pin note is the engine decision's record — choice, dialect,
rationale, probes, and the revisit trigger. The same memo discipline as
every decision since W10.

## Exercises

1. Run the dialect probes against SQLite; record which MySQL/Postgres
   constructs fail — the diff table, verified live.
2. Port drill: rewrite Q2 (monthly revenue) in MySQL and Postgres
   dialects; the three versions side-by-side in your notes.
3. Heuristic drill: for three hypothetical deployments (single-user
   demo, LAMP web app, analytics platform), pick the engine and justify
   from §1's table.
4. Pin drill: write the note; the probes committed beside it.
5. Record drill: fill §4; the failing probe's exact error message
   recorded — it becomes a repair-loop test case.