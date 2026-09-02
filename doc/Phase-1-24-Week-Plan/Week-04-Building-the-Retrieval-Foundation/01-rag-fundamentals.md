# 01 — RAG Fundamentals

> Week 4 index: [README.md](README.md)

**Session 1 topic:** *Introduce RAG fundamentals: why it's essential, how it works, document chunking. LLM Limitations — constraints of base language models. BYOD (Bring Your Own Data) — integrating custom data with LLMs. Embeddings, Vector Databases, Search Engine Development.*

---

## What you'll learn

- The four failure modes of raw LLMs on enterprise data
- What "retrieval-augmented" means mechanically
- The two pipelines of every RAG system (ingestion, query) and every component in them
- Grounding, citations, and why RAG became the default enterprise pattern

## 1. LLM limitations that force RAG

| Limitation | Symptom | Example |
|---|---|---|
| **Knowledge cutoff** | correct-but-stale answers | "our current price is $X" — from last year's training data |
| **No private data** | confident fabrication | your internal policy numbers were never in training |
| **Hallucination** | plausible, false, confident | invented URLs, stats, policy names (Week 2 file 02's failure notes) |
| **No provenance** | can't verify or audit | user asks "source?" — there is none |
| **Context window** | can't paste the whole wiki | 5,000 docs ≫ any context limit |

Fine-tuning (file W3-05) fixes *behavior*, not *facts* — facts rot and fine-tunes forget. The fix for facts is **fetching them at ask-time**.

## 2. What RAG actually is

**Retrieval-Augmented Generation** = before answering, *retrieve* relevant passages from your data and put them in the prompt:

```
user question ─► [retriever: find top-k relevant chunks] ─► prompt = question + chunks ─► LLM ─► grounded answer
```

The model's job narrows from "know everything" to "read and synthesize" — a task LLMs are excellent at. The *knowledge* lives in your retrievable corpus, updatable per-minute, auditable per-answer.

### The BYOD framing

"Bring Your Own Data" is the enterprise reality: the valuable knowledge is your PDFs, tickets, wikis, DBs — none of it was in any training run. RAG is the bridge between that pile and the LLM, and it's built from skills you already have: crawling/parsing (W1-04), embeddings (W2-03), prompting (W3-01/02).

## 3. The two pipelines (memorize this diagram)

```
INGESTION (offline, runs when data changes)
  documents ─► parse/extract ─► clean ─► chunk ─► embed each chunk ─► index (vector DB + metadata)
       │                                                              │
QUERY (online, per user question)
  question ─► embed ─► search index (top-k) ─► [rerank/filter] ─► prompt assembly ─► LLM ─► answer + citations
```

Component responsibilities:

| Stage | Ingestion side | Query side |
|---|---|---|
| Parse | PDF/HTML/DB → text (W1-04) | — |
| Chunk | split with strategy + metadata (file 02) | — |
| Embed | `model.encode(chunk)` (W2-03) | `model.encode(question)` — **same model!** |
| Index | FAISS/LanceDB add (file 03) | `search(query_vector, k)` |
| Generate | — | prompt template with `<context>` blocks (W3-02) |

## 4. Grounded generation: the prompt that makes RAG work

```python
SYSTEM = """You answer questions using ONLY the provided context.
Rules:
- Answer from <context> blocks; cite as [doc:ID].
- If the context is insufficient: "I don't have that information."
- Never use outside knowledge for facts about Acme."""

def answer(question, hits):
    blocks = "\n\n".join(
        f"<context id='{h['id']}' source='{h['source']}'>\n{h['text']}\n</context>"
        for h in hits)
    return client.chat.completions.create(
        model="gpt-4o-mini", temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"{blocks}\n\nQuestion: {question}"},
        ]).choices[0].message.content
```

Design decisions encoded here (all from Week 3): delimited context (injection defense), citation contract (provenance), explicit insufficiency escape (hallucination pressure valve), `temperature=0` (factual).

## 5. Why RAG won as the enterprise default

| Requirement | RAG answer |
|---|---|
| Freshness | re-index when data changes — no retraining |
| Trust/audit | every claim cites a chunk |
| Access control | filter chunks by permission *before* generation |
| Cost | retrieve k chunks, not fine-tune on the corpus |
| Multi-data-source | index everything; sources are just metadata |

When RAG is the *wrong* tool (record this in your capstone scope): teaching style/tone (→ fine-tune), teaching a general skill (→ prompting/fine-tune), when "retrieve-then-read" latency is unacceptable and facts are static (→ distill).

## Exercises

1. Take your Week 3 chatbot. Build the ingestion pipeline for 20 of your capstone docs: parse → chunk (any strategy) → embed → store as JSONL. Measure: docs in, chunks out, embed time.
2. Wire the retrieval: embed a query, cosine-search your JSONL in numpy, top-3 into the grounded prompt. Run 5 test questions. Where did retrieval fail?
3. Hallucination experiment: run your *Week 3* bot (no context) vs this RAG prompt on 3 questions about facts that exist only in your corpus. Compare answers.
4. Inject a chunk about a *different* topic into the top-k. Does the model cite the irrelevant chunk, ignore it, or blend it? What does that tell you about needing rerankers (Week 5)?
5. Write the "insufficiency" test: 5 questions with no answer in your corpus. Does the bot say "I don't have that information" every time?

## Pitfalls

- **Embedding model mismatch** between ingestion and query time — different vector spaces, silent garbage (W2-03 pitfall, now a system-level risk)
- **Context stuffing** — "top-20 chunks" is not free: dilutes attention, costs tokens; k=3–8 with good retrieval beats k=20
- **Chunk IDs without sources** — citations are the product; metadata is not optional (file 02)
- **Testing only questions the corpus can answer** — the insufficiency escape needs testing too
- **Skipping the parse quality check** — RAG quality is capped by extraction quality (Week 2 file 03 PDF notes apply verbatim)

## Resources

- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020) — the original paper
- OpenAI, [Embeddings use cases](https://platform.openai.com/docs/guides/embeddings) + cookbook *Question answering using embeddings*
- Anthropic Engineering, *Reducing hallucinations* + contextual retrieval posts
- pinecone.io *learn* section — chunking and indexing explainers (vendor blog but genuinely good)
