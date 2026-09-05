# Fixed vs Agentic RAG — The Decision Analysis

**What you'll learn:** the per-query-class decision between fixed
retrieval (always retrieve top-k, then answer) and agentic retrieval
(the model chooses whether/what/when to search) — with your own numbers.

## 1. The two modes, restated at the agent level

| Mode | Mechanism | Failure mode |
|---|---|---|
| fixed | retrieve top-k → stuff → answer | retrieval wasted on chitchat; wrong k hurts |
| agentic | model decides to call search | model skips needed retrieval |

W9's routing table picked *patterns* per query class; agentic RAG hands
that routing to the model. The decision analysis asks: for which of your
classes is the model's routing better than your regex?

## 2. The decision table (per class)

| Query class | Fixed | Agentic | Why |
|---|---|---|---|
| chitchat/meta | wasted retrieval | skips search (0 calls) | agentic wins on cost |
| exact-term | fixed FTS-lean | model may paraphrase badly | fixed wins on recall |
| multi-hop | multiple fixed retrievals, hand-wired | model iterates naturally | agentic wins on coverage |
| simple lookup | one fixed retrieval | may double-search | fixed wins on latency |
| ambiguous | fixed guesses the route | model asks or branches | agentic wins on robustness |

The pattern: **fixed wins where the query shape is known; agentic wins
where it varies.** Your W9 measurement (class distribution) decides the
blend — typically fixed pipeline for the hot path, agentic for the long
tail (the W10 boundary statement, re-earned at the retrieval layer).

## 3. The hybrid: agentic with a floor

```python
agent = Agent(
    model=...,
    knowledge=knowledge,
    search_knowledge=True,
    instructions=[
        "... grounding rules (file 02) ...",
        "If you have not searched and the question mentions any domain "
        "term, search once before answering.",
    ],
)
```

The "search once" floor closes the skip-failure for domain queries while
keeping the skip for chitchat — the hybrid that most capstones land on.
The battery's skip-detection instrumentation (file 02-03) measures
whether the floor holds.

## 4. The decision memo row

```markdown
## Retrieval mode (W12)
- Hot path (charts, exact-term): fixed pipeline (W9 patterns)
- Long tail + multi-hop: agentic RAG (search_knowledge + floor)
- Skip behavior: measured via call-count instrumentation
- Revisit: if agentic skip-rate on domain queries >5%, harden the floor
```

The same memo discipline: numbers, triggers, owner.

## 5. The mode-mixing pattern (what ships)

Real systems do not pick one mode — they mix by *route*, and the mix is
the architecture:

```text
route = regex (exact-term) → fixed FTS-lean pipeline
route = known simple classes → fixed pipeline (W9 hot path)
route = long tail / multi-hop → agentic agent with floor
```

The W9 router survives as the *pre-router*; agentic RAG serves the
classes the regex was weak on (your W9 miss log is the evidence). This
is the W11 framework-decision pattern again: measured routing, layered
mechanisms, one eval set grading all of it.

## Exercises

1. Run the eval set in both modes (fixed via your W9 pipeline; agentic
   via `search_knowledge=True`); fill the class × mode table with R@5
   and tokens.
2. Floor drill: add the "search once" instruction; re-run the chitchat
   and absent-fact cases; verify the floor fires on domain terms only.
3. Decision drill: write the memo row from your own table; name the
   revisit trigger with its threshold (skip-rate >5% on domain queries).

## Pitfalls

- Agentic RAG as a default — it is a *routing delegation*; delegate only
  where your regex was weak (the W9 miss log).
- Floors without instrumentation — an unmeasured floor is a hope; call
  counts are the instrument.
- Comparing modes without the same corpus version — the eval header
  discipline applies to mode comparisons too.

## Resources

- Agno agentic RAG docs (context7: `/agno-agi/docs`).
- [`../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md`](../../Week-09-RAG-with-Image-Video-Audio/03-multimodal-rag-patterns/05-pattern-selection.md)
  — the class distribution this decision uses.