# 02.1 — String Methods Lab

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

---

## What you'll learn

- The string operations used daily in text pipelines, with their exact edge-case behavior
- Splitting/joining patterns for corpora, logs, and transcripts
- Efficient string building (and why `+=` in loops is a smell)

## 1. Core operations and their edge cases

```python
s = "  Large Language Models  "

s.strip()                # 'Large Language Models' — strips BOTH ends, whitespace only
s.split()                # ['Large', 'Language', 'Models'] — runs of whitespace collapse
s.split(" ")             # ['', '', 'Large', '', 'Language', ...] — explicit sep KEEPS empties!
"a,b,,c".split(",")      # ['a', 'b', '', 'c'] — empty field preserved
"line1\nline2".splitlines()  # ['line1', 'line2'] — handles \r\n too
" ".join(["a", "", "b"]) # 'a  b' — empty strings still contribute
```

The `split()` vs `split(" ")` difference is the #1 beginner surprise: **no-arg split collapses whitespace; explicit separators preserve empties.**

Case and comparison traps:

```python
"I".lower()                     # 'i' — fine
"İ".lower()                     # 'i̇' — TWO code points (Turkish dotted I)!
"ß".upper()                     # 'SS' — length changes under case folding
"café".casefold() == "cafe"     # False — casefold ≠ lower (see file 03)
```

Rule for pipelines: use `.casefold()` for comparison, `.lower()` for display — they differ on ß, İ, and a few others.

## 2. Membership, replace, and finding

```python
s = "refund timeline: 5 business days"
s.find("timeline")            # 7 — first index, -1 if absent
s.replace("5", "five")        # new string (immutability!)
s.count("e")                  # 4
s.removeprefix("refund ")      # 'timeline: 5 business days' (3.9+)
s.removesuffix("days")        # 'refund timeline: 5 business '
```

- `find` vs `index`: `find` returns −1; `index` raises. In pipelines, prefer `find` + explicit check
- `replace` replaces **all** occurrences; pass a count to limit: `s.replace(" ", "_", 1)`
- **Immutability** means loops that "modify" `s` create garbage — build lists and `join` instead

## 3. Building text efficiently

```python
# WRONG: quadratic behavior on large corpora
text = ""
for line in lines: text += line + "\n"

# RIGHT: join once
text = "\n".join(lines)

# streaming-friendly: write incrementally to a file (W1-04)
```

Benchmark it: 100k lines — `+=` is O(n²) due to reallocation; `join` is linear. The difference is seconds vs minutes.

## 4. Common pipeline patterns

```python
# normalize + filter a log
lines = [ln.strip() for ln in raw.splitlines()]
lines = [ln for ln in lines if ln and not ln.startswith("#")]

# word frequency with case-insensitivity
from collections import Counter
Counter(w.casefold() for w in text.split()).most_common(10)

# fixed-width formatting for tables
for i, name in enumerate(names, 1):
    print(f"{i:>3}. {name:<20} {scores[i-1]:>8.2f}")
```

## Exercises

1. Write `clean_line(line)`: strip, collapse internal whitespace to single spaces, drop empty — then run it over a 1000-line log and report dropped/kept counts.
2. Split `"a=b;c=d,,e=f"` on `,` and `;` into a dict, preserving empty values as `None` — handle the missing-`=` case.
3. Implement `truncate(s, n, suffix="…")` that never breaks words: cut at the last space before the limit.
4. Build a word-frequency table for a real document with casefold + regex tokenization (file 04); compare against naive `.split()` counts.
5. Benchmark string building: `+=` vs join vs `io.StringIO` on 100k lines — report times.

## Pitfalls

- **`split()` on user input with tabs/newlines** — collapses everything; use explicit separators when structure matters
- **Modifying while iterating** — build a new list instead
- **`.strip()` only strips whitespace** — pass the character set for quotes/brackets: `s.strip('"')`
- **Assuming `lower()` fixes all case issues** — casefold for comparison, lower for display
- **String concatenation in loops over corpora** — quadratic behavior; join or stream

## Resources

- Python [str method reference](https://docs.python.org/3/library/stdtypes.html#string-methods)
- W1-02 parent, W16-02 (string-driven data generation) — the consumers of these patterns
