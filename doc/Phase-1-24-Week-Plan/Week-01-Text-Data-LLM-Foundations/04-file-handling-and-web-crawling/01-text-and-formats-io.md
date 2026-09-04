# 04.1 — Text & Format I/O

> Subfolder index: [README.md](README.md) · Parent: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md)

---

## What you'll learn

- pathlib as the file-system API (paths as objects, not strings)
- Encoding discipline: UTF-8 everywhere, `utf-8-sig`, error policies
- CSV option matrix and streaming
- JSON vs JSONL vs Parquet — format selection by workload

## 1. pathlib — paths as objects

```python
from pathlib import Path

root = Path("data")
root.mkdir(parents=True, exist_ok=True)

p = root / "docs" / "handbook.pdf"       # / operator joins — no string concat
print(p.suffix, p.stem, p.parent)        # '.pdf' 'handbook' data/docs
list(root.glob("**/*.txt"))              # recursive search
p.resolve()                              # absolute, normalized
p.read_text(encoding="utf-8")            # read/write helpers (W1-04 baseline)
```

Operations you'll use weekly: `glob`/`rglob` for corpora, `stat().st_size` for size checks, `.exists()`, `.with_suffix(".json")` for format swaps, `iterdir()` for listings.

## 2. Encoding discipline

```python
text = path.read_text(encoding="utf-8")          # explicit, always
open("x.csv", encoding="utf-8-sig")              # strip Excel BOM on read
open("x.txt", "w", encoding="utf-8", errors="strict")   # don't silently replace
```

| Policy | Behavior | When |
|---|---|---|
| `errors="strict"` (default) | raises on bad bytes | ingestion — you want to know |
| `errors="replace"` | `\ufffd` markers | last resort, logged |
| `utf-8-sig` read | strips BOM | Excel-exported CSVs |

Non-negotiable: explicit `encoding=` on every text open (W1-04's rule); the `UnicodeDecodeError` you suppress today is the garbage chunk you debug tomorrow (W4).

## 3. CSV — the option matrix

```python
import csv, pandas as pd

# csv module: full control, streaming
with open("data/orders.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f): process(row)

# pandas: analysis-ready, dtype control
df = pd.read_csv("data/orders.csv", dtype={"id": "string"},
                 parse_dates=["created_at"], na_values=["", "NA"])
for chunk in pd.read_csv("data/huge.csv", chunksize=100_000): ...
```

Real-world CSV failure modes, each mapped to an option: mixed encodings (`encoding=`), embedded commas/newlines (`quoting=`), type coercion (`dtype=`, `parse_dates=`), NA spellings (`na_values=`), huge files (`chunksize=`). The W6-01 pandas-bridge exercises drill these.

## 4. JSON vs JSONL vs Parquet

| Format | Shape | Best for | Caveat |
|---|---|---|---|
| JSON | one tree | configs, API payloads | load whole file |
| **JSONL** | one record/line | logs, datasets, streaming append | no nesting across records |
| Parquet | columnar binary | large analytics tables | needs engine (pyarrow) |

```python
import json
rows = [json.loads(l) for l in open("data/corpus.jsonl", encoding="utf-8") if l.strip()]
open("out.jsonl", "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
```

The JSONL append pattern is this program's standard log/dataset format (W9-05, W10-04) — one record per line means partial reads survive crashes. `ensure_ascii=False` keeps multilingual text readable (W1-02).

## 5. Format selection (the decision)

- **Config/small structured** → JSON
- **Event logs, datasets, append-only** → JSONL
- **Analytical tables > 100k rows** → Parquet (typed, compressed, fast)
- **Human handoff** → CSV (with the option matrix applied)
- **Long documents** → raw text/pdf with a manifest (W7-01)

## Exercises

1. Build `safe_read(path)` that tries `utf-8`, then `utf-8-sig`, then `latin-1` — returning (text, encoding_used); test on BOM'd, latin-1, and clean files.
2. Convert 12 monthly CSVs to a single Parquet dataset with a consistent schema (W6-02's normalize step) — verify row counts and dtypes survive.
3. JSONL surgery: deduplicate a 1M-line JSONL by record hash using a streaming pass — no full load; report before/after counts and throughput.
4. Format triage: one 500k-row table stored as CSV, JSON, and Parquet — compare file size, load time, and memory. Table it.
5. Round-trip audit: CSV → JSONL → CSV — find and explain every field that changed (W1-04 ex. 4 revisited with the option matrix).

## Pitfalls

- **`encoding` omitted** — Windows default cp1252 mangles the first non-ASCII byte; always explicit
- **JSONL lines without `ensure_ascii=False`** — `\uXXXX` soup makes review impossible
- **CSV type coercion after the fact** — leading zeros, dates-as-strings (W6-01's dtype lesson)
- **Partial JSONL writes from crashes** — last line may be truncated; tolerate-and-skip malformed final lines on read
- **Parquet without schema discipline** — schema evolution across files breaks merges; pin schemas (W6-02)

## Resources

- [pathlib docs](https://docs.python.org/3/library/pathlib.html) · [csv](https://docs.python.org/3/library/csv.html) · [json](https://docs.python.org/3/library/json.html)
- pandas [IO tools](https://pandas.pydata.org/docs/user_guide/io.html) · [Parquet](https://pandas.pydata.org/docs/user_guide/io.html#parquet)
- W1-04 parent, W6-02 (formats), W7-01 (manifests) — composed here
