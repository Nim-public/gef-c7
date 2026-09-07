# 04.4 — Project: The Resumable Corpus Builder

> Subfolder index: [README.md](README.md) · Parent: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md)

---

## What you'll learn

- The capstone-grade ingestion pipeline: everything from this subfolder composed into one resumable, incremental, auditable system
- State management: how a crashed 1,000-document run resumes exactly where it stopped
- The ingestion report: the artifact that proves the corpus is trustworthy

## 1. The architecture

```
SOURCES (crawls, PDFs, CSVs — file 01/02/03)
   │
   ├─► 1. DISCOVER: list source assets (URLs/paths) → manifest rows
   ├─► 2. FETCH/EXTRACT: per-asset, with retries; raw cached to disk
   ├─► 3. EXTRACT TEXT: pypdf/pdfplumber/BS4 — routed by asset type
   ├─► 4. CLEAN: unicode → boilerplate → whitespace (file 05)
   ├─► 5. CHUNK: sentence-aware (file 05 §4) with metadata
   └─► 6. REPORT: per-asset status JSONL + aggregate stats
```

**Resumability invariant:** every stage writes its outputs keyed by a content fingerprint (sha1 of the source), and checks for existing outputs before redoing work. Kill the process anywhere; re-run continues.

## 2. The fingerprint-keyed state

```python
import hashlib, json
from pathlib import Path

def fingerprint(data: str | bytes) -> str:
    if isinstance(data, str): data = data.encode("utf-8")
    return hashlib.sha1(data).hexdigest()[:16]

STATE = Path("data/corpus_state.jsonl")        # append-only: one row per asset

def already_done(fp: str) -> bool:
    if not STATE.exists(): return False
    return any(json.loads(l).get("fp") == fp for l in STATE.open(encoding="utf-8"))
```

Append-only state (W1-04's JSONL pattern) survives crashes: a partially written last line is skipped on read (`if line.strip()` + try/except). The fingerprint means re-crawled identical content is detected and skipped even if the URL changed.

## 3. The pipeline (composed)

```python
def ingest(sources: list[str], out: Path) -> dict:
    stats = {"in": 0, "done": 0, "skipped": 0, "failed": 0}
    report = out / "ingestion_report.jsonl"
    with report.open("a", encoding="utf-8") as log:
        for src in sources:
            fp = fingerprint(src)
            stats["in"] += 1
            if already_done(fp):
                stats["skipped"] += 1; continue
            try:
                raw = fetch_and_cache(src)                 # file 03 §1 + cache
                text = extract_text(raw, src)              # file 02, routed by type
                chunks = chunk_by_sentences(clean_for_corpus(text))   # file 05
                write_chunks(out, fp, src, chunks)         # JSONL with metadata
                log.write(json.dumps({"fp": fp, "src": src, "status": "ok",
                                      "chunks": len(chunks)}) + "\n")
                stats["done"] += 1
            except Exception as e:
                log.write(json.dumps({"fp": fp, "src": src, "status": "failed",
                                      "error": f"{type(e).__name__}: {e}"}) + "\n")
                stats["failed"] += 1
    return stats
```

The `try/except` per asset is what makes 1,000-asset runs finish despite 30 failures — failures are **recorded**, never swallowed (W10-02's error contracts). The stats dict is the ingestion report's summary.

## 4. The metadata contract (per chunk)

```python
{
  "id": "fp:3f2a::chunk:04",           # stable: fingerprint + ordinal
  "source": "https://…",               # or file path
  "fp": "3f2a…",                       # content fingerprint
  "chunk_ordinal": 4, "n_chunks": 12,
  "text": "…",
  "ingested_at": "2026-11-20T10:00:00Z"
}
```

This is the W4-02 metadata schema's ingestion side — citations, dedup, and re-processing all key off these fields. When W16-01 versions the eval set, the `fp` provenance answers "which corpus version was this eval run against?"

## 5. The operations view

| Scenario | Behavior |
|---|---|
| crash at asset 617/1000 | re-run: 616 skipped, resumes at 617 |
| same document at a new URL | fingerprint skip — no duplicate chunks |
| document content changed | new fingerprint → re-ingested; old chunks become orphans → cleanup job |
| extraction fails on 30 assets | run completes; report lists all 30 with errors; fix and re-run only those |

The cleanup job (orphaned chunks) checks stored chunk `fp`s against the current state file — a small set-difference, run after big corpus updates (W4-05's re-indexing rule).

## Exercises

1. Build the pipeline over ≥20 real sources (W1-04 crawl + 5 local PDFs); kill the process mid-run (Ctrl-C); resume and verify the skip counts.
2. Ingestion report: generate the summary (in/done/skipped/failed + median chunk stats); make it a one-glance quality statement.
3. Fingerprint drill: re-ingest the same source under a different URL — verify zero new chunks. Then modify the content by one character — verify re-ingestion.
4. Failure injection: make extraction raise on every 7th asset; verify the run completes, the report lists exactly the 1-in-7 failures, and a fixed re-run processes only those.
5. Cleanup job: delete 3 source files after ingestion; implement the orphan-chunk detection (stored fps vs state fps) and remove the orphans with a logged count.

## Pitfalls

- **State file as a single JSON blob** — crash during write corrupts everything; append-only JSONL lines (W1-04)
- **Fingerprinting the URL instead of content** — content moves, URLs change; fingerprint the payload
- **Chunk ids without a corpus-version component** — eval runs (W16-01) need to know which corpus version produced them; add a corpus version to the manifest and stamp chunks
- **Silent failure counting without errors listed** — "30 failed" without reasons is unactionable; every failure row carries the exception
- **Re-running extraction with changed cleaning code but the same fingerprints** — cleaning changes the *content*, so the fingerprint must include a pipeline-version component (W7-02's determinism rule)

## Resources

- Files 01/02/03 of this subfolder + W4-02 (chunking), W4-05 (incremental ingestion), W1-04 (crawling) — composed here
- [W9-05](../../../Phase-1-24-Week-Plan/Week-09-RAG-with-Image-Video-Audio/05-practice-multimodal-rag.md) — the retrieval-side contract these chunks feed
- W16-01 (eval versioning) — the consumer of corpus versioning
