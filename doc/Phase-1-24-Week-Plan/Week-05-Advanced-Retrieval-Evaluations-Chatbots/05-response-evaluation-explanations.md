# 05 — Response Evaluation & Explanation (Ragas)

> Week 5 index: [README.md](README.md)

**Session 2 topic:** *Response Evaluation & Explanation.*

---

## What you'll learn

- The four Ragas metrics and what each isolates in your pipeline
- Running Ragas locally on your own eval set
- Reading the numbers as *pipeline diagnostics* (which stage is broken?)
- Generating explanations users (and mentors) trust

## 1. Why answer "vibes" aren't evaluation

"The bot seems good" is not a number. RAG evaluation splits quality into **independent, diagnosable components**:

```
question ─► retrieved_contexts ─► response
                 │                     │
   context precision/recall        faithfulness / answer relevancy
   (was retrieval good?)           (was generation good?)
```

The separation is the whole point: a 0.4 faithfulness + 0.9 context precision = *retrieval fine, generation lying*. No more guessing which stage to fix.

| Metric | Question it answers | Needs |
|---|---|---|
| **Faithfulness** | Is every claim in the response supported by the retrieved context? | response + contexts |
| **Answer relevancy** | Does the response address the question? (non-commital/wrong-topic detection) | question + response |
| **Context precision** | Are the *relevant* chunks ranked at the top of what was retrieved? | question + reference + contexts |
| **Context recall** | Did retrieval surface everything needed for the reference answer? | question + reference + contexts |

## 2. Ragas, locally

```powershell
pip install ragas datasets
```

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy, context_precision, context_recall,
)
from datasets import Dataset

rows = [{
    "question": q,
    "answer": response,                     # what your bot produced
    "contexts": [h["text"] for h in hits],  # what retrieval returned
    "ground_truth": expected,               # your hand-written reference
} for q, response, hits, expected in cases]

ds = Dataset.from_list(rows)
report = evaluate(ds, metrics=[faithfulness, answer_relevancy,
                               context_precision, context_recall])
print(report)      # e.g. {'faithfulness': 0.83, 'answer_relevancy': 0.91, ...}
```

Setup requirements: an eval LLM (the metrics are LLM-as-judge — use a strong cheap model like `gpt-4o-mini`, set `temperature=0`) and embeddings for relevancy scoring. Both are injectable (`evaluate(..., llm=..., embeddings=...)`) so you can judge local models with local judges.

**Build the dataset from your logs**: the Week 3/4 task files had you log turns as JSONL — each row needs question, reference answer (you write it once), and the pipeline's retrieved contexts. 20–30 rows is enough to see signals; 100+ for decisions.

## 3. Diagnosing with the four numbers

| Pattern | Diagnosis | Fix lever |
|---|---|---|
| context recall low | retrieval misses the right chunk | chunking/embedding/fusion (W5-01/02/03) |
| context precision low | right chunk retrieved but buried | reranking (W5-03), k↓ |
| faithfulness low | model invents beyond context | prompt contract, temperature↓, smaller k (W4-01) |
| answer relevancy low | model dodges/off-topic | system prompt, query understanding |

Plus the meta-rule: **fix the cheapest failing stage first** — retrieval fixes are deterministic; generation fixes are not.

## 4. Explanations: showing your work to humans

Evaluation isn't only for you — the UI-level "explanation" builds user trust:

```python
def explain(hits, confidence: str) -> str:
    srcs = sorted({f"{h['source']} §{h.get('section','')}".strip() for h in hits})
    return (f"Answer grounded in: {'; '.join(srcs)}. "
            f"Retrieval confidence: {confidence}. "
            f"I read the {len(hits)} most relevant passages and cited the ones used.")
```

Three explanation levels, ascending effort:

1. **Citations** (free — the `[doc:ID]` contract already there)
2. **Retrieval transparency** — "searched 50 candidates, these 3 scored highest for *these* matched terms" (keyword hits + rerank scores)
3. **Self-check statement** — one extra LLM call: "Which parts of your answer are directly supported? Which are inference?" — surprisingly honest, use sparingly (latency)

## Exercises

1. Build a 25-row Ragas dataset from your capstone logs (question, reference, contexts, answer). Run the four metrics. Which is lowest?
2. Diagnose the lowest metric with the §3 table; apply one fix; re-run. Numbers before/after.
3. Faithfulness stress test: force k=15 (context stuffing) vs k=3 — plot faithfulness for both. Which direction does dilution push it?
4. Judge stability: run the same 10 rows twice with `temperature=0` judge. How stable are scores (±0.05? ±0.2?)? What does that tell you about trusting single runs?
5. Build `explain()` into your chatbot UI. Then break a citation on purpose — does your output guardrail from file 04 catch it?

## Pitfalls

- **LLM-as-judge is a model too** — it hallucinates scores; pin temperature=0, judge model, and *version* your judge like any prompt (W3-02)
- **Judging with the same model that generated** — self-preference bias; use a different family when possible
- **Small-n theater** — 5 samples with ±0.2 noise support no conclusions; report n alongside every metric
- **Optimizing one metric into another's grave** — faithfulness 1.0 is trivially achievable ("I don't know"); always read the four together
- **Reference answers written by the same person who wrote the bot** — blind spots transfer; swap graders with a teammate

## Resources

- [Ragas docs](https://docs.ragas.io) — metrics reference + *get started* (the four above are the core set)
- Es et al., *Ragas: Automated Evaluation of Retrieval Augmented Generation* (paper)
- Hamel Husain, *Your AI product needs evals* — the mindset piece this file implements
- OpenAI Cookbook, *Evaluation with LLM-as-judge patterns*
