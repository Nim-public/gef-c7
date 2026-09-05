# Ragas Revision — Four Metrics, Diagnosis Patterns

**What you'll learn:** the four Ragas metrics as *diagnoses*: each
metric names a specific pipeline failure, and the four together form a
decision tree from score to fix.

## 1. The four metrics, as diagnoses

| Metric | Measures | Low score diagnoses |
|---|---|---|
| faithfulness | answer claims ⊆ context | hallucination (generation or retrieval noise) |
| answer relevancy | answer ↔ question | off-target generation |
| context precision | retrieved chunks relevant, ranked well | retriever noise (bad chunks ranked high) |
| context recall | ground-truth facts present in retrieved context | retrieval miss (chunks not found) |

The diagnosis pairs: **low recall + high faithfulness** = the system
honestly says "not found" (a *retrieval* problem — fix indexing/chunking);
**high recall + low faithfulness** = the right chunks were there but the
answer invented (a *generation* problem — fix the prompt/constitution).

## 2. The decision tree

```text
context recall low?
  ├─ yes → RETRIEVAL: check chunking, embeddings, hybrid weights (W9)
  └─ no → context precision low?
        ├─ yes → RANKING: rerank (W12) or trim k
        └─ no → faithfulness low?
              ├─ yes → GENERATION: constitution, temp, context formatting
              └─ no → relevancy low?
                    └─ yes → UNDERSTANDING: query rewriting or decomposition
```

The tree is the eval's *action* layer — each leaf names the week's
artifact to fix. The W12-05 routing table sends queries to patterns;
this tree sends *scores* to fixes.

## 3. The implementation (minimal Ragas-style, your scorers)

```python
def context_recall(query: str, contexts: list[str], gold_facts: list[str]) -> float:
    blob = " ".join(contexts).lower()
    return sum(1 for f in gold_facts if f.lower() in blob) / len(gold_facts)

def faithfulness(answer: str, contexts: list[str]) -> float:
    claims = split_claims(answer)
    supported = sum(1 for c in claims if any(cfact(c, ctx) for ctx in contexts))
    return supported / max(len(claims), 1)
```

| Metric | Inputs | Gold needed |
|---|---|---|
| context recall | contexts + gold facts | yes (the facts) |
| context precision | contexts + relevance labels | yes (sampled) |
| faithfulness | answer + contexts | no (self-consistency) |
| answer relevancy | answer + query | no |

Recall needs gold facts (your data); relevancy needs no gold — the
metrics differ in *labeling cost*, which is why the eval set (file 04)
records which gold each case carries.

## 5. The metric-lie table (where each metric misleads)

| Metric | How it lies | Guard |
|---|---|---|
| faithfulness | one-sentence answers score 1.0 | claim splitting + length floor |
| answer relevancy | echoes the question back | relevancy = new information check |
| context precision | one perfect chunk among dross | rank-aware (MRR-style) |
| context recall | gold facts trivially word-matched | fact paraphrase matching |

Every metric has a failure mode where it rewards garbage — the guard
column is the metric's own validation. The W9-04 walkthrough (one case
per scoring type) applies here: hand-verify one case per metric before
trusting any of them.

## 6. The Ragas library vs your implementations (the port decision)

| Option | Pros | Cons |
|---|---|---|
| Ragas library | maintained, standard | fixed metric definitions, LLM-judge cost |
| your implementations | transparent, tunable, free | maintenance, drift risk |

The decision rule: use the library when its definitions match your
needs and the LLM-judge cost fits the budget; use your implementations
when you need domain-specific claim matching (your corpus's vocabulary).
Either way — hand-verify 10 cases first; the library is not exempt from
the calibration protocol.

## Exercises

1. Implement the four metrics on your 15-case set; produce the
   diagnosis-tree path per case; group cases by leaf.
2. Fix-drill: take the most common leaf; apply its fix (e.g., rerank);
   re-run; the leaf's population must shrink.
3. Claim-splitter drill: improve `split_claims` on 5 answers; the
   faithfulness scores shift — the splitter is the metric's real work.
4. Lie-drill: construct one garbage answer per metric that fools it;
   then add the guard — the metric's validation by its own failure.