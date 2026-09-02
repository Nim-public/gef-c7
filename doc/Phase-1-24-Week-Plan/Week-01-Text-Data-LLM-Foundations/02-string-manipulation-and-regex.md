# 02 — String Manipulation, f-strings & Regex

> Week 1 index: [README.md](README.md)

**Session 1 topic:** *string manipulation* — the layer you touch every single day: cleaning scraped text, normalizing corpora, extracting fields, and building prompts.

---

## What you'll learn

- Python string essentials you'll use constantly in LLM pipelines
- f-strings as the foundation of prompt templating
- Unicode realities that break NLP pipelines silently
- Regex for extraction, cleaning, and validation

## 1. String essentials

Strings are immutable — every "modification" returns a new string.

```python
s = "  Large Language Models  "

s.strip()            # 'Large Language Models'
s.lower()            # '  large language models  '
s.replace(" ", "_")  # '__Large_Language_Models__'
s.split()            # ['Large', 'Language', 'Models']
"-".join(["a", "b"]) # 'a-b'
s.startswith("  L")  # True
"LM" in s            # True
s[2:7]               # 'Large' — slicing
len(s)               # 23
```

The workhorses for corpora:

```python
words = "the cat sat on the mat".split()
from collections import Counter
Counter(words).most_common(3)   # [('the', 2), ('cat', 1), ('sat', 1)]

" ".join(msg for msg in chat_log if msg.strip())   # rebuild text from lines
```

## 2. f-strings: prompt templating foundation

Prompt engineering (Week 3) is mostly f-strings or templates over f-string syntax. Master it now:

```python
topic = "RAG"
n_words = 120
style = "beginner-friendly"

prompt = (
    f"Explain {topic} in about {n_words} words.\n"
    f"Audience: {style}.\n"
    f"End with one concrete example."
)
```

Formatting power you'll need for logs and tables:

```python
pi = 3.14159265
f"{pi:.2f}"            # '3.14'
n = 1_250_000
f"{n:,}"               # '1,250,000'
f"{n:,} tokens"        # '1,250,000 tokens'
for i, w in enumerate(["a", "b"]):
    print(f"{i:>2}. {w}")
```

Prompt templates usually become functions that return f-strings:

```python
def summarize_prompt(text, max_sentences=3):
    return f"Summarize the following text in {max_sentences} sentences:\n\n{text}"
```

(Week 14 replaces raw f-strings with LangChain `PromptTemplate`s — same idea, extra features.)

## 3. Unicode: the silent pipeline killer

Real text is Unicode. Three facts that matter:

```python
s = "café"                      # 4 characters
len(s)                          # 4
s.encode("utf-8")               # b'caf\xc3\xa9' — 5 bytes
len(s.encode("utf-8"))          # 5 — bytes ≠ characters

"ﬁ" == "fi"                     # False — ligature vs two letters!
import unicodedata
unicodedata.normalize("NFKC", "ﬁ") == "fi"   # True
```

1. **UTF-8 byte length ≠ character count** — tokenizers and APIs count differently.
2. **Normalization matters**: `NFC` composes accents, `NFKC` also expands ligatures/compat forms. Normalize corpora consistently.
3. **Always open files with `encoding="utf-8"`** — Windows default encodings have bitten every developer at least once.

A standard first-pass cleaner for LLM corpora:

```python
import re
import unicodedata

def clean_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00a0", " ")                  # non-breaking space
    s = re.sub(r"[ \t]+", " ", s)                 # collapse runs of spaces
    s = re.sub(r"\n{3,}", "\n\n", s)              # collapse blank lines
    return s.strip()
```

## 4. Regex (`re`)

Regex = pattern language for "find/extract/replace strings matching a shape."

### Core building blocks

| Pattern | Matches |
|---|---|
| `\d` `\w` `\s` | digit / word char / whitespace |
| `.` | any char except newline |
| `[abc]`, `[^abc]` | set / negated set |
| `*` `+` `?` `{2,4}` | repetition: 0+, 1+, optional, 2–4 |
| `^` `$` | start / end of string (or line) |
| `(...)` | capture group |
| `(?:...)` | non-capturing group |
| `a\|b` | alternation |
| `(?=...)` `(?!...)` | lookahead / negative lookahead |

### The four `re` functions you need

```python
import re

re.search(r"\d{4}", "batch 2024 done")     # first match or None
re.findall(r"\d+", "a1 b22 c333")          # all matches: ['1','22','333']
re.sub(r"\s+", " ", "too   many")          # replace: 'too many'
re.match(r"^\w+@\w+\.\w+$", email)         # anchored match from start
```

### Worked examples

**Extract structured fields from messy text:**

```python
invoice = """Invoice #INV-2024-099
Date: 05 Sep 2024
Email: ops@acme-corp.com
Total: $1,250.00"""

invoice_no = re.search(r"Invoice #([\w-]+)", invoice).group(1)
date       = re.search(r"Date:\s*(.+)", invoice).group(1)
email      = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", invoice).group(0)
total      = re.search(r"\$([\d,]+\.\d{2})", invoice).group(1)
```

**Clean scraped HTML-ish text:**

```python
raw = "Price:   $9.99     (was   $19.99)   !!!"
re.sub(r"\s+", " ", raw)                 # collapse whitespace
re.sub(r"!{2,}", "!", raw)               # clamp punctuation
re.findall(r"\$\d+\.\d{2}", raw)         # ['$9.99', '$19.99']
```

**Split text into paragraph/word chunks (tiny taste of Week 4 chunking):**

```python
paragraphs = re.split(r"\n\s*\n", doc)
sentences  = re.split(r"(?<=[.!?])\s+", paragraph)   # split after punctuation
```

**Validate before sending to an LLM** (cheap guardrail before expensive calls):

```python
def looks_like_email(s): return re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", s) is not None
```

### Tips

- Test patterns interactively at [regex101.com](https://regex101.com) (set the *Python* flavor)
- Compile patterns you reuse: `EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")`
- Prefer verbose mode for complex patterns: `re.compile(r"""...\s+  # spaces""", re.VERBOSE)`
- Don't regex HTML structure — use BeautifulSoup (file 04); regex is for text shapes

## Exercises

1. Write `normalize_phone(s)` returning `+91XXXXXXXXXX` from `+91 98765 43210`, `09876543210`, `98765-43210`.
2. From a block of text, extract all URLs, all `@handles`, and all hashtags into three lists.
3. Write `clean_text()` above, then deliberately break it: feed it `"ﬁnance café \u00a0 x"` and verify the output.
4. Build `render_prompt(template: str, **vars)` that substitutes `{name}` placeholders — then explain why `str.format_map` with a `defaultdict` is the one-line version.
5. Split a multipage text into ~500-character chunks that never break mid-sentence.

## Pitfalls

- **Greedy quantifiers**: `re.search(r"<.*>", "<a><b>")` eats everything; use `.*?` (lazy).
- **Catastrophic backtracking** on nested quantifiers like `(a+)+$` — hangs the process.
- **Regex for HTML/JSON parsing** — wrong tool; use parsers.
- **`re.match` vs `re.search`** — `match` anchors at start; most bugs are using the wrong one.
- **Forgetting `re.escape()`** when interpolating user input into a pattern.

## Resources

- Python docs: [re — Regular expression operations](https://docs.python.org/3/library/re.html) and the HOWTO
- [regex101.com](https://regex101.com) — live pattern debugger
- [f-string reference](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals)
- Hartley & Leroux, *Text Processing in Python* (concepts still apply)
