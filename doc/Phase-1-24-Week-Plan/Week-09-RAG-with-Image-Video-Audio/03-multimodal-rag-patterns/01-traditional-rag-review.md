# Traditional RAG, Reviewed — The Contract Restated

**What you'll learn:** text RAG as a five-clause contract; every multimodal
pattern in this week is an amendment to exactly one clause. Naming the
clause being amended is how you keep architectures comparable.

## 1. The contract

```text
1. INGEST:    corpus → chunks → embeddings
2. INDEX:     vectors + metadata, filterable
3. RETRIEVE:  query → embedding → top-K chunks
4. AUGMENT:   prompt = question + top-K chunks (+ citations)
5. GENERATE:  LLM answers, grounded in chunks
```

Each clause carries a guarantee; RAG quality = all five holding:

| Clause | Guarantee | Measured by |
|---|---|---|
| Ingest | chunks carry meaning | chunk-size ablation (W4) |
| Index | filterable, fresh | index tests (this week file 02) |
| Retrieve | relevant chunks rank high | R@K, MRR (W4/W7) |
| Augment | context fits, cites cleanly | prompt-fit audit |
| Generate | answers quote the context | faithfulness (W5/W12) |

## 2. Multimodal amendments, one clause at a time

| Pattern | Amends | How |
|---|---|---|
| Caption-then-index (P1) | Ingest | image → text caption → text index |
| Unified space (P2) | Retrieve | query embedding matches image embeddings directly |
| VLM generation (P3) | Generate | answer grounded in *pixels*, not text |
| Hybrid (your capstone) | Retrieve + Generate | fusion of P1+P2, citations either way |

The discipline: when you say "we use pattern 2", you can name the amended
clause and what stays guaranteed. Patterns that quietly break Ingest (e.g.,
chunking images into regions without manifest records) fail later at
citation time — the contract is where those bugs become visible.

## 3. What does *not* change

Everything around the clauses: evaluation harness, cost ledger, manifest
discipline, row-alignment invariants. Week 04's `eval_retrieval.py`
extends to multimodal by adding a column, not by rewriting — that is the
point of stating the contract first.

## 4. The contract in code — one function per clause

```python
def rag_answer(query: str) -> dict:
    chunks = ingest_and_chunk(CORPUS)            # clause 1 (offline)
    index = build_index(chunks)                  # clause 2 (offline)
    hits = retrieve(query, index, k=5)           # clause 3
    prompt = augment(query, hits)                # clause 4
    answer = generate(prompt)                    # clause 5
    return {"answer": answer, "citations": [h["unit_id"] for h in hits]}
```

Naming clauses in code is the whole point: when a multimodal pattern
amends clause 3 (unified space), the diff is *one function* — and the
other four clauses' tests keep passing untouched. The contract is also
your eval structure: one harness section per clause.

## 5. The clause-to-test matrix

Each clause needs at least one automated check — the matrix that keeps
the contract enforced as patterns change:

| Clause | Cheapest test | Runs |
|---|---|---|
| Ingest | row count + hash validation (W7 gate) | per ingest |
| Index | schema check + GT smoke query | per index build |
| Retrieve | R@10 ≥ baseline on 25 queries | per eval run |
| Augment | token budget assertion (W9-04) | per answer |
| Generate | citation audit + faithfulness (W5) | per answer |

The matrix is deliberately boring: every cell is an artifact you already
built in Weeks 04–09. Its value is completeness — any clause without a
test is where the next silent regression lands.

## Exercises

1. Write the contract for *your* capstone with the amended clauses marked;
   one line per clause, one owner-week per amendment.
2. Contract-violation hunt: name three ways the caption-then-index pattern
   can break the Augment clause (caption hallucinated; caption lacks
   numbers; caption duplicates page text).
3. For each violation in exercise 2, name the week's artifact that detects
   it (validation report, eval harness, citation audit).
4. Map your existing Week-04 code to the five clauses — anything that
   spans two clauses is refactor bait; note it.

## Pitfalls

- Treating "RAG" as one indivisible thing — the clause granularity is what
  makes patterns comparable and costs estimable.
- Amending two clauses at once and losing attribution — one amendment per
  experiment, or deltas are unexplainable.
- Contract without clause-level tests — a "failing RAG" tells you nothing;
  a failing clause tells you what to fix.

## Resources

- Week 04 files (the original contract); Week 05 eval harness.
- Your capstone README's architecture section — the contract lives there.
