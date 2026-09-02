# 03 — Long-Context Strategies

> E2 index: [README.md](README.md)

**Core topics:** *Long-context models vs RAG. Lost-in-the-middle. Context compression. When to paste, retrieve, or compress.*

---

## What you'll learn

- The real costs of long context: quality degradation, latency, cost — not just the token ceiling
- "Lost in the middle": position effects in attention, and what they mean for prompt design
- Context compression techniques (extraction, summarization, LLMLingua-style)
- The decision framework: paste everything vs retrieve vs hybrid

## 1. The long-context fallacy

"A 1M-token window means RAG is obsolete" — wrong three ways:

| Cost | Reality |
|---|---|
| **Quality** | recall degrades with context length even below the ceiling — models are *distracted* by volume ("lost in the middle", Liu et al. 2023): relevant info buried mid-context is missed far more often than at the start/end |
| **Latency** | prefill time scales ~linearly with tokens (KV cache, W15-03): 500k tokens of prefill = seconds before the first output token |
| **Cost** | you pay for the full context every call (mitigated by caching only for *stable* prefixes — W15-04) |

The correct mental model: **long context raises the ceiling of what can be pasted; RAG still decides what's *worth* pasting.** The two compose.

## 2. Lost in the middle — what it means for prompts

Empirical finding: models retrieve information best from the **beginning and end** of long contexts; middle-positioned facts are missed most. Prompt-design consequences:

```python
def order_context(docs, question_type):
    if question_type == "exact":            # needle-type questions
        most_relevant_first = sorted(docs, key=lambda d: -d["score"])
        return most_relevant_first[:3] + most_relevant_first[3:]   # best at the edges
    if question_type == "synthesis":         # needs everything, weighted
        return docs                          # ordering matters less, but cap the length
```

- Put the **most relevant chunks at the start and end** of the context block; bury the merely-related in the middle
- With W5-03's reranker you have the ordering for free — the scores are the placement guide
- For synthesis questions, ordering matters less than *total length* — cap aggressively

## 3. Long-context vs RAG — the decision framework

| Question type | Strategy |
|---|---|
| one document, one answer ("summarize this 80-page contract") | **paste the whole doc** (long context wins; no retrieval precision needed) |
| multi-document, specific facts ("what do *all* contracts say about termination?") | **RAG** (retrieve per doc, synthesize — long-context the whole corpus is cost-prohibitive and degrades) |
| conversational over a codebase/repo | **hybrid**: repo map + selective retrieval (file E3-01) |
| tabular aggregation | **SQL** (W6) — long context cannot compute |

Long context is a *complement*: it widens what you can paste per retrieval — chunk groups, whole small documents, multi-doc bundles — rather than replacing retrieval.

## 4. Context compression (fitting more, better)

When the worth-pasting content exceeds budget, compress before calling:

### a. Extraction compression (extractive — zero hallucination risk)

```python
def extract_relevant(chunks: list[str], question: str, keep_ratio=0.4) -> str:
    """Keep sentences scoring highest against the question embedding."""
    sents = [s for c in chunks for s in split_sentences(c)]
    embs = embed(sents); q = embed([question])[0]
    scores = embs @ q
    order = np.argsort(-scores)
    keep = sorted(order[:int(len(sents) * keep_ratio)])
    return " ".join(sents[i] for i in sorted(keep))    # restore reading order
```

### b. Summarization compression (abstractive — hallucination risk, W2-03 rules)

```python
def compress_docs(docs, budget_tokens=3000):
    per = budget_tokens // len(docs)
    return [summarize(d, max_tokens=per) for d in docs]     # W2-03 summarizer
```

### c. LLMLingua-style token compression (research-grade)

Small LM *deletes* low-information tokens (~2–4× compression, meaning-preserving) — `llmlingua` package. Use when structure matters (tables, code) and extractive/abstractive both lose too much.

### d. Hierarchical memory (the W25 preview)

Compress old turns into summaries that themselves get compressed — the recursion behind MemGPT-style systems (file E9-03).

## 5. The hybrid placement pattern (put it together)

```python
def assemble_context(question, corpus, budget_tokens=30000):
    # 1. retrieve (W4/W5) — precision first
    hits = hybrid_search(question, k=10)                     # W4-05 + W5-03 rerank
    # 2. expand: include the FULL source docs of top hits (long-context luxury)
    full_docs = {h["source"] for h in hits[:3]}
    # 3. fill budget: reranked chunks first, then expanded docs, compressed to fit
    ctx = fit_budget(reranked=hits, expansions=full_docs, corpus=corpus,
                     budget=budget_tokens, compress=compress_docs)   # §4
    return ctx
```

The pattern answers the "RAG is dead, long live long context" debate: retrieval picks *what matters*, long context lets you paste *more of it verbatim* (fewer truncation losses), compression squeezes the rest.

## Exercises

1. Lost-in-the-middle test on your model: hide a fact ("the warranty is 26 months") at position 10%, 50%, 90% of a 30k-token context; ask for it. Plot accuracy vs position.
2. RAG-vs-paste A/B: 10 single-doc questions — whole-doc paste vs chunked RAG. Quality, cost, latency per side.
3. Compression A/B: extractive vs abstractive compression on the same 40k tokens at the same budget; compare answer faithfulness (W5-05 faithfulness metric) and completeness.
4. Hybrid placement: implement `assemble_context`; measure answer quality on multi-doc questions vs chunk-only context (your W5 eval set).
5. LLMLingua trial: compress a 10k-token context ~3×; does the answer survive? On what question types does it break (tables? code? citations)?

## Pitfalls

- **Ceiling ≠ quality** — the model *accepting* 1M tokens says nothing about attention quality over them; benchmark on your tasks
- **Compression hallucination** — abstractive summaries of contracts/policies invent clauses; extractive for compliance contexts
- **Cache destruction by reordering** — aggressive per-question context reordering breaks prefix caching (W15-04); keep the stable prefix, vary only the tail
- **Needle-in-haystack benchmarks as proof** — they test single-fact retrieval, not multi-fact synthesis/aggregation quality
- **Paying full-price prefill for cached-irrelevant content** — 500k-token contexts uncached cost real money per call (W15-04 §1)

## Resources

- Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* — the position-effect paper
- [LLMLingua](https://github.com/microsoft/LLMLingua) — prompt compression
- W4-01 (context assembly), W5-03 (rerank ordering), W13 (state), W15-04 (caching) — composed here
- Long-context model docs (Gemini/GPT/Claude long-context guidance) — per-provider tips
