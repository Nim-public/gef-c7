# 01.3 — Content-Aware Chunking

> Subfolder index: [README.md](README.md) · Parent topic: [../01-advanced-chunking.md](../01-advanced-chunking.md)

---

## What you'll learn

- Special content types need special chunking: tables, Q&A pairs, code, transcripts
- The per-type rules and their metadata requirements
- The transcript chunking pattern (E5-01's output → chunks)

## 1. The special-case table

| Content type | Chunk unit | Why | Metadata |
|---|---|---|---|
| **Tables** | whole table | rows meaningless alone; header-value mapping critical | caption, source range |
| **Q&A / FAQ** | one pair | the question is the retrieval hook | category |
| **Code** | per function/class | signature identifies; body implements | file, language |
| **Transcripts** | speaker turn or topic block | speaker + time matter | speaker, timestamp |
| **Legal** | per clause | clause number is the reference | clause number, section |
| **Config/spec** | whole file if < 2k | structure is the meaning | format |

## 2. Implementation patterns

```python
def chunk_by_type(text: str, doc_type: str) -> list[dict]:
    if doc_type == "markdown":
        return chunk_markdown(text)           # headers + tables split out
    if doc_type == "transcript":
        return chunk_transcript(text)         # speaker turns
    if doc_type == "code":
        return chunk_code(text)               # AST or regex on def/class
    return chunk_recursive(text)              # default fallback
```

### Tables

```python
def chunk_markdown_table(table_lines: list[str], caption: str) -> dict:
    return {
        "type": "table",
        "text": "\n".join(table_lines),       # header row + data rows
        "metadata": {"caption": caption, "n_rows": len(table_lines) - 1},
    }
```

### Transcripts

```python
def chunk_transcript(turns: list[dict]) -> list[dict]:
    """turns: [{speaker, start, end, text}] from E5-01"""
    chunks = []
    for turn in turns:
        chunks.append({
            "text": f"[{turn['speaker']} at {turn['start']:.0f}s] {turn['text']}",
            "metadata": {"speaker": turn["speaker"], "start": turn["start"],
                         "end": turn["end"], "type": "transcript_turn"},
        })
    return chunks
```

## Exercises

1. Implement the table chunker: detect markdown tables, extract whole, verify header preservation.
2. The code chunker: split a Python file by top-level `def`/`class`; verify each chunk is independently parseable.
3. The transcript indexer: chunk a diarized meeting (E5-01) by topic blocks; index and retrieve "what did we decide about pricing?"

## Pitfalls

- **Tables split mid-row** — the header-value mapping is destroyed; whole-table only
- **Code chunks without the signature** — a function body without `def f(x):` is unidentifiable
- **Transcript turns too short** — "Yes." alone has no retrieval value; group short consecutive turns
- **Mixed content in one chunk** — a table inside a paragraph confuses both the embedder and the chunker; separate them

## Resources

- W5-01 parent, W7-01 (the metadata), E5-01 (diarized transcripts) — composed here
- [docling](https://github.com/DS4SD/docling) — the layout-aware parser for complex PDFs
