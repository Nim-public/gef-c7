# 02 — Knowledge Bases & Data Ingestion

> Week 12 index: [README.md](README.md)

**Session 1 topics:** *Setting up data ingestion from databases (RDBMS, CSV, JSON).*

---

## What you'll learn

- Agno `Knowledge`: the framework's RAG layer, with your W4/W5 choices as pluggable parts
- LanceDB as the knowledge vector DB (your W9 stack, framework-managed)
- Ingesting RDBMS/CSV/JSON the *right* way: structured data stays queryable (W6), prose goes to knowledge (W7-01's decision tree)
- The hybrid agent: knowledge tool + SQL tool answering over both halves

## 1. Agno Knowledge — RAG as configuration

```python
from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    vector_db=LanceDb(                       # your W4/W9 store, framework-managed
        uri="tmp/lancedb",
        table_name="capstone_knowledge",
        search_type=SearchType.hybrid,       # native hybrid (W9-02)
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

knowledge.insert(url="https://.../capstone-handbook.pdf")   # or text=, or local paths

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,                   # wires a knowledge-search tool automatically
    instructions=["Answer ONLY from knowledge; cite sources; say when missing."],
)
agent.print_response("What is the refund timeline?")
```

Recognize everything under the abstraction — you built each piece: chunking (W4-02) happens inside readers, embeddings come from the `embedder` (W5-02), `SearchType.hybrid` is W4-04's keyword+vector+RRF, and `search_knowledge=True` is the W10-02 tool registry adding one tool. **The framework doesn't change the RAG contract (W4-01); it packages it.**

Design decisions you still own:

- **Same embedder model + normalization rules** as any existing index (W4-03's mismatch warning — Agno tables are *separate* from your W9 tables; don't double-store without a reason)
- **Readers = your W1-04 skills**: PDF/CSV/JSON URLs, text files; the content-aware caveats (tables, W7) still apply
- **Insufficiency escape**: keep the instruction + verify the no-match behavior (W4-01's test, on the framework path)

## 2. Ingestion by source type

| Source | Path into the agent | Your prior work |
|---|---|---|
| PDFs/docs | `knowledge.insert(url=... / path=...)` → auto-chunked | W1-04 parsing caveats (scans, layouts) still apply |
| Prose in CSV/JSON | extract text fields → insert as documents | serialization rules (W6-04 row-major) |
| **Tabular data** | *not* knowledge — load to SQLite (W6) + expose a SQL tool | the decision tree, unchanged |
| Mixed | both, with the router (file 05) | W6-04's hybrid bridge |

The session's "RDBMS, CSV, JSON ingestion" is honestly two pipelines, and conflating them is the classic mistake: **knowledge for prose, tables for SQL** (file 05 makes the agent pick correctly).

```python
# CSV: prose column → knowledge; numeric columns → SQL
import pandas as pd

df = pd.read_csv("data/products.csv")
for _, row in df.iterrows():
    knowledge.insert(text=f"Product {row['sku']}: {row['name']} — {row['description']}")

df.drop(columns=["description"]).to_sql("products", sqlite3.connect("capstone.db"),
                                        if_exists="replace", index=False)
```

## 3. Data ingestion from RDBMS (the session's phrasing)

For an *existing* relational DB (MySQL/Postgres at work):

1. **Schema → knowledge (summary chunks)**: one summary per table (W6-04's summary-major pattern) so the agent knows what exists
2. **Rows → SQL tool**, not knowledge: live data belongs to `sql_query` (file 03)
3. **Long text columns** (ticket bodies, notes) → optionally into knowledge with `source_table/row_id` metadata (W6-04's hybrid round-trip)

```python
tables_summary = []
for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    cols = [c[1] for c in conn.execute(f"PRAGMA table_info({name})")]
    n = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    knowledge.insert(text=f"Table '{name}': {n} rows. Columns: {', '.join(cols)}.")
```

Now "what data do we have about refunds?" hits the summary chunk, and the agent knows to call `sql_query` for the numbers.

## 4. Grounding rules for the knowledge tool

The W4-01 prompt contract translates to `instructions`:

```python
instructions=[
    "Answer ONLY from your knowledge base and tools.",
    "Cite sources as [source] for every factual claim.",
    "If knowledge search returns nothing relevant: 'I don't have that information.'",
    "Never combine your general knowledge with knowledge-base facts.",
]
```

Then *test* the grounding (W4-01 exercise 5's insufficiency battery — 5 unanswerable questions). Frameworks make grounding *easier to configure* and *easier to skip testing*.

## Exercises

1. Load 10 of your capstone docs via `knowledge.insert`; verify a retrieval fires (enable Agno's debug/logs) and compare the chunks against your W4-02 chunker's output — same quality?
2. Dual-pipeline ingest (§2 CSV block): one question that needs prose ("describe product P-100") and one that needs SQL ("count products under ₹5000"). Does the agent pick the right tool for each?
3. Grounding battery: 5 unanswerable questions through the knowledge agent; count the insufficiency escape firing. Fix instructions until 5/5.
4. Swap the embedder (`OpenAIEmbedder` → a local `sentence-transformers` model if supported, or another API) — re-ingest, re-ask. What must you invalidate when the embedder changes (W4-03)?
5. Write the ingestion section of your capstone README: what lives in Knowledge vs SQLite vs neither, with the W7-01 decision tree as the rationale.

## Pitfalls

- **Double-storing the corpus** — Agno's LanceDB table + your W9 table with different chunkers = two answers to the same question; pick one source of truth per artifact
- **Inserting whole CSVs as text** — numeric tables embedded as prose lose aggregation power (W6-04's tree)
- **Hybrid search configured but FTS/index missing** — silent fallback to vector-only (W9-02's rebuild pitfall)
- **No citations configured** — `markdown=True` without a citation contract = uncited RAG (W4-01)
- **Ingestion not resumable** — framework readers re-insert on re-run; dedup by id/fingerprint (W4-05's incremental rule)

## Resources

- Agno [Knowledge docs](https://docs.agno.com) — readers, vector DBs, hybrid search, filters
- Agno [LanceDB integration](https://docs.agno.com) + [Your first knowledge base](https://docs.agno.com/examples) walkthroughs
- W4-01/02/03 + W6-04 — the concepts being packaged here
- LangChain equivalent loaders (comparison reading) — same ideas, different packaging
