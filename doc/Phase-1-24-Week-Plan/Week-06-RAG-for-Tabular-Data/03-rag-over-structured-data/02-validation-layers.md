# Validation Layers — Allow-Lists, Read-Only, Row Caps

**What you'll learn:** the validation stack between the LLM and the
database: statement allow-listing, structural parsing, read-only
connections, and row caps — defense in depth so no single check is
load-bearing.

## 1. The validation stack

```python
def validate_and_execute(sql: str, conn, max_rows: int = 100) -> list[dict]:
    # layer 1: statement allow-list
    if (err := validate_dql(sql)):            # from file 01-02 §5
        raise ToolError(err)
    # layer 2: structural parse (sqlglot or ast-style)
    statements = split_statements(sql)
    if len(statements) != 1:
        raise ToolError("exactly one statement allowed")
    # layer 3: read-only connection (structural)
    rows = conn.execute(statements[0]).fetchmany(max_rows + 1)
    # layer 4: row cap
    if len(rows) > max_rows:
        rows = rows[:max_rows]
    return [dict(r) for r in rows]
```

| Layer | Blocks | Independently |
|---|---|---|
| 1. allow-list | non-SELECT, missing LIMIT | yes (string rules) |
| 2. structural parse | multi-statement, comment tricks | yes |
| 3. read-only conn | ANY write, even validator-blind | yes (file mode) |
| 4. row cap | context stuffing | yes |

Layer 3 is the guarantee: even if layers 1–2 are bypassed, the
connection cannot write. The layers' independence is proven by the
drill (file 02-03): disable any one, the others still hold.

## 2. The comment/multi-statement tricks (the parser's job)

```sql
SELECT 1; DROP TABLE orders;          -- multi-statement
SELECT * FROM orders -- LIMIT 100
/* hidden */ ; DELETE FROM products   -- comment-hiding
SELECT * FROM orders LIMIT 100; -- ok
```

| Trick | Layer that catches it |
|---|---|
| `; DROP TABLE` | layer 2 (statement count) + layer 3 (ro mode) |
| comment swallowing the LIMIT | layer 1 (LIMIT missing) |
| `/* */` hiding a second statement | layer 2 |

The parse layer (sqlglot or a split on unquoted `;`) is what makes the
string rules reliable — regexes alone miss the comment tricks.

## 3. The row cap and its contract

| Cap | Effect | User-visible |
|---|---|---|
| `max_rows = 100` | fetchmany(101) detects overflow | "showing first 100 of 1,204 rows" |
| column cap | wide results truncated per column | "12 of 30 columns shown" |

The cap is honest: the answer *states* the truncation rather than
silently showing partial data — the same principle as the observation
formatting (W10 file 05-02).

## 5. The validation pin note (the stack's manifest)

```markdown
# SQL validation stack (W06)
- L1 allow-list: SELECT-only + FORBIDDEN keywords + LIMIT
- L2 structural parse: single statement, sqlglot or split
- L3 read-only connection: file:...?mode=ro (structural)
- L4 row cap: 100 rows, honest truncation message
- independence drill: any layer disabled → others still hold
```

The pin note is the stack's manifest — four layers, four independent
mechanisms. The independence drill is the stack's proof: any single
layer can fail without the write path opening.

## Exercises

1. Implement the four-layer stack; run the trick battery (multi-
   statement, comment-hiding, LIMIT-swallowing); every one caught.
2. Independence drill: disable layer 1; layers 2–3 still block the
   write probes — the depth property, proven.
3. Cap drill: query a 1,204-row result; verify the honest truncation
   message and the exact row count stated.
4. Pin drill: write the note; the drill results cited.

## 6. The validator's error messages (the hints, SQL edition)

| Rejection | Message |
|---|---|
| non-SELECT | "blocked: only SELECT statements are allowed — this tool reads data" |
| missing LIMIT | "blocked: add a LIMIT clause (max 100) — large results should be aggregated" |
| unknown table | "blocked: table 'x' not in the allow-list. Tables: orders, products, customers, order_items" |
| multi-statement | "blocked: exactly one statement per call" |

The messages follow the W10 file 05-04 phrasing rules — constraint,
shape, next action. Each message names the *valid* alternative, which
is what the repair loop (file 03) feeds back to the model.

## Exercises (continued)

5. Message drill: for each rejection type, verify the hint names the
   valid alternative — the phrasing rules, checked.