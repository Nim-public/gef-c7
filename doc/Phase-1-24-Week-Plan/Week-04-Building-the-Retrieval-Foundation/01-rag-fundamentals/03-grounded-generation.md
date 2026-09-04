# 01.3 — Grounded Generation

> Subfolder index: [README.md](README.md) · Parent: [../01-rag-fundamentals.md](../01-rag-fundamentals.md)

---

## What you'll learn

- The grounded prompt contract: the four clauses and their tests
- The citation machinery: format, validation, rendering
- The insufficiency escape: the hallucination pressure valve
- The k-selection: how many chunks to paste

## 1. The four clauses

```python
SYSTEM = """You answer questions using ONLY the provided context.
Rules:
1. Answer from <context> blocks; cite as [doc:id].
2. If the context is insufficient: reply exactly "I don't have that information."
3. Never use outside knowledge for facts about Acme.
4. Numbers, dates, and names must appear verbatim in a cited context block."""
```

| Clause | Prevents | Test |
|---|---|---|
| ONLY the context | outside-knowledge contamination | the no-context probe |
| cite as [doc:id] | uncited claims | the citation validator (W5-04) |
| insufficiency escape | confident fabrication | the no-answer battery (W4-01 ex. 5) |
| verbatim numbers | paraphrased/rounded facts | the numeric check (W12-04) |

Each clause has a test; each test maps to a production failure. The constitution is the grounding contract's enforcement layer (W3-02's system prompt, RAG edition).

## 2. The citation machinery

```python
import re

CITE_RE = re.compile(r"\[doc:([^\]]+)\]")

def extract_citations(answer: str) -> list[str]:
    return CITE_RE.findall(answer)

def validate_citations(answer: str, hits: list[dict]) -> list[str]:
    cited = set(extract_citations(answer))
    available = {h["id"] for h in hits}
    return list(cited - available)              # invalid citations = hallucinated sources
```

The validator runs on every answer (W5-04 §3): invalid citations trigger regeneration or flagging — the guardrail that makes citations trustworthy.

## 3. The insufficiency escape

Two triggers, both tested:

| Trigger | Mechanism | Test |
|---|---|---|
| retrieval-side | top score below threshold (W4-03's elbow) | the weak-hit battery |
| generation-side | the model says "I don't have that information." | the no-answer battery |

The generation-side escape needs the model to *choose* the escape — which requires the instruction AND low enough temperature that it doesn't improvise instead. The battery: 5 unanswerable questions × 3 phrasings, ≥13/15 must escape (W4-01 ex. 5's bar).

## 4. The k-selection (how many chunks to paste)

| k | Effect | When |
|---|---|---|
| 1–3 | focused, cheap, risks missing context | precise questions |
| 5–8 | the default balance | most production systems |
| 10–20 | comprehensive | multi-part synthesis; diluted attention |

The k-selection is empirical: sweep k on your eval set, plot faithfulness (W5-05) vs k — the optimum balances coverage against dilution. W5-03's reranker lets you use larger k (rerank 20, paste 5) — the coverage/precision split.

## Exercises

1. Clause-by-clause testing: 4 tests, one per clause — each fails when the clause is removed from the prompt.
2. Citation lifecycle: extract → validate → render — the full path; test with 0, 1, and 5 citations in the answer.
3. The k-sweep: faithfulness (W5-05) at k ∈ {1, 3, 5, 10, 20} — plot; find your optimum and justify it.
4. The paraphrase attack: the model restates the context in different words — does the verbatim-numbers rule catch it?
5. The multi-context drill: the answer needs TWO context blocks — test that both are cited and the join is coherent.

## Pitfalls

- **The escape instruction alone** — without the retrieval-side trigger, the model only escapes when it *feels* insufficient; both sides needed
- **Context blocks without ids** — citations reference nothing; the id must be in the block AND in the hit metadata
- **Temperature above 0 on grounded generation** — sampling variance produces different citations per run; T=0 for factual
- **The verbatim rule too strict** — paraphrased answers with correct meaning flagged as unfaithful; the rule targets numbers/names, not phrasing
- **k uncoupled from reranking** — pasting top-k from a reranked list is different from pasting top-k raw; the reranker (W5-03) changes the optimal k

## Resources

- W4-01 parent (the architecture), W5-04 (the guards), W5-05 (the metrics) — composed here
- W3-02 (the constitution pattern), W12-04 (numeric grounding) — the enforcement layers
