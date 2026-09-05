# LlamaIndex Essentials — Readers, Nodes, Index, Query Engine

**What you'll learn:** LlamaIndex's four objects and how they map to
your pipeline: readers load, nodes chunk, indexes embed, query engines
retrieve+synthesize — the W9 pipeline with LlamaIndex's vocabulary.

## 1. The four objects

```python
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex, Settings)
from llama_index.core.node_parser import SentenceSplitter

Settings.embed_model = "pinned-embedder"      # pinned, not default!
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)

docs = SimpleDirectoryReader("data/raw/docs").load_data()
nodes = Settings.node_parser.get_nodes_from_documents(docs)
index = VectorStoreIndex(nodes)               # or from your vector store
engine = index.as_query_engine(similarity_top_k=5)

response = engine.query("Which chart shows Q3 margin?")
```

| LlamaIndex object | Your W9 equivalent |
|---|---|
| reader | the W7 ingestion (files → documents) |
| node parser | the W4 chunker |
| index | the W9 LanceDB vector store |
| query engine | retrieval + synthesis (your RAG node) |

The mapping is the W10-style table — the concepts are identical; the
vocabulary differs. The Settings object (file 02) is where the pinning
happens.

## 2. The query engine's two halves

| Half | What it does | Your equivalent |
|---|---|---|
| retriever | fetch top-k nodes | hybrid_retrieve (W9) |
| synthesizer | LLM composes the answer | the generation node |

```python
retriever = index.as_retriever(similarity_top_k=5)
nodes = retriever.retrieve("Q3 margin")     # retrieval alone
```

The split matters for evaluation: retrieval quality (R@K on the nodes)
and synthesis quality (faithfulness given the nodes) are *separable* —
the W9-05 discipline applies to the retriever half directly.

## 3. LlamaIndex vs your stack (the honest comparison)

| Aspect | Your W9 stack | LlamaIndex |
|---|---|---|
| ingestion | your manifest pipeline | readers (less control) |
| chunking | your settings | SentenceSplitter (configurable) |
| vector store | LanceDB hybrid | pluggable (LanceDB supported) |
| query | your RAG node | query engine (retriever+synthesizer) |
| evaluation | your harness | separate (your harness wins) |

The integration decision: LlamaIndex's *readers and node parsers* are
convenient; your *manifest, hybrid search, and harness* are the
discipline. The comparison (file 03) measures whether the convenience
costs quality.

## 5. The four-object review (the wiring checklist)

```text
[ ] reader: loads your corpus (or a subset) without errors
[ ] node parser: chunk settings from your W4 pin (not defaults)
[ ] index: built over nodes carrying unit_id metadata
[ ] query engine: retriever + synthesizer, both pinned via Settings
[ ] round-trip: node metadata → manifest rows resolve
```

The wiring checklist is the four objects' review — the same structure
as the W10 assembly checklist. The round-trip row is the life-line: a
node whose metadata lost the unit_id produces uncitable answers.

## 6. LlamaIndex vs your pipeline (the vocabulary translation)

| LlamaIndex term | Your program's term |
|---|---|
| document | a loaded file (pre-chunk) |
| node | a chunk — a *unit* in your manifest |
| index | the vector store + embedding config |
| retriever | your hybrid retrieval |
| query engine | retriever + synthesizer (your RAG node) |
| response synthesizer | the generation prompt + LLM call |

The translation table is the week's vocabulary lesson — every LlamaIndex
concept has a W7–W9 name you already own. Reading LlamaIndex docs is now
translation, not learning from scratch.

## Exercises

1. Build the four objects over a subset of your corpus; query it;
   compare the answers with your W9 stack's on the same questions.
2. Node-audit drill: inspect the nodes (text, metadata, ids); verify
   your manifest's unit_ids survived — metadata round-tripping (W9
   rule), LlamaIndex edition.
3. Retriever drill: run the retriever alone on 5 queries; R@5 vs your
   W9 retriever — the retriever half, isolated.
4. Review drill: run the §5 checklist; every row cites its test.

## Pitfalls

- Default embedder silently used — `Settings.embed_model` unset means
  OpenAI's default, not yours; pin or the vectors mismatch.
- Node ids not carrying `unit_id` — citations die; metadata must
  round-trip (the W9 rule).
- LlamaIndex's query engine as the *evaluator* — your harness evaluates;
  the engine is the system under test.