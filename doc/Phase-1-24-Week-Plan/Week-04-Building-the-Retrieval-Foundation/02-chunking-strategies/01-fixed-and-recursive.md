# 02.1 — Fixed & Recursive Chunking

> Subfolder index: [README.md](README.md) · Parent: [../02-chunking-strategies.md](../02-chunking-strategies.md)

---

## What you'll learn

- Fixed-size chunking with overlap — the math and the boundary failures
- Recursive splitting — the separator hierarchy and its tuning
- The boundary-quality comparison between the two

## 1. Fixed-size with overlap — the math

```python
def chunk_fixed(text: str, size: int = 512, overlap: int = 64) -> list[str]:
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]
```

The arithmetic that matters:

| Size | Overlap | Step | Chunks per 5000 chars | Boundary loss |
|---|---|---|---|---|
| 512 | 64 | 448 | 12 | ~64 chars duplicated per boundary |
| 512 | 0 | 512 | 10 | 0 duplicated, 512 lost per boundary |
| 512 | 256 | 256 | 19 | 256 duplicated — heavy redundancy |

The overlap trade: more overlap = fewer lost sentences at boundaries, but more duplicated content in the index (storage + retrieval noise). The parent's rule: **overlap > size is an infinite loop** — enforce `step ≥ 1`.

## 2. The boundary failures (see them, don't imagine them)

```python
chunks = chunk_fixed("The refund window is 5 business days. After approval, "
                     "funds arrive within 24 hours.", size=40, overlap=0)
# chunk 1 ends: "...refund window is 5 business"
# chunk 2 starts: "days. After approval..."
# → the ANSWER ("5 business days") is split across both chunks
```

Retrieval finds chunk 2 ("days. After approval") — no "refund window" context. The answer is technically present but semantically incomplete. This is the failure fixed by recursive splitting and overlap.

## 3. Recursive splitting — the hierarchy

```python
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

def chunk_recursive(text: str, size: int, seps=None) -> list[str]:
    seps = seps or SEPARATORS
    if len(text) <= size:
        return [text]
    for sep in seps:
        if sep in text:
            parts = text.split(sep)
            break
    else:
        return [text[:size]]                      # hard cut, no separator found
    # greedy pack parts into chunks ≤ size
    chunks, cur = [], ""
    for p in parts:
        piece = (sep + p) if cur else p           # restore the separator
        if len(cur) + len(piece) > size and cur:
            chunks.append(cur); cur = piece
        else:
            cur += piece
    if cur: chunks.append(cur)
    return chunks
```

The hierarchy: try the strongest separator first (paragraphs); if a piece is still too big, recurse with the next separator. The result: chunks break at *natural* boundaries wherever possible.

## 4. The comparison (boundary quality, eyeballed)

| Strategy | Boundary at | Boundary quality |
|---|---|---|
| fixed-512 | mid-sentence, mid-word | poor — fragments |
| recursive-512 | sentence or paragraph ends | good |
| recursive + structure | header boundaries | best |

The eyeball check (file W1-04's discipline): read 5 chunk boundaries per strategy — the differences are immediately visible.

## Exercises

1. The boundary census: for 10 documents, count how many chunk boundaries fall mid-sentence per strategy — the table that quantifies §2.
2. The overlap sweep: overlap ∈ {0, 64, 128} at size 512 — measure boundary-content duplication and retrieval impact.
3. The separator audit: for your corpus, which separator hierarchy produces the fewest mid-sentence cuts? (Try adding "—", ";", ": ".)
4. The minimum-viable test: what's the smallest `size` where every chunk still contains at least one complete sentence? (The readability floor.)
5. Edge cases: empty text, single giant word, text exactly = size — each handled without crashing.

## Pitfalls

- **Separator not restored** — splitting on "\n\n" and joining without it loses paragraph breaks
- **Overlap computed as `size - step` when step < overlap** — infinite loop; enforce `step ≥ 1`
- **Chunks with only whitespace** — filter after chunking, not before (or you'll re-index stale chunks)
- **The last chunk smaller than `min_size`** — merge it into the previous chunk or flag it
- **Assuming the corpus has paragraph structure** — scraped text may have no "\n\n" at all; the hierarchy falls through to sentences

## Resources

- W4-02 parent (the strategies), W4-05 (the pipeline consuming them), W16-02 (the eval that measures them) — composed here
- LangChain [text splitters](https://python.langchain.com/docs/how_to/#text-splitters) — the production implementations
- Chroma, *Evaluating chunking strategies* — the metrics-first approach file 03 applies
