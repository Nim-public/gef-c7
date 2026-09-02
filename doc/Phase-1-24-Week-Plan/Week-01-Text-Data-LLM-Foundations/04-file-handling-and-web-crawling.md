# 04 — File Handling & Web Crawling

> Week 1 index: [README.md](README.md)

**Session 1 topic:** *File Handling & Web Crawling: Working with CSV, JSON, PDF files.* RAG systems (Week 4+) are only as good as the corpus you ingest — and corpora come from files and the web.

---

## What you'll learn

- Robust file I/O with `pathlib` and UTF-8 everywhere
- CSV: `csv` module vs pandas, and streaming large files
- JSON and JSONL — the lingua franca of LLM datasets and APIs
- PDF text extraction with `pypdf` and `pdfplumber`
- Polite, legal web crawling: `requests` + `BeautifulSoup`
- A complete mini-corpus build: crawl → clean → save JSONL → load to pandas

## 0. Setup

```powershell
pip install pandas requests beautifulsoup4 pypdf pdfplumber
```

## 1. Text files done right

```python
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

path = data_dir / "notes.txt"
path.write_text("line one\nline two", encoding="utf-8")

text = path.read_text(encoding="utf-8")
for line in text.splitlines():
    print(line.upper())
```

Rules that prevent 90% of file bugs:

- Always pass `encoding="utf-8"` on both read and write
- Use `pathlib.Path`, not string concatenation
- Use `with open(...)` so files close on exceptions
- Glob for corpora: `list(data_dir.glob("**/*.txt"))`

```python
corpus = []
for f in Path("data/docs").glob("*.txt"):
    corpus.append({"source": f.name, "text": f.read_text(encoding="utf-8")})
```

## 2. CSV

CSV = comma-separated, but real files have dialects, quoting, and encodings.

```python
import csv
from pathlib import Path

with open("data/orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "product", "units"])
    writer.writeheader()
    writer.writerows([
        {"order_id": 1001, "product": "GPU", "units": 2},
        {"order_id": 1002, "product": "CPU", "units": 10},
    ])

with open("data/orders.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["product"], row["units"])
```

Pandas for anything analytical (see file 03), with the options that matter on real files:

```python
import pandas as pd

df = pd.read_csv("data/orders.csv")                 # guesses dtypes
df = pd.read_csv("data/orders.csv", sep=",", encoding="utf-8",
                 dtype={"order_id": "string"}, na_values=["", "NA", "-"])

for chunk in pd.read_csv("data/huge.csv", chunksize=100_000):   # streaming
    process(chunk)
```

**When CSV is wrong:** numeric-looking IDs (`00123`), embedded commas/quotes/newlines, mixed encodings. Prefer JSONL or Parquet for pipelines you control.

## 3. JSON and JSONL

### JSON (one document, tree-shaped)

```python
import json

doc = {
    "week": 1,
    "session": {"day": "Saturday", "topics": ["tokenization", "pandas"]},
}

path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
loaded = json.loads(path.read_text(encoding="utf-8"))
loaded["session"]["topics"][0]        # 'tokenization'
```

### JSONL (one JSON object per line)

JSONL is the standard for LLM fine-tuning datasets, logs, and eval sets — one record per line, streamable, append-friendly:

```python
records = [
    {"text": "RAG = retrieval + generation", "label": "notes"},
    {"text": "BPE merges frequent pairs", "label": "notes"},
]

with open("data/corpus.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open("data/corpus.jsonl", encoding="utf-8") as f:
    records = [json.loads(line) for line in f if line.strip()]
```

### Nested JSON → tables

```python
from pandas import json_normalize

api = {"results": [
    {"id": 1, "user": {"name": "Asha", "region": "south"}, "score": 0.91},
    {"id": 2, "user": {"name": "Ravi", "region": "north"}, "score": 0.88},
]}
json_normalize(api["results"], sep="_")
#    id user.name user.region  score
# 0   1      Asha       south   0.91
# 1   2      Ravi       north   0.88
```

## 4. PDF

```python
from pypdf import PdfReader

reader = PdfReader("data/report.pdf")
print(len(reader.pages))
text = "\n".join(page.extract_text() or "" for page in reader.pages)
print(text[:500])
```

`pdfplumber` when layout, tables, or coordinates matter:

```python
import pdfplumber

with pdfplumber.open("data/report.pdf") as pdf:
    page = pdf.pages[0]
    print(page.extract_text())
    tables = page.extract_tables()      # list of rows of cells
```

Reality checks you must internalize now:

