# 02.4 — Metadata Design

> Subfolder index: [README.md](README.md) · Parent: [../02-chunking-strategies.md](../02-chunking-strategies.md)

---

## What you'll learn

- The metadata schema: every field, its type, and its consumer
- The design review: each field earns its place with a named consumer
- The metadata lifecycle: written at ingestion, read at query, updated at corpus changes

## 1. The schema

```python
CHUNK_METADATA = {
    "id": str,              # "{source_fp}::chunk:{ordinal}" — stable, unique
    "source_fp": str,       # content fingerprint of the source document
    "source_path": str,     # original file path or URL
    "doc_type": str,        # policy | faq | ticket | report | ...
    "section": str,         # "Refunds > Timeline" — the section path (W5-01)
    "page": int | None,     # for PDFs
    "ordinal": int,         # chunk position within the document
    "n_chunks": int,        # total chunks in the source (for progress/citation)
    "updated": str,         # ISO date of the source document
    "permissions": str,     # "all-staff" | "engineering" | "hr-only"
    "language": str,        # "en" | "hi" | ...
    "embedder": str,        # the model that produced the vector (W4-03's contract)
    "ingested_at": str,     # when this chunk was created
}
```

Each field has a named consumer — the design review question: *"who reads this field, and what do they do with it?"* Fields without consumers get cut; consumers without fields get added.

## 2. The consumers (who reads what)

| Field | Consumer | Use |
|---|---|---|
| `id` | everything | dedup, joins, citations |
| `source_path` | citation renderer | "[handbook.pdf p.12]" |
| `doc_type` | router (W6-04/W14-04) | filter before retrieval |
| `section` | contextual headers (W5-01), citations | path-aware answers |
| `page` | PDF citation rendering | "[handbook.pdf p.12]" |
| `permissions` | prefilter (W5-03) | security — access control |
| `updated` | freshness ordering, staleness alerts | "as of" answers |
| `language` | multilingual routing (W12-05) | filter by language |
| `embedder` | consistency check (W4-03) | query-time validation |
| `ingested_at` | corpus versioning (W16-01) | audit trail |

## 3. The metadata lifecycle

| Stage | Metadata operation |
|---|---|
| ingestion | all fields written; schema validated |
| re-ingestion | updated fields changed; others preserved |
| corpus update | orphaned chunks detected by `source_fp` (W4-05) |
| query | fields read for filtering, citation, and provenance |
| eval | fields used for slice analysis (W16-01) |
| security review | permissions audited (E7-04) |

The lifecycle makes metadata a *living* part of the system — not a one-time annotation.

## 4. The schema evolution

Metadata schemas change (new fields, renamed values). The rules:

- **Additive changes are safe** — new fields with defaults don't break old consumers
- **Renames are breaking** — migrate or dual-write during the transition
- **The schema is versioned** — `{schema_version: 2}` in the metadata itself
- **Old chunks get migrated** — a backfill job updates existing chunks (W4-05's incremental rule)

## Exercises

1. Schema design review: for each field in your current implementation, name the consumer; cut the fields without one; add the missing ones.
2. The migration drill: add a `language` field to existing chunks — write the backfill that detects language and updates; verify no chunk is missed.
3. Permission audit: query with and without the `permissions` prefilter — verify a restricted user cannot retrieve restricted chunks (W5-03's security test).
4. The schema-drift detection: two ingestion runs with different schemas — write the detector that flags the difference; decide the migration path.
5. Citation rendering: from metadata alone, render three citation formats (inline, footnote, hover) — the metadata supports all three without re-querying.

## Pitfalls

- **Schema drift without detection** — old and new chunks coexist with different fields; the detector flags it
- **Free-text enum fields** — "policy"/"Policy"/"POLICY" as separate values; use constrained sets
- **Metadata without timestamps** — staleness and freshness checks need `ingested_at`/`updated`
- **Permissions at the document level only** — chunk-level permissions enable finer control (a doc with one restricted section)
- **Migration without a dry-run** — backfill jobs corrupt data silently; dry-run first, then apply

## Resources

- W4-02 parent (the schema introduction), W5-03 (filtering), W16-01 (slices) — composed here
- W9-02 (LanceDB metadata queries) — the enforcement layer
- W20-02 (document-AI metadata — the structured-data extension)
