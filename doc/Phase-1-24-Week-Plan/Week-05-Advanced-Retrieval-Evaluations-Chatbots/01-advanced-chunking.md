# 01 — Advanced Chunking: Semantic & Content-Aware

> Week 5 index: [README.md](README.md)

**Session 1 topic:** *Advanced chunking strategies: semantic chunking, content-aware document-based chunking.*

---

## What you'll learn

- Semantic chunking: split on *topic boundaries*, not character counts
- Content-aware chunking: tables, Q&A pairs, code — special shapes get special handling
- Contextual enrichment: making each chunk self-describing
- Measuring whether any of it actually helped (Week 4's harness decides)

## 1. Where fixed/recursive chunking breaks

Recall the recursive splitter keeps units together until they don't fit — but paragraphs drift topics mid-paragraph, and sections blur. Two real failure patterns:

- **Multi-topic mega-chunks**: one 800-token chunk half about refunds, half about shipping → its embedding is about neither; retrieved for both, perfect for neither
- **Topic split across chunks**: one coherent answer split at an arbitrary character boundary

## 2. Semantic chunking

Embed sentences, find where similarity between consecutive windows drops sharply — that drop is a topic boundary. Split there instead of at character N.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def semantic_chunks(text: str, threshold: float = 0.5, min_size: int = 3) -> list[str]:
    sents = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    embs = model.encode(sents, normalize_embeddings=True)

    chunks, start = [], 0
    for i in range(1, len(sents)):
        sim = float(embs[i - 1] @ embs[i]) if (embs := embs) else 0   # consecutive similarity
        if sim < threshold and i - start >= min_size:
            chunks.append(". ".join(sents[start:i]) + ".")
            start = i
    chunks.append(". ".join(sents[start:]) + ".")
    return chunks
```

Trade-offs: boundaries follow meaning (good) at the cost of an embedding pass over every sentence (slower ingestion), plus a `threshold` hyperparameter that varies per corpus (calibrate with the histogram of consecutive similarities — the dip separation is visible).

## 3. Content-aware chunking: respect what the document *is*

| Content type | Rule |
|---|---|
| **Tables** | chunk whole (rows are meaningless alone); serialize as markdown with header row; table *caption/title* in metadata |
| **Q&A / FAQ** | one pair per chunk — question is the retrieval hook |
| **Code** | per function/class (AST-aware splitters exist); keep the signature line |
| **Emails/transcripts** | per message or per topic block with speaker metadata |
| **Legal/contracts** | per clause, keep clause number in metadata |
| **PDFs with layout** | use `pdfplumber`'s structure (file W1-04) rather than plain `extract_text` |

The multiplier trick — **contextual headers**: prepend the section path to every chunk's text before embedding:

```python
chunk_text = f"[{doc['title']} > {chunk['section']}] {chunk['text']}"
```

A bare "It takes 5 business days." becomes "…[Acme Handbook > Refunds > Timeline] It takes 5 business days." — now the embedding carries the topic, and the LLM can cite the section. Cheap, huge, zero new infrastructure. (Anthropic's *Contextual Retrieval* is the industrial-strength version: an LLM writes a one-sentence context blurb per chunk before embedding — expensive, but the strongest known uplift when chunks are context-starved.)

## 4. Measure or it didn't happen

Week 4's harness (`search_eval.jsonl`, hit-rate@k) is the judge:

| Strategy | Hit rate @5 | Chunks | Ingest time |
|---|---|---|---|
| recursive-800 (baseline) |  |  |  |
| semantic (thr=0.6) |  |  |  |
| recursive + contextual headers |  |  |  |
| structure-aware (md headers) |  |  |  |

Expect: contextual headers are the best effort/reward; semantic chunking helps on long meandering docs, does nothing on already-structured ones. **If baseline ≈ upgrade, keep the baseline** — complexity is a cost you pay every day.

## Exercises

1. Plot the histogram of consecutive-sentence similarities on 3 of your docs. Where's the natural threshold? Do the resulting chunks match *your* reading of topic boundaries?
2. Implement semantic chunking (above) and run the harness. Hit rate vs recursive baseline — worth it?
3. Take 3 tables from your corpus. Chunk whole-table vs row-wise; compare retrieval for "what does the pricing table say about annual plans?"
4. Add contextual headers to your Week 4 engine; re-run harness. Numbers before/after.
5. Pick one doc type from the content-aware table and write its special-case chunker. What metadata did it need that prose chunks didn't?

## Pitfalls

- **Semantic chunking on short docs** — everything is one topic; you get one giant chunk
- **Threshold cargo-culting** — copy someone's 0.5 without your histogram and you split at noise
- **Embedding the header *instead of* the chunk** — the context line *prepends*; the content must stay
- **Tables serialized to strings without headers** — cells lose meaning ("5000" means nothing without "Price (INR)")
- **Optimizing chunking with no eval set** — unmeasurable by construction; build the harness first

## Resources

- LangChain [semantic chunking how-to](https://python.langchain.com/docs/how_to/semantic-chunker/)
- Greg Kamradt, *5 Levels of Text Splitting* (video + repo) — the canonical chunking taxonomy
- Anthropic Engineering, *Contextual Retrieval* — LLM-written chunk context, with measured uplift
- Chroma, *Evaluating chunking strategies* — the metrics-first approach this file follows
