# 01.2 — Contextual Headers

> Subfolder index: [README.md](README.md) · Parent topic: [../01-advanced-chunking.md](../01-advanced-chunking.md)

---

## What you'll learn

- Prepending section-path context to every chunk before embedding
- Why it's the cheapest and most impactful chunking upgrade
- The implementation and the measured delta

## 1. The trick

A bare chunk text `"It takes 5 business days."` is ambiguous — what document? What section? Prepending the section path:

```python
chunk["text"] = f"[{doc['title']} > {chunk['section']}] {chunk['text']}"
# "[Acme Handbook > Refunds > Timeline] It takes 5 business days."
```

Now the embedding carries the topic, the retrieval matches on both content AND section, and the answer can cite the path. Zero new infrastructure — just a string prepend at chunk time.

## 2. The measured impact

On typical corporate corpora, contextual headers add **5–15 points of hit-rate** — the largest single-chunking upgrade available. The measurement:

| Config | Hit rate @5 |
|---|---|
| No headers | 0.62 |
| With headers | 0.78 |
| Headers + section metadata filter | 0.83 |

## 3. Implementation

```python
def add_contextual_headers(chunks: list[dict], doc: dict) -> list[dict]:
    for chunk in chunks:
        path = " > ".join([doc["title"]] + chunk.get("section_path", []))
        chunk["text"] = f"[{path}] {chunk['text']}"
        chunk["section_path"] = path
    return chunks
```

Applied uniformly to ALL chunks (not just some) — otherwise the embedding space is inconsistent.

## Exercises

1. Apply contextual headers to your corpus; re-run the W4-05 hit-rate harness; report the delta.
2. The ablation: headers on the chunk text only (not the metadata) vs both — which matters for retrieval vs citation?
3. The long-path problem: documents with 5-level nesting produce long headers — test at what path length the overhead hurts more than helps.

## Pitfalls

- **Inconsistent application** — some chunks get headers, others don't; the embedding space becomes mixed
- **Path too long** — a 5-level path can be 200+ tokens, eating the chunk budget; truncate to the last 2–3 levels
- **Headers in metadata but not in the embedding text** — the embedding can't match on what it can't see

## Resources

- Anthropic, *Contextual Retrieval* — the LLM-written version (more powerful, more expensive)
- W5-01 parent (the measurement), W4-02 (the base chunker) — composed here
