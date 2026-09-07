# 04.3 — Web Crawling

> Subfolder index: [README.md](README.md) · Parent: [../04-file-handling-and-web-crawling.md](../04-file-handling-and-web-crawling.md)

---

## What you'll learn

- The crawl loop with production hardening: sessions, retries with backoff, politeness
- Parsing with BeautifulSoup selectors
- Content extraction strategy: full-page text vs structured fields
- Robots/ToS/ethics as engineering constraints (not vibes)

## 1. The hardened fetcher

```python
import time, random, requests

UA = {"User-Agent": "GEF-C7-study-bot/1.0 (educational; contact@example.com)"}
RETRYABLE = {429, 500, 502, 503, 504}

def fetch(session: requests.Session, url: str, tries: int = 4) -> str:
    for attempt in range(tries):
        resp = session.get(url, headers=UA, timeout=15)
        if resp.status_code == 200:
            return resp.text
        if resp.status_code in RETRYABLE and attempt < tries - 1:
            delay = min(2 ** attempt + random.random(), 30)
            time.sleep(delay)                       # exponential backoff + jitter
            continue
        resp.raise_for_status()
    raise RuntimeError(f"unreachable after {tries} tries: {url}")
```

Rules embodied: a **Session** (connection reuse + cookie continuity), exponential backoff **with jitter** (avoid thundering herds), only retrying the retryable classes, `raise_for_status` so failures are explicit (W15-01's error contracts).

## 2. Politeness as configuration

| Rule | Implementation |
|---|---|
| check `robots.txt` | `urllib.robotparser` — `can_fetch(UA, url)` before every fetch |
| rate limit | `time.sleep(1 + random())` between requests to the same host |
| honor crawl-delay | read `Crawl-delay:` from robots.txt, use as the minimum sleep |
| identify honestly | descriptive User-Agent with contact info |
| cache raw HTML | never fetch the same URL twice (persist to disk keyed by hash) |

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser("https://example.com/robots.txt"); rp.read()
assert rp.can_fetch(UA["User-Agent"], url), "disallowed by robots.txt"
```

The crawling ethics from W1-04, restated as code: politeness rules are **preconditions**, not suggestions — a crawler that ignores them gets your IP banned and your project named.

## 3. Parsing with BeautifulSoup

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
soup("script, style, nav, footer").decompose()      # strip noise FIRST

for card in soup.select("div.quote"):
    text = card.select_one("span.text").get_text(strip=True)
    author = card.select_one("small.author").get_text(strip=True)
    tags = [a.get_text(strip=True) for a in card.select("a.tag")]
```

Selector patterns: `select` (CSS), `select_one`, `get_text(strip=True)`, `decompose()` for noise removal. Strip scripts/styles/nav **before** text extraction — boilerplate is the biggest quality leak in scraped corpora.

## 4. Content extraction strategy

| Need | Approach |
|---|---|
| main article text | find the content container (`article`, `#content`) or largest text block heuristic |
| structured fields | targeted selectors per site |
| everything readable | `soup.get_text(separator=" ")` after noise removal — then clean (W1-02) |
| link discovery | `soup.select("a[href]")` + URL normalization (`urljoin`) |

The `urljoin(base, href)` pattern matters for relative links — the classic pagination bug (E5-02's quotes crawler uses it).

## 5. The crawl loop (pagination + dedup + persistence)

```python
import hashlib, json
from pathlib import Path
from urllib.parse import urljoin

def crawl(start: str, out: Path, max_pages: int = 50):
    seen, done = {start}, 0
    out.mkdir(exist_ok=True)
    queue = [start]
    while queue and done < max_pages:
        url = queue.pop(0)
        html = fetch(session, url)                      # §1
        (out / f"{hashlib.sha1(url.encode()).hexdigest()}.html").write_text(html, encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href]"):
            nxt = urljoin(url, a.get("href"))
            if nxt.startswith(start) and nxt not in seen:      # same-site only
                seen.add(nxt); queue.append(nxt)
        done += 1
        time.sleep(1 + random.random())
```

Properties: content-addressed storage (hash-keyed files), same-site scoping, bounded pages, dedup via `seen`, raw HTML persisted for offline re-parsing (W1-04's rule). This is the E3-02 web-agent's fetch layer, minus the agent.

## Exercises

1. Build the hardened fetcher; test against a 429-returning endpoint (or a local mock) — verify backoff timing and eventual success.
2. Politeness audit: write the robots.txt compliance check and run it against 5 sites; log which disallow your UA.
3. Boilerplate ablation: extract text with and without script/style/nav removal — compare token counts and RAG-relevant content ratio (W4's chunker on both).
4. Same-site scope drill: craft an external link (or find one) — verify the `startswith` scope excludes it; then attempt the classic open-redirect trick (`/redirect?url=...`) and discuss.
5. Raw-cache replay: crawl 20 pages; then re-run the parse step with zero network — the offline replay that makes debugging cheap (W1-04's rule).

## Pitfalls

- **Crawling without caching** — every debug iteration re-hits the site; fetch once, parse forever
- **Infinite same-site loops** — calendar pages with `?page=N` forever; bound by max_pages AND URL normalization (strip fragments/params)
- **Parsing across encoding boundaries** — `resp.encoding` may misguess; set it from `resp.apparent_encoding` when the charset meta is missing
- **JS-rendered sites** — requests gets pre-JS HTML; Playwright tier (E3-02) only when content is truly dynamic
- **Legal certainty assumptions** — robots.txt compliance ≠ license to republish; separate fetching from redistribution rights (W1-04)

## Resources

- [requests docs](https://requests.readthedocs.io/) · [Beautiful Soup docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) · [urllib.robotparser](https://docs.python.org/3/library/urllib.robotparser.html)
- W1-04 parent, E3-02 (browser agents), W10-02 (tool result formatting) — composed here
