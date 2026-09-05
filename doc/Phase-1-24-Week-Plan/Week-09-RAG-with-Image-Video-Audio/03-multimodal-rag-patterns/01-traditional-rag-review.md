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

## Exercises

1. Write the contract for *your* capstone with the amended clauses marked;
   one line per clause, one owner-week per amendment.
2. Contract-violation hunt: name three ways the caption-then-index pattern
   can break the Augment clause (caption hallucinated; caption lacks
   numbers; caption duplicates page text).
3. For each violation in exercise 2, name the week's artifact that detects
   it (validation report, eval harness, citation audit).

## Pitfalls

- Treating "RAG" as one indivisible thing — the clause granularity is what
  makes patterns comparable and costs estimable.
- Amending two clauses at once and losing attribution — one amendment per
  experiment, or deltas are unexplainable.

## Resources

- Week 04 files (the original contract); Week 05 eval harness.
- Your capstone README's architecture section — the contract lives there.
