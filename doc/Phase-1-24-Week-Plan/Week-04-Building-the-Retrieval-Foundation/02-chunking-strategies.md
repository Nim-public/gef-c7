# 02 — Chunking Strategies

> Week 4 index: [README.md](README.md)

**Session topics:** *document chunking (S1) · Chunking & Retrieval Strategies — optimizing data preparation and search (S2)*

---

## What you'll learn

- Why chunking is *the* highest-leverage knob in RAG
- Four chunking strategies and their failure modes
- Choosing chunk size and overlap from evidence, not vibes
- Metadata design — the part beginners skip and production runs on

## 1. Why chunk at all?

Two constraints collide:

1. **Embeddings need coherent units** — embed a 50-page PDF as one vector and it represents *nothing* precisely; the signal is averaged into mush
2. **Generation needs compact context** — you can only paste a few thousand tokens; each pasted chunk must be *about* the question

The chunk is the atomic unit of retrieval: what gets embedded, what gets returned, what gets cited. Get it wrong and no downstream model fixes it.

## 2. The four strategies

### A. Fixed-size (with overlap)

```python
def chunk_fixed(text: str, size: int = 512, overlap: int = 64):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]
```

- Simple, predictable, fast — good baseline and good for homogeneous text
- Cuts mid-sentence, mid-table, mid-thought → retrieval on a broken fragment

### B. Recursive (the default that works)

Split by a hierarchy of separators until pieces fit:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800, chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],   # try paragraph → line → sentence → word → char
)
chunks = splitter.split_text(long_doc)
```

Keeps natural units when possible, falls back gracefully. This is the sensible default for prose; `langchain-text-splitters` is worth installing just for it.

### C. Structure-aware (document parsing)

Split on the document's *own* structure: markdown headers, PDF sections, HTML tags, code functions. Keep heading hierarchy in metadata (`{"section": "Refunds > Windows > Policy"}`) — retrieval quality jumps because a chunk that starts under "Refund Policy" *is* about refunds.

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")])
docs = splitter.split_text(md_text)      # chunks carry h1/h2/h3 as metadata
```

### D. Content-aware / semantic (preview — Week 5 deep dive)

- **Semantic chunking**: split where consecutive sentences' embedding similarity drops (topic boundaries)
- **Layout-aware**: tables as one chunk each, code blocks whole, Q&A pairs unsplit
- Cost: more compute + pipeline complexity. Rule: don't reach for it until fixed/recursive measurably fail on *your* corpus.

## 3. Choosing size and overlap — the trade triangle

| Chunk size | Retrieval | Generation |
|---|---|---|
| **Small** (200–400 tok) | precise match, sharp vector | fragment lacks context; model must guess |
| **Large** (1000–2000 tok) | diluted vector (multiple topics averaged) | rich context, fewer tokens wasted on headers |
| **Overlap** | saves statements cut at boundaries | duplicated content in context |

Practical procedure — tune on *your* corpus, not folklore:

1. Build a 20-question test set with known answer-chunks (you built this muscle in Week 2's mini-eval)
2. Sweep `size ∈ {300, 500, 800, 1200}`, `overlap ∈ {0, 10%, 20%}`
3. Metric: **hit rate** — is a chunk containing the answer in top-k? (k=5)
4. Pick the smallest size with acceptable hit rate; verify answer quality with the LLM

Typical landing zone for prose: **400–800 tokens, 10–15% overlap**. Tables/code: whole units regardless of size.

## 4. Metadata: the unglamorous 50%

Every chunk ships with:

```python
chunk = {
    "id": "doc7::chunk42",
    "text": "...",
    "source": "handbook_v3.pdf",
    "page": 12,
    "section": "Refunds > Timeline",
    "doc_type": "policy",
    "updated": "2026-08-01",
    "permissions": "all-staff",
}
```

This unlocks: citations (`[handbook_v3.pdf p.12]`), filtered retrieval (`doc_type == "policy"`, Week 5), permission checks *before* generation (security), freshness ordering, and debuggability ("why did this chunk win?"). Without metadata you have a demo; with it, you have a product.

## Exercises

1. Ingest 10 of your capstone docs three ways: fixed-512, recursive-800/100, markdown-header. Report chunk counts and eyeball 3 chunks from each — which keeps meaning best?
2. Build the 20-question hit-rate test set (question + expected source section). It costs ~45 min and powers every sweep this month.
3. Run the sweep from §3; plot hit rate vs chunk size. Write down your corpus's best size/overlap.
4. Break something deliberately: set `chunk_size=2000, overlap=0` and `chunk_size=100, overlap=50`. Describe both failure modes with real examples from your data.
5. Design your chunk metadata schema (fields + why). What filter will Week 5's hybrid search use, and what citation will users see?

## Pitfalls

- **Overlap > size** — infinite loop / duplicate-everything
- **Chunking tables or code with text splitters** — destroys structure; special-case them
- **Measuring only "it looks fine"** — chunking is measurable (hit rate); measure it
- **Forgetting the query is also chunked by the embedder's limit** — questions are short, but ingest-time chunks must fit the model's max input (512 for MiniLM, 8k for others)
- **No IDs** — dedup, updates, and citations all need stable chunk IDs

## Resources

- LangChain [text splitters docs](https://python.langchain.com/docs/concepts/text_splitters/) — all splitter types with code
- pinecone.io learn, *Chunking strategies for LLM applications*
- Anthropic Engineering, *Contextual Retrieval* (the advanced version of "give chunks context" — revisit in Week 5)
- Chroma research: *Evaluating chunking strategies* — metrics-first framing like §3
