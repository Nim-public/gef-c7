# 02.3 — Unicode & Normalization

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

---

## What you'll learn

- Code points vs bytes vs grapheme clusters — three different "lengths"
- The four normalization forms and when each applies
- The pipeline bugs: NFKC policy, zero-width characters, confusables, RTL
- Building a Unicode-safe cleaner with tests

## 1. Three lengths for one string

```python
s = "école"                       # 'e' + combining accent (2 code points)
len(s)                             # 2 code points
len(s.encode("utf-8"))             # 6 bytes
import unicodedata
len(unicodedata.normalize("NFC", s))   # 1 code point (precomposed é)
```

Add **grapheme clusters** (what users perceive as characters) and you have three answers to "how long is this string?". Tokenizers add a fourth (tokens). When budgets and limits collide, know which count each layer uses (file 01.5).

## 2. Normalization forms

| Form | Effect | Use |
|---|---|---|
| **NFC** | compose accents (é = e + ◌́ → é) | default for text exchange |
| **NFD** | decompose accents | some search/index systems |
| **NFKC** | NFC + compatibility (ﬁ→fi, ①→1, ²→2) | cleaning pipelines |
| **NFKD** | NFD + compatibility | strip-diacritics recipes |

```python
import unicodedata
unicodedata.normalize("NFKC", "ﬁnance")     # 'finance'
unicodedata.normalize("NFKC", "①")          # '1'
unicodedata.normalize("NFC", "cafe\u0301") == "café"   # True
```

**Policy rule:** pick ONE form at ingestion, apply to everything, document it. Mixed forms break equality checks, dedup, and search — silently.

## 3. The invisible characters that break pipelines

```python
invisible = {
    "\u00a0": "non-breaking space",
    "\u200b": "zero-width space",
    "\u200e": "left-to-right mark",
    "\ufeff": "BOM / zero-width no-break space",
    "\u202e": "right-to-left override (spoofing!)",
}
for ch, name in invisible.items():
    print(repr(ch), name, "| visible:", ch.isprintable())
```

- **ZWSP/ZWNJ** inside words split tokens invisibly — `"ref\u200bund"` ≠ `"refund"`
- **RTL override (U+202E)** can make code look reversed — a real attack vector in code review (E3-01's `security_review` node flags it)
- **BOM** at file start breaks naive `json.loads` — strip with `encoding="utf-8-sig"` on read

## 4. Confusables and spoofing

```python
from unicodedata import normalize
"ΑВСЕ" == "АBCE"          # False! — the first uses GREEK/CYRILLIC lookalikes
# defense: NFKC + confusables screening for identifiers, domains, tickers
```

Homoglyph attacks matter for: tickers in financial extraction (W12-04), domain names in crawled text (W1-04), user identifiers (E9 memory keys). The `confusable-homoglyphs` package screens for them.

## 5. The Unicode-safe cleaner (reference implementation)

```python
import re, unicodedata

INVISIBLES = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u200e\u202a\u202c\u202e\ufeff"), None)

def clean_unicode(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(INVISIBLES)                    # strip zero-width/invisible
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

# tests (write these FIRST — file 02-01's discipline):
assert clean_unicode("café\u00a0") == "café"
assert clean_unicode("ref\u200bund") == "refund"
assert "ﬁ" not in clean_unicode("ﬁnance")
```

## Exercises

1. Length census: for 10 strings (emoji ZWJ, accents, CJK), report code points / UTF-8 bytes / grapheme clusters (via the `grapheme` package). Table the ratios.
2. Normalization A/B: index a corpus with NFC vs without (W4's `CountVectorizer`); find queries whose recall differs.
3. Invisible-character hunt: scan 50 scraped pages (W1-04) for §3's invisibles; report per-page counts. Which sites are worst?
4. Confusable screening: check 20 extracted tickers/domains against the confusables list; flag the spoofing candidates.
5. Property-based tests: use `hypothesis` to generate random Unicode strings and assert `clean_unicode` invariants (no invisibles, NFC, no double spaces).

## Pitfalls

- **`len()` ≠ user-perceived length** — counts code points; graphemes need the `grapheme` package (matters for truncation UX)
- **Encoding errors as "replace"** — `errors="replace"` inserts `?`/`\ufffd` silently; decode with explicit policy and log
- **NFKC expanding things you meant to keep** — e.g., "㎡" → "m2"; review what compatibility decomposition does to your domain glyphs
- **BOM in concatenated files** — `\ufeff` mid-file after naive merging; strip at read
- **RTL override in scraped content** — U+202E can reverse display order of your UI text; strip invisibles before rendering

## Resources

- [Unicode Standard Annex #15](https://unicode.org/reports/tr15/) — normalization forms
- Python [unicodedata](https://docs.python.org/3/library/unicodedata.html) · [codecs](https://docs.python.org/3/library/codecs.html)
- [confusable-homoglyphs](https://pypi.org/project/confusable-homoglyphs/) · [grapheme](https://pypi.org/project/grapheme/)
- W1-02 parent, W1-04 (BOM/BOM-in-merge), W19-01 (RTL in code review) — composed here
