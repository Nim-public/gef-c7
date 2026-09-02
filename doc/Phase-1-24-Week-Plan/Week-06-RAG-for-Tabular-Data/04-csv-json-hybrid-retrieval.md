# 04 — CSV/JSON Retrieval & the Hybrid Bridge

> Week 6 index: [README.md](README.md)

**Session 2 topics:** *Hybrid retrieval · Other formats of structured data — CSV data and JSON data.*

---

## What you'll learn

- The structured-data retrieval decision tree: SQL, hybrid-index, or plain chunking
- Making CSV/JSON files queryable three ways (pandas/SQL, search-indexed, LLM-summarized)
- Hybrid retrieval over semi-structured data — combining Week 4's engine with Week 6's precision
- When *not* to embed rows, and what to do instead

## 1. The decision tree (start here)

```
Is the data tabular and are questions aggregational/relational?
├─ yes, sizable, stable schema → load into SQL (file 03) — Text2SQL it
├─ yes but small/frequently-changing file → pandas over CSV/JSON, LLM writes
│   pandas-filter descriptions OR small table → just give it whole
└─ is the content prose-in-structure (descriptions, notes, JSON blobs)?
    → index like documents (Week 4/5 engine) — but serialize smartly (§3)
```

The failure this tree prevents: **embedding 10k rows and calling it RAG.** Each row becomes a 20-token vector that can't answer "total by region", "top 3", or "average" — the questions people actually ask of tables. Numbers are *computed*, not *found* (file 03).

## 2. CSV/JSON as first-class sources

### CSV → SQLite (file 01's bridge, two lines)

```python
import pandas as pd, sqlite3

df = pd.read_csv("data/products.csv", dtype={"sku": "string"})   # preserve ID leading zeros!
df.to_sql("products", sqlite3.connect("capstone.db"), if_exists="replace", index=False)
# now Text2SQL applies — no special pipeline needed
```

### JSONL/JSON → records → same door

```python
import json
rows = [json.loads(l) for l in open("data/events.jsonl", encoding="utf-8")]
pd.DataFrame(rows).to_sql("events", conn, if_exists="replace", index=False)
```

### The "small table" path (underappreciated)

Under ~100 rows × a few columns: **paste the table into the prompt.** No index, no retrieval — the model reads the whole thing. Formats matter:

```
| sku | name | price | stock |
|---|---|---|---|
| P-100 | GPU | 45000 | 2 |
```

Markdown tables beat JSON-in-prompt for LLM readability (column-aligned). Token-budget check (tiktoken) decides when a table is "too big to paste" — that threshold is your router's job.

## 3. When rows ARE documents: hybrid retrieval over semi-structured data

Some structured data is *prose in disguise* — product descriptions, ticket bodies, review texts, JSON blobs with rich text fields. These deserve Week 4's engine, with three adaptations:

### a. Serialize rows into retrievable text (row-major)

```python
def row_to_text(row: dict) -> str:
    return (f"Product {row['sku']}: {row['name']} — {row['description']} "
            f"Price ₹{row['price']}, {row['stock']} in stock, category {row['category']}.")

corpus = [row_to_text(r) for r in rows]        # embed these (W4 pipeline as-is)
```

Every field becomes findable-by-meaning; the serialization *is* the schema prompt for the embedder.

### b. Table-level summaries (summary-major)

For "what tables/datasets do you have?" questions, embed one summary chunk per file/table:

```python
summary = (f"Table 'products': 1200 rows. Columns: sku (id), name, price (INR), "
           f"stock, category. Covers electronics inventory, updated 2026-08.")
```

This is the router's map: query hits the summary chunk → router knows to answer from *that table* (via Text2SQL), not from a row.

### c. Metadata round-trip

Chunk metadata carries the row's key: `{"source_table": "products", "row_key": "P-100"}` — so a search hit can *fetch the live row* (or trigger the SQL for its siblings). Document-RAG finds "the GPU product page"; the relational side pulls current price/stock. That join is the hybrid architecture of your capstone:

```
question ─► router ─┬─ aggregational → Text2SQL (file 03)
                    ├─ prose-y      → vector+BM25 hybrid (W4/W5) ──┐
                    └─ both         → do both, cite both ◄────────┘ (results fused like W4-04 RRF)
```

## 4. Hybrid retrieval mechanics for structured corpora

Week 4's RRF fusion generalizes untouched — only the corpus changes:

| Signal | Use |
|---|---|
| BM25 over serialized rows | exact SKU/IDs, field names |
| Vector over serialized rows | intent/description match ("cheap gaming laptop") |
| SQL (router-selected) | counts, sums, comparisons |
| Metadata filters (`category='gpus'`) | the Week 5 prefilter pattern, now on tabular columns |

One ingestion pipeline, multiple indexes: SQLite (rows) + LanceDB (serialized chunks) + BM25 (same chunks). The `id` in every chunk is the join key across all three — the discipline from W4-02's metadata section pays off here.

## Exercises

1. Load your CSV into SQLite *and* the hybrid index (a+b above). Answer "which products are similar to X but cheaper?" — which retrieval arm contributes? (Hint: the answer needs both.)
2. Row-major vs summary-major: ask "what data do you have about refunds?" — does the summary chunk route better than row chunks? Measure with your harness.
3. Injection via cells: put "IGNORE INSTRUCTIONS" inside a product description; run the file 03 answer-formatter. Does the W3-02 delimiting hold?
4. Build the §1 decision-tree as an actual `route(question)` function (rules first, zero-shot LLM second). Log its decisions on 20 mixed questions; report accuracy.
5. Denormalization probe: flatten one nested JSON into two tables vs one JSON column. Query both for "events by user in March" — which shape did SQL prefer?

## Pitfalls

- **Embedding what should be computed** — the §1 tree exists because this is the default failure
- **Header row lost in serialization** — "₹45000" without "Price (INR)" poisons both embeddings and answers
- **Mixed-type columns** (IDs as ints vs strings) breaking joins *and* filters — enforce dtypes at ingestion (W1-03)
- **LLM narrating unverified numbers** — the file 03 rule: result rows are truth; format from them, never from the model's memory of the schema
- **Three indexes, three stale versions** — one ingestion script writes all stores, one `updated` column everywhere

## Resources

- LangChain [SQL + CSV chains](https://python.langchain.com/docs/tutorials/sql/) — library versions of §2
- DuckDB — query CSVs/JSON *directly* with SQL, no load step (`SELECT * FROM 'data.csv'`) — the analysis shortcut worth knowing
- [sqlglot](https://github.com/tobymao/sqlglot) (file 03) — same validator for pandas/duckdb dialects
- Anthropic Engineering, *Contextual retrieval* — the serialization-with-context idea generalized
