# 05.1 — Ragas in Practice

> Subfolder index: [README.md](README.md) · Parent topic: [../05-response-evaluation-explanations.md](../05-response-evaluation-explanations.md)

The Ragas implementation from W5-05, operationalized:

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

def run_ragas(cases: list[dict]) -> dict:
    ds = Dataset.from_list([{
        "question": c["question"], "answer": c["response"],
        "contexts": c["retrieved_contexts"], "ground_truth": c["reference"]
    } for c in cases])
    report = evaluate(ds, metrics=[faithfulness, answer_relevancy,
                                   context_precision, context_recall])
    return dict(report)
```

The eval set construction: each row needs question, reference (hand-written), retrieved contexts (from the pipeline), and the pipeline's answer. The W10-04 logs + W16-01's versioned eval sets provide the raw material.

## Exercises

1. Build a 30-case Ragas dataset from your W5-04 logs; run the four metrics; produce the slice table (per route, per doc type).
2. The diagnosis: identify the lowest metric; apply the mapped fix (file W5-05 §3's table); re-run; report the delta.
3. The judge audit: run the eval twice; report the score spread; if > 0.1, investigate the judge (model, temperature, prompt).
4. The k-sweep faithfulness: measure faithfulness at k ∈ {3, 5, 10, 20} — the dilution curve.

## Pitfalls

- **LLM-as-judge without calibration** — the judge hallucinates scores; pin and version it (W16-01)
- **n too small for conclusions** — report n with every metric; below 20, treat as directional
- **Aggregate-only reporting** — the per-slice breakdown reveals what the aggregate hides (W16-01's slice discipline)

## Resources

- [Ragas docs](https://docs.ragas.io/) — the metric reference
- W5-05 parent, W16-01 (versioning), W10-04 (the logs feeding the eval) — composed here
