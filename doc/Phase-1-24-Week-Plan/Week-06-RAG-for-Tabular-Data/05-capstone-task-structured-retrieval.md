# 05 — Weekly Task: Structured Data Retrieval in the Capstone

> Week 6 index: [README.md](README.md) · **Due: before Week 7 (by 17 Oct)**

**Task (from the schedule):** *Extend your capstone project to include structured data retrieval.*

Week 4/5 gave the capstone document-RAG; this task adds the second retrieval mode — SQL/Text2SQL and structured sources — plus the router that decides between them. After this week, the capstone answers over *both* halves of its data.

---

## 1. Deliverable

```
structured/
  schema.sql              # DDL: tables, keys, constraints (file 01)
  ingest_tabular.py       # CSV/JSON → SQLite (+ summary chunks → vector index, file 04)
  text2sql.py             # schema prompt + validator + repair loop + formatter (file 03)
  router.py               # route(question) → "sql" | "vector" | "both" | "small-table"
  README.md               # schema, decisions, eval table
```

Demo transcript: 8 questions — 3 aggregational (SQL), 3 prose-y (vector), 1 hybrid (both cited), 1 unanswerable (either path refuses).

## 2. Build order (do it in this order, honestly)

1. **Schema first** (`schema.sql`): 2–4 tables from your capstone domain, keys + ≥2 constraints, with the justification comments from file 01 ex. 1
2. **Load real data**: CSV/JSON via pandas `to_sql` (≥200 rows; synthetic-but-realistic if needed — *mark it synthetic in the README*)
3. **Text2SQL service**: file 03's four components — schema prompt (generated from the DB, not hand-copied), `validate_sql`, repair loop, grounded formatter with the `_query_` audit line
4. **Summary chunks**: one per table (file 04 §3b) into the existing vector index, so the router has a map
5. **Router**: rules first ("how many/top/average/sum/revenue/by region" → sql), zero-shot LLM fallback (W2-02) for the rest; log every decision
6. **Hybrid answers**: when both arms fire, fuse like Week 4's RRF — SQL rows + retrieved chunks in one grounded prompt, citing *both* table and document sources

## 3. Evaluation (the graded component)

Extend your harness — one table, two slices:

| Slice | Metric | n | Result |
|---|---|---|---|
| SQL questions | answer correct (hand-verified vs gold SQL) | 10 |  |
| Vector questions | hit rate @5 (existing W4 harness) | 25 |  |
| Router | routing accuracy | 20 |  |
| Unanswerable | correct refusal (both arms) | 8 |  |

Plus the standard safety battery:

- [ ] Read-only connection proven (attempt a write through the *LLM* path; show the failure)
- [ ] Validator trips on UPDATE/multi-statement/`SELECT *`-PII probes (file 03 ex. 3)
- [ ] Cell-injection attempt contained (file 04 ex. 3)
- [ ] Date questions handled via injected "today" + explicit rules (file 03 ex. 4)

## 4. Rubric

- [ ] Schema has keys/constraints; data loaded from real files, reproducibly
- [ ] Text2SQL: schema prompt + validation + ≥1 working repair + result-grounded answers
- [ ] Router accuracy ≥80% on 20 mixed questions, decisions logged
- [ ] Hybrid answer demonstrated with dual citations (table + document)
- [ ] All 4 safety checks pass
- [ ] README: the §1 decision-tree applied to *your* data (what went SQL, what went vector, what stayed small-table) — this section is what your mentor will quote back at the capstone review

## 5. The seam into Week 7 (multimodal)

Your capstone now retrieves: documents (W4/W5) + tables (W6). Week 7 adds *images/audio/video* as a third modality — and the router grows a third arm. Before Week 7, note in the README: which of your data is inherently multimodal (product photos? scanned PDFs? audio logs?), and what one image-use-case would prove the most value. That's your W7–9 runway.

Bring to Office Hours (15 Oct): the router's confusion cases (which questions went to the wrong arm?) — routing errors are the new retrieval errors, and mentors read router logs the way they read eval tables.