- **Not all PDFs have a text layer** — scanned PDFs are images and need OCR (`pytesseract` + `pdf2image`)
- Extraction order can scramble multi-column layouts — always eyeball output
- Headers/footers/page numbers repeat — clean before chunking (Week 4)
- This is exactly the ingestion problem RAG systems fight; PDFs are the hardest common source

## 5. Web crawling

Crawling = fetching pages and following links to build a corpus. Scraping = extracting structured fields. You'll do both.

### Non-negotiables: politeness & legality

1. **Check `robots.txt`** (e.g., `https://site.com/robots.txt`) — it disallows paths per bot
2. **Rate-limit yourself**: sleep 1–2 s between requests; never hammer
3. **Set a User-Agent** identifying your bot honestly
4. **Check terms of service** and copyright before republishing content
5. Cache raw HTML locally — never fetch twice

### Fetching

```python
import time
import requests

HEADERS = {"User-Agent": "GEF-C7-learner/1.0 (study project)"}

def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()          # 4xx/5xx -> exception
    return resp.text

html = fetch("https://quotes.toscrape.com/")
time.sleep(1.5)
```

Status codes to know: `200` OK · `301/302` redirect · `403` blocked (check UA/robots) · `404` missing · `429` rate-limited (back off!) · `5xx` their problem, retry later.

For robust crawls: `requests.Session()` (reuses connections, carries cookies), retries with backoff (`tenacity` or a simple loop).

### Parsing with BeautifulSoup

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

for quote in soup.select("div.quote"):
    text = quote.select_one("span.text").get_text(strip=True)
    author = quote.select_one("small.author").get_text(strip=True)
    tags = [t.get_text() for t in quote.select("a.tag")]
    print(text, "|", author, "|", tags)
```

CSS selectors you'll use constantly: `div.quote`, `#main`, `.highlight`, `a[href]`, `div > p`, plus `.get("href")` for attributes.

### The crawl loop (pagination + dedup + save)

```python
import json
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://quotes.toscrape.com"
HEADERS = {"User-Agent": "GEF-C7-learner/1.0 (study project)"}

def crawl():
    url, seen = BASE, set()
    out = open("data/quotes.jsonl", "w", encoding="utf-8")
    while url and url not in seen:
        seen.add(url)
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=10).text, "html.parser")

        for q in soup.select("div.quote"):
            rec = {
                "text": q.select_one("span.text").get_text(strip=True),
                "author": q.select_one("small.author").get_text(strip=True),
                "tags": [t.get_text() for t in q.select("a.tag")],
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

        nxt = soup.select_one("li.next a")
        url = BASE + nxt.get("href") if nxt else None
        time.sleep(1.5)                      # be polite
    out.close()

crawl()
```

### Close the loop: corpus → pandas

```python
import json
import pandas as pd

with open("data/quotes.jsonl", encoding="utf-8") as f:
    df = pd.DataFrame(json.loads(line) for line in f if line.strip())

df["n_tags"] = df["tags"].str.len()
df.explode("tags")["tags"].value_counts().head(10)   # most common tags
```

You just built the exact pipeline of every ingestion system: **fetch → parse → normalize → persist → analyze**. Week 4 adds the "chunk → embed → index" tail.

### What about JavaScript-rendered pages?

`requests` gets the raw HTML only. If content appears after JS runs, you need a headless browser: **Playwright** (`pip install playwright`) — noted now, used when needed.

## Exercises

1. Rebuild the quotes crawler with `requests.Session`, retries on 429/5xx, and a `max_pages` parameter.
2. Crawl two pages of quotes; output a pandas profile: quotes per author, top 5 tags, avg words per quote.
3. Download any public PDF report; extract text, count characters per page, and write the cleaned text to JSONL with page numbers as metadata.
4. Convert `data/corpus.jsonl` to CSV and back; find one field where information is lost and explain why.
5. Write `crawl_sitemap(start_url)`: parse `<loc>` URLs from a sitemap XML and fetch each (respecting robots.txt).

## Pitfalls

- **Default encoding on Windows** — explicit `encoding="utf-8"` everywhere
- **429s ignored** — add backoff or you get IP-banned
- **HTML parsing with regex** — use BeautifulSoup
- **PDF extraction hallucination** — always diff `extract_text()` output against the visual page
- **Deep-copied requests without caching** — crawl once, store raw HTML, parse offline

## Resources

- [requests docs](https://requests.readthedocs.io) · [Beautiful Soup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [pandas IO tools](https://pandas.pydata.org/docs/user_guide/io.html)
- MDN: [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- robots.txt spec + Google's crawler etiquette guide
- `quotes.toscrape.com` / `books.toscrape.com` — legal sandboxes built for scraping practice
