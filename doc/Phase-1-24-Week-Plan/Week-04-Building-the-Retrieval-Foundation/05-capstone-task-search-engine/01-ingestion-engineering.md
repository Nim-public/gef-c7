# 05.1 — Ingestion Engineering

> Subfolder index: [README.md](README.md) · Parent: [../05-capstone-task-search-engine.md](../05-capstone-task-search-engine.md)

---

## What you'll learn

- The state machine: every source is pending → extracting → indexing → done/failed
- The fingerprint-keyed dedup: identical content never re-ingests
- The incremental protocol: only changed sources re-process

## 1. The state machine

```python
STATES = ["pending", "extracting", "chunking", "indexing", "done", "failed"]

def ingest_source(src: str, state: dict) -> dict:
    fp = fingerprint(src)
    if state.get(fp, {}).get("status") == "done":
        return {"status": "skipped", "reason": "already ingested"}
    try:
        state[fp] = {"status": "extracting"}
        text = extract(src)
        state[fp] = {"status": "chunking"}
        chunks = chunk(text)
        state[fp] = {"status": "indexing"}
        index_chunks(chunks)
        state[fp] = {"status": "done", "chunks": len(chunks)}
        return {"status": "done", "chunks": len(chunks)}
    except Exception as e:
        state[fp] = {"status": "failed", "error": str(e)}
        return {"status": "failed", "error": str(e)}
```

The state machine makes the pipeline **inspectable** (what state is each source in?), **resumable** (skip done, retry failed), and **auditable** (the state log is the report).

## 2. The dedup guarantee

```python
def fingerprint(content: str | bytes) -> str:
    if isinstance(content, str): content = content.encode("utf-8")
    return hashlib.sha1(content).hexdigest()[:16]
```

The fingerprint is computed from the *content*, not the path or URL — the same document at a different URL produces the same fingerprint and is skipped. Content changes → new fingerprint → re-ingestion.

## 3. The incremental protocol

```python
def incremental_ingest(sources: list[str], state: dict) -> dict:
    new_or_changed = [s for s in sources
                      if fingerprint(s) not in {r.get("fp") for r in state.values()
                                                if r.get("status") == "done"}]
    for src in new_or_changed:
        ingest_source(src, state)
    return {"processed": len(new_or_changed), "skipped": len(sources) - len(new_or_changed)}
```

The incremental protocol is what makes the pipeline production-viable: a daily corpus update re-processes only changed documents, not the full corpus.

## Exercises

1. Build the state machine; crash at source 60%; resume — verify exactly the right sources skipped and processed.
2. The dedup drill: ingest the same content under 3 paths — one fingerprint, one chunk set, zero duplicates.
3. The change-detection drill: modify one document by one character — verify only that document re-ingests.
4. The state inspection: build a dashboard (or CLI) showing per-source state — the operational visibility.
5. The failure-retry: force a failure; fix the cause; re-run only the failed sources — the selective retry protocol.

## Pitfalls

- **Fingerprinting the path instead of content** — the same file at a new path re-ingests; the content hash is the identity
- **State stored in memory only** — a restart loses the state; persist to disk (JSONL or SQLite)
- **Partial chunk sets** — a crash mid-chunking leaves partial chunks in the index; clean up or use transactions
- **The state file as a single JSON blob** — concurrent access corrupts it; append-only JSONL or SQLite (W15-01's pattern)
- **Infinite retry on persistent failures** — a source that always fails retries forever; cap the retries and mark permanently failed

## Resources

- W4-02 (chunking), W4-03 (indexing), W1-04 (extraction) — the stages
- W4-05 (the task consuming this pipeline), W15-01 (the reliability patterns) — composed here
