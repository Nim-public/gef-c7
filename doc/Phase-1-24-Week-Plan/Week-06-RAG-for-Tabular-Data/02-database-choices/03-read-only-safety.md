# Read-Only Safety — Users, Modes, Allow-Lists

**What you'll learn:** the read-only pattern in depth: SQLite's URI
modes, the validator layer, and the defense stack that makes the
agent's SQL tool structurally unable to write.

## 1. The connection-level wall

```python
# SQLite: open read-only at the connection level
conn = sqlite3.connect("file:data/warehouse.db?mode=ro", uri=True)
conn.execute("INSERT INTO products VALUES (99, 'x', 1.0)")   # → error
# sqlite3.OperationalError: attempt to write a readonly database
```

The `mode=ro` URI is the strongest wall: even a validator bug or an
injection that slips every pattern *cannot* write — the database file
itself refuses. The agent's tool opens its connection read-only; your
ingestion scripts open read-write separately.

## 2. The layered defenses (wall, validator, allow-list)

| Layer | Mechanism | Blocks |
|---|---|---|
| connection `mode=ro` | SQLite refuses writes at the file level | everything, structurally |
| SQL validator (W12 file 02-04) | SELECT-only, LIMIT, allow-listed tables | injection shapes |
| table allow-list | only warehouse tables reachable | attached foreign DBs |
| user separation (Postgres/MySQL) | a `readonly` DB user | privilege escalation at the server |

On Postgres/MySQL the equivalent wall is a read-only database user:
`GRANT SELECT ON warehouse.* TO agent_ro`. The pattern generalizes: the
agent's credentials are the narrowest that serve its queries.

## 3. The wall's test (prove it structurally)

```python
def test_connection_is_readonly():
    conn = sqlite3.connect("file:data/warehouse.db?mode=ro", uri=True)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        conn.execute("DELETE FROM orders")
```

| Probe | Expected |
|---|---|
| DELETE via ro connection | OperationalError |
| PRAGMA writable_schema hack | refused |
| ATTACH a writable db then write | the ATTACH itself is blocked (ro mode) |

The test suite is the structural proof: the wall holds against the
validator's blind spots because it operates below SQL — at the storage
layer. The W15 defense-stack table cites this as the layer that
"cannot be prompted away".

## 5. The read-only pin note (the wall's record)

```markdown
# SQL read-only safety (W06)
- connection: file:...?mode=ro (structural wall — tested)
- validator: SELECT-only, LIMIT, allow-list (W12-02-04, imported)
- user separation: Postgres/MySQL → agent_ro with SELECT grants
- tests: 3 write probes refused, validator-independence drill green
```

The pin note is the wall's record — the connection mode, the validator,
the user separation, and the tests. It is the containment row of the
W15 defense-stack table, SQL edition.

## 6. The read-only drill record (the wall's proof)

```text
probe 1: INSERT INTO products ... → OperationalError: readonly ✓
probe 2: DELETE FROM orders ...   → OperationalError: readonly ✓
probe 3: PRAGMA journal_mode=WAL  → refused in ro mode ✓
probe 4: ATTACH 'rw.db' + write   → ATTACH blocked / write refused ✓
validator disabled: probes STILL refused (independence proven)
```

The drill record is the structural wall's evidence — every write probe
refused *with the validator disabled*, proving the wall operates below
SQL. This is the containment layer that cannot be prompted away.

## Exercises

1. Open the warehouse read-only; attempt INSERT, DELETE, and
   `PRAGMA journal_mode=WAL`; all refused — the wall, demonstrated.
2. Layer drill: disable the SQL validator; the ro connection still
   blocks writes — the layers' independence, proven.
3. Port drill: on Postgres (if available), create an `agent_ro` user
   with SELECT-only; attempt a write; the server refuses.
4. Pin drill: write the note; the wall tests in CI cited.
5. Record drill: fill §6 from the probes; the validator-disabled run
   documented.

## 7. The wall vs the validator (the division of labor)

| Concern | Wall (ro-mode) | Validator (SQL rules) |
|---|---|---|
| write statements | blocks all, structurally | blocks by pattern |
| ATTACH/PRAGMA | blocks at connection | blocks by keyword |
| full-table scans | allows (reads are safe) | blocks via LIMIT |
| resource exhaustion | allows | partially (row caps) |

The division: the wall is absolute but blunt; the validator is nuanced
but bypassable. Together they cover each other's gaps — the defense
stack's layering principle (W15 file 03-03) applied at the database.