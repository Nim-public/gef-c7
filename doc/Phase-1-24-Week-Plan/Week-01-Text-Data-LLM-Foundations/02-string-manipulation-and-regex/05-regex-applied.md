# 02.5 — Regex Applied: Extraction, Cleaning & Chunking

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

---

## What you'll learn

- Production extraction patterns: invoices, PII, structured fields — with verification
- A composable text-cleaning pipeline (the corpus-ingestion primitive for W4)
- Sentence-aware chunking (the W4-02 primitive)
- The extraction-verification pattern: every extraction asserts its own correctness

## 1. The invoice extractor (worked example)

```python
import re

INVOICE_PATTERNS = {
    "invoice_no": re.compile(r"Invoice\s*#\s*([A-Z]{2,4}-\d{3,6})", re.I),
    "date":       re.compile(r"Date:\s*(\d{1,2}\s+\w+\s+\d{4})", re.I),
    "email":      re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "total":      re.compile(r"Total:?\s*₹?\s*([\d,]+\.\d{2})"),
}

def extract_invoice(text: str) -> dict:
    out = {}
    for field, pat in INVOICE_PATTERNS.items():
        m = pat.search(text)
        out[field] = m.group(1) if m else None      # explicit None, never invented
    return out
```

Design rules (from the parent file): named constants, explicit `None` (the model/pipeline never invents), one pattern per field, patterns compiled once at module level.

### The verification step (extraction asserts itself)

```python
def verify_extraction(text: str, fields: dict) -> list[str]:
    issues = []
    if fields["total"]:
        if float(fields["total"].replace(",", "")) <= 0:
            issues.append("total not positive")
        if fields["total"].replace(",", "").replace(".", "") not in text.replace(",", "").replace(".", ""):
            issues.append("total digits not found verbatim in source")
    if fields["invoice_no"] and not text.lower().count("invoice"):
        issues.append("no 'invoice' keyword though number extracted")
    return issues
```

The verbatim-digit check is the W12-04 `numbers_supported` pattern in miniature: **extracted values must exist in the source text** — the defense against extraction hallucination (whether from regex or an LLM).

## 2. The PII scrubber (composed from W2-02/W10-02 usage)

```python
PII_PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("PHONE", re.compile(r"(?:\+91[- ]?)?\d{5}[- ]?\d{5}")),
    ("CARD",  re.compile(r"\b(?:\d[ -]?){13,16}\b")),
    ("IFSC",  re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")),
]

def scrub_pii(text: str) -> str:
    for tag, pat in PII_PATTERNS:
        text = pat.sub(f"[{tag}]", text)
    return text
```

Test it against synthetic PII (never real), including the tricky cases: emails in signatures, phone numbers with country codes, card numbers with spaces. This function is consumed by W5-04's intake guardrails and W19-01's file tools.

## 3. The text-cleaning pipeline (composable stages)

```python
def clean_for_corpus(text: str) -> str:
    text = scrub_headers(text)         # page numbers, repeated headers (file-specific)
    text = collapse_whitespace(text)   # W1-02
    text = fix_hyphenation(text)       # "doc-\nument" -> "document"
    text = normalize_quotes(text)      # smart quotes -> ascii (policy!)
    return text

def fix_hyphenation(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)     # de-hyphenate line-broken words
```

Order matters and must be **tested on real pages** (W1-04's eyeball rule): de-hyphenation before whitespace collapse; header scrubbing before everything (page numbers pollute chunk boundaries).

## 4. Sentence-aware chunking (the W4-02 primitive)

```python
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")
PARA_SPLIT = re.compile(r"\n\s*\n")

def chunk_by_sentences(text: str, target_chars: int = 600) -> list[str]:
    chunks, current = [], ""
    for para in PARA_SPLIT.split(text):
        for sent in SENT_SPLIT.split(para):
            if len(current) + len(sent) > target_chars and current:
                chunks.append(current.strip()); current = ""
            current += sent + " "
        current += "\n\n"
    return [c.strip() for c in chunks if c.strip()]
```

Properties: never breaks mid-sentence, respects paragraph boundaries where possible, deterministic. This is the fallback chunker for W4-02's recursive strategy — same contract (`list[str]`), zero dependencies.

## 5. Pattern library discipline

- Patterns live in **one module** with docstrings and tests (`patterns.py`)
- Each pattern: name, what it matches, what it deliberately doesn't, 3 example matches + 2 non-matches
- Compile at import; never recompile in loops
- Track *which version* of a pattern produced which extraction (W16-01's versioning, pattern edition)

## Exercises

1. Build `extract_invoice` + `verify_extraction` on 5 synthetic invoices; inject 3 corruptions (wrong total digits, missing date) and confirm verification catches each.
2. Extend `scrub_pii` with Aadhaar (`\d{4} \d{4} \d{4}`) and PAN (`[A-Z]{5}\d{4}[A-Z]`) — test on 10 synthetic strings, including near-misses (PAN-like license plates).
3. Write `fix_hyphenation` test cases: "docu-\nment", "well-\nknown" (keep the hyphen!), "3-\n4" (ranges) — handle the ambiguity explicitly.
4. Compare `chunk_by_sentences` against the W4-02 recursive splitter on the same document: chunk counts, boundary quality (eyeball 5), retrieval hit-rate on 10 questions.
5. Benchmark the pipeline: 1MB of scraped text through `clean_for_corpus` + chunking — tokens/s; profile the regex hot spots.

## Pitfalls

- **Extraction without verification** — a wrong total extracted confidently is worse than no extraction (the §1 pattern exists for this)
- **Case-sensitivity surprises** — "INVOICE", "Invoice", "invoice" in the wild; use `re.I` deliberately
- **Over-eager PII scrubbing** — scrubbing ticket IDs that look like phones breaks lookups; test downstream flows after scrubbing (W5-04's counter-metric)
- **Cleaning order bugs** — de-hyphenating after whitespace collapse destroys the `\n` anchor the pattern needs
- **Anchors in MULTILINE vs not** — `^` semantics change; the page-number scrubber needs `re.M` to catch mid-document lines

## Resources

- W1-02 parent (grammar), W4-02 (chunk consumer), W12-04 (verification origin) — composed here
- [regex101](https://regex101.com/) — pattern debugging (Python flavor)
- [presidio](https://microsoft.github.io/presidio/) — the production PII framework (graduate from regex when needed)
