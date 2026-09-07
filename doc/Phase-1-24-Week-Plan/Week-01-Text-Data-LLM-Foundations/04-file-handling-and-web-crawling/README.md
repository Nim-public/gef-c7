# 04 — File Handling & Web Crawling: Deep Dive

> Parent topic: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md) · Week 1 index: [../../README.md](../../README.md)

**Study order:**

| Order | File | Focus | Est. time |
|---|---|---|---|
| 1 | [01-text-and-formats-io.md](01-text-and-formats-io.md) | pathlib, UTF-8, CSV/JSON/JSONL deep dive | 3 h |
| 2 | [02-pdf-extraction.md](02-pdf-extraction.md) | pypdf/pdfplumber/OCR decision tree | 3 h |
| 3 | [03-web-crawling.md](03-web-crawling.md) | requests, politeness, parsing, retry/backoff | 3 h |
| 4 | [04-corpus-builder-project.md](04-corpus-builder-project.md) | End-to-end resumable corpus builder | 4 h |
| — | [exercises.md](exercises.md) | Labs with worked approaches | 3 h |

## File map

- **01** — text I/O and encoding, the CSV option matrix, JSON/JSONL streaming, format selection
- **02** — the three PDF layers (text-layer extraction, layout parsing, OCR) and their decision tree
- **03** — fetching with sessions/retries, politeness, parsing with BeautifulSoup, the crawl loop
- **04** — the capstone-grade ingestion pipeline: resumable, incremental, dedup-safe, reported
- **exercises.md** — labs including the W1-04 corpus rebuild
