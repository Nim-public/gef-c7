# 02.2 — Structure-Aware Chunking

> Subfolder index: [README.md](README.md) · Parent: [../02-chunking-strategies.md](../02-chunking-strategies.md)

---

## What you'll learn

- Markdown/HTML header-aware chunking with section-path metadata
- Table, code, and Q&A special cases
- The serialization rules that keep structure intact

## 1. Header-aware chunking

```python
import re

def chunk_by_headers(text: str) -> list[dict]:
    """Split markdown by ## headers; carry the section path."""
    sections = []
    current_path, current = [], []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if current:
                sections.append({"path": list(current_path), "text": "\n".join(current)})
            depth = len(m.group(1))
            current_path = current_path[:depth - 1] + [m.group(2)]
            current = []
        else:
            current.append(line)
    if current:
        sections.append({"path": list(current_path), "text": "\n".join(current)})
    return sections
```

The section path (`["Refunds", "Timeline"]`) is the metadata that enables filtered retrieval (W5-03) and path-cited answers (`[handbook > Refunds > Timeline]`) — the W5-01 contextual-header trick, here at the chunker level.

## 2. Tables — whole-table chunks

```python
def extract_markdown_tables(text: str) -> tuple[list[dict], str]:
    """Pull out markdown tables as atomic chunks; return them + the remaining text."""
    tables, remaining = [], []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if "|" in lines[i] and i + 1 < len(lines) and set(lines[i+1].replace(" ", "")) <= {"-", "|", ":"}:
            table = [lines[i], lines[i+1]]
            j = i + 2
            while j < len(lines) and "|" in lines[j]:
                table.append(lines[j]); j += 1
            tables.append({"type": "table", "text": "\n".join(table)})
            i = j
        else:
            remaining.append(lines[i]); i += 1
    return tables, "\n".join(remaining)
```

Tables are atomic: splitting a table destroys the header-value relationships that make it meaningful. The whole-table chunk gets its own metadata (caption, source row range) and its own embedding.

## 3. Code and Q&A special cases

| Content | Chunk unit | Metadata |
|---|---|---|
| Code | per function/class (AST-aware, or regex on `def `/`class `) | file, language, signature |
| FAQ | per Q&A pair | question as the retrieval hook |
| Meeting transcripts | per speaker turn or topic block | speaker, timestamp range |
| Config/spec files | whole file if small | key-value pairs in metadata |

The transcript case (E5-01's diarized output) maps naturally: each speaker turn is a chunk with speaker metadata — the E5-04 RAG index consumes it directly.

## 4. The serialization rules (W7-01 applied at chunk level)

| Rule | Example |
|---|---|
| headers prepended to chunk text | `[Handbook > Refunds > Timeline] It takes 5 days` |
| table header row included | `| SKU | Price |\n|---|---|\n| P-100 | 45000 |` |
| code signature included | `def process_refund(order_id): ...` |
| speaker tagged | `[Priya, 12:04] We'll commit to the 5-day window.` |

Each rule preserves the *relationship* between structure and content — the property that generic splitters destroy.

## Exercises

1. Header chunking: run on a real markdown doc; verify the section paths are correct and non-overlapping.
2. Table extraction: 3 tables from your corpus — chunk whole, verify the header row survives; retrieve "what does the pricing table say?" — does the whole-table chunk win?
3. Code chunking: split a Python file by function — verify each chunk has the signature and compiles independently.
4. Transcript chunking: diarized meeting output (E5-01) → speaker-turn chunks with timestamps — retrieve "what did Priya commit to?" from the chunk index.
5. The serialization audit: for 10 chunks, verify the header/rule serializations are present and the content is unmodified.

## Pitfalls

- **Header paths not tracked** — the section metadata is what makes filtered retrieval and citations work
- **Tables split mid-row** — destroys the header-value mapping; whole-table chunks always
- **Code chunks without the signature** — a function body without its def line is unidentifiable
- **Q&A pairs split** — the question is the retrieval hook; pairing them is the point
- **Serialization applied inconsistently** — the contextual-header trick (W5-01) must apply to ALL chunks uniformly, or the embedding space is inconsistent

## Resources

- W4-02 parent (the strategies), W5-01 (contextual headers), W7-01 (metadata design) — composed here
- LangChain [MarkdownHeaderTextSplitter](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/) — the production implementation
- E5-01 (diarized transcripts → chunks) — the audio consumer
