# Row Serialization — Row-Major Text, Summary Chunks

**What you'll learn:** turning table rows into retrievable text: row-
major serialization (one chunk per row), summary-major chunks (the
table's shape), and the metadata round-trip that lets retrieved rows
link back to the SQL path.

## 1. Row-major serialization

```python
def serialize_row(row: dict, columns: list[str]) -> str:
    parts = [f"{col}: {row.get(col, '')}" for col in columns]
    return " | ".join(parts)

# "sku: SKU-007 | unit_price: 16.9 | category: general"
```

| Rule | Why |
|---|---|
| field names in the text | "16.9" alone is meaningless to the embedder |
| consistent separator | parseable back if needed |
| every column present (even empty) | uniform chunk shapes |
| unit_id in metadata | the citation round-trip |

The serialized row is a *sentence about one entity* — the embedder's
input. The field names give the numbers semantics; without them,
"16.9" embeds like any other float.

## 2. Summary-major chunks (the table's shape)

```python
def summarize_table(df) -> str:
    return (
        f"Table with {len(df)} rows. Columns: {', '.join(df.columns)}. "
        f"Date range: {df['order_date'].min()} to {df['order_date'].max()}. "
        f"Numeric summary: {df.describe().loc[['min', 'max']].to_dict()}. "
        f"Use the SQL tool to query this table.")
```

| Chunk | Retrieves queries like |
|---|---|
| the summary | "what data do we have about orders" |
| a row | "which product costs 16.90" |

Both chunk types are indexed: the summary catches schema-level
questions and routes them to SQL; the rows catch entity-level
questions. The summary's "use the SQL tool" line is the router hint
embedded in the corpus itself.

## 3. The metadata round-trip

```python
metadata = {
    "unit_id": f"tbl-orders-r{row_idx:04d}",
    "source_table": "orders",
    "row_key": row["order_id"],
    "serialization": "row-major-v1",
}
# retrieved row → SQL join → full row from the warehouse
```

| Metadata field | Enables |
|---|---|
| `unit_id` | the citation audit |
| `row_key` | the SQL path can fetch the *live* row |
| `serialization` version | stale-serialization detection |

The retrieved chunk is a *pointer*: the SQL path can fetch the current
row by `row_key`, so the answer's numbers come from the warehouse, not
from the stale serialized text. This is the cross-store join (file 04).

## 5. The serialization pin note (the chunk contract's record)

```markdown
# Row serialization (W06)
- format: "col: value | col: value" (field names included)
- metadata: unit_id, source_table, row_key, serialization version
- summary chunks: one per table (shape + "use the SQL tool" hint)
- round-trip: retrieved chunk → live warehouse row by row_key
```

The pin note is the serialization contract — the format, the metadata,
and the round-trip. The round-trip is what makes the vector hit and
the warehouse row the same fact (file 04).

## 5. The serialization pin note (the chunk contract's record)

**Task:** extend `reports/sdk-versions.md` with the serialization
contract: the format string, the metadata fields, the summary chunk's
template, and the round-trip test command.

**Worked approach:** the serialization contract follows the pin
discipline — the format, the metadata, and the round-trip are the
chunk's specification.

**Pass criterion:** note committed; the round-trip command green as
recorded.

## Exercises

1. Serialize 100 order rows; embed them; query "which product appears
   most" — the serialization quality shows in the hit list.
2. Round-trip drill: retrieve a row chunk; use its `row_key` to fetch
   the live row via SQL; compare — the two sources must agree.
3. Summary drill: write the table summary chunk; query "what data do
   we have"; the summary must be the top hit.
4. Pin drill: write the note; the round-trip command recorded.