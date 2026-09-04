# 02.4 — Regex Fundamentals

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

---

## What you'll learn

- The pattern grammar: atoms, quantifiers, groups, anchors, lookarounds
- The four `re` functions and the match-object API
- Compilation flags and verbose patterns
- Testing regexes: property discipline and failure classification

## 1. Atoms and quantifiers (tested, not memorized)

```python
import re

tests = {
    r"\d+":            ["abc123", "12", "", "a1b2"],       # digit runs
    r"\w+@\w+\.\w+":   ["a@b.co", "a@b"],                  # naive email
    r"colou?r":        ["color", "colour", "colr"],
    r"^start":         ["start here", "the start"],        # ^ anchors: 2nd fails
    r"end$":           ["the end", "the end."],            # $ : 2nd fails
}
for pat, samples in tests.items():
    for s in samples:
        m = re.search(pat, s)
        print(f"{pat!r:22} {s!r:16} -> {m.group(0) if m else None}")
```

Quantifiers and greediness — the classic trap:

```python
re.findall(r"<.*>", "<a><b>")     # ['<a><b>']  greedy eats everything
re.findall(r"<.*?>", "<a><b>")    # ['<a>', '<b>']  lazy stops at first close
```

**Rule:** default to lazy (`*?`, `+?`) when the terminator can repeat; test both on real data.

## 2. Groups: capture, non-capture, named

```python
m = re.search(r"(?P<user>[\w.+-]+)@(?P<host>[\w-]+\.[\w.]+)", "ops@acme.com")
m.group("user"), m.group("host")           # named groups — self-documenting

re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\2/\1/\3", "2026-11-05")   # '11/2026/05'
```

- Named groups (`?P<name>`) — use in any pattern someone else will read
- `re.sub` replacement strings can reference groups: `\1`, `\g<name>`
- **Backreferences** `\1` inside the pattern match repeated text (find doubled words: `\b(\w+)\s+\1\b`)

## 3. Lookarounds (zero-width assertions)

```python
re.findall(r"\d+(?= days)", "5 days, 30 days")            # ['5', '30'] — no 'days' in match
re.findall(r"\b(?!for)\w+ed\b", "signed for walked")       # not 'for'-ed words
re.split(r"(?<=\.)\s+", "A. B. C.")                        # split after periods
```

Lookaheads/behinds match *positions*, consume nothing — the tool for split-after and context-checking without capturing. `(?<=\.)` is the "sentence-aware split" from W1-02's chunking.

## 4. The four functions, decision table

| Function | Returns | Use when |
|---|---|---|
| `search` | first `Match` or None | default choice |
| `match` | Match at position 0 only | explicit start-anchoring |
| `fullmatch` | Match only if ENTIRE string matches | validation |
| `findall`/`finditer` | all matches (str list / Match iter) | extraction |

Plus `re.split`, `re.sub`, `re.escape` (wrap user input as literal — W1-02's pitfall).

## 5. Flags and verbose patterns

```python
EMAIL_RE = re.compile(r"""
    [\w.+-]+        # local part
    @
    [\w-]+          # domain label
    (?:\.[\w-]+)+   # dot-separated TLDs
""", re.VERBOSE | re.IGNORECASE)

# multiline: ^ $ match per line — needed for line-based cleaning
MULTI = re.compile(r"^\s*#.*$", re.MULTILINE)      # comment lines
MULTI.sub("", config_text)
```

Flags to know: `IGNORECASE`, `MULTILINE` (`^`/`$` per line), `DOTALL` (`.` matches newlines), `UNICODE` (default in py3).

## 6. Testing regexes (property-style)

```python
import re

def valid_phone(s): return re.fullmatch(r"\+91[- ]?\d{5}[- ]?\d{5}", s) is not None

assert valid_phone("+91 98765 43210")
assert not valid_phone("98765") and not valid_phone("+91-98765432101")   # wrong digit count
# adversarial: leading zeros, +91 duplicated, letters — each = one test
```

Regexes are code: test happy paths, boundaries (empty, max length), and adversarial inputs. Keep patterns in named constants with a docstring.

## Exercises

1. Write `extract_dates(text)` matching `2026-11-05`, `05/11/2026`, `5 Nov 2026` — return ISO format; test 15 inputs including invalid ones.
2. Doubled-word finder: `re.findall(r"\b(\w+)\s+\1\b", text, re.I)` over a real document — report true duplicates vs false positives (case, punctuation).
3. Catastrophic-backtracking demo: run `(a+)+$` against `"a"×30 + "!"` — time it; then fix with an atomic-group equivalent or possessive logic.
4. Template tokenizer: split `"Hello {name}, you owe {amount}"` into literal/placeholder segments — the W3-01 render-validation primitive.
5. Password validator: one regex enforcing length ≥ 12, upper+lower+digit+symbol, no repeated 3-char runs — then argue why multi-pass validators are clearer.

## Pitfalls

- **Greedy by default** — `.*` to the *last* match; lazy `.*?` or character-class negation
- **Backtracking blowup** — nested quantifiers over ambiguous classes; keep patterns deterministic
- **`re.match` ≠ full validation** — use `fullmatch` for validators
- **Forgetting `re.escape`** — user input with `.`/`+`/`(` injects regex syntax
- **Over-precise patterns** — validation regexes that reject valid real-world data (international phones!); validate shape, not the world

## Resources

- [re module HOWTO](https://docs.python.org/3/howto/regex.html) — the canonical tutorial
- [regex101](https://regex101.com/) — live debugging (Python flavor)
- W1-02 parent, W1-04 (parsers vs regex), W2-02 (PII extraction consumer) — composed here
