# 06.4 — The Integration Seam

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-huggingface-integration.md](../06-capstone-task-huggingface-integration.md)

---

## What you'll learn

- The contract-first integration: typed inputs/outputs, error behavior, provenance
- Where the component sits in the capstone pipeline (the seam definition)
- The W4 handoff: what the retrieval system consumes from this component
- Monitoring hooks from day one (W10-04's instrumentation, component edition)

## 1. The contract (write it before the code)

```python
from dataclasses import dataclass, field

@dataclass
class ClassificationResult:
    label: str                 # one of the model's label set
    confidence: float          # 0-1, model score
    model: str                 # pinned model id
    revision: str              # pinned revision
    low_confidence: bool       # the W5-04 escalation flag

def classify_ticket(text: str) -> ClassificationResult:
    """Route a support ticket.

    Input: raw ticket text (any length; truncated at 512 tokens).
    Output: ClassificationResult.
    Errors: empty text -> label='empty'; model load failure -> raises.
    """
    ...
```

The contract answers, before implementation: what goes in, what comes out, what happens on the edge cases. Every downstream consumer (the W3 bot, the W4 router, the W13 graph) codes against this contract — not against the model.

## 2. Provenance in every result

| Field | Source | Consumer |
|---|---|---|
| `model`, `revision` | the pin (file 02) | audit, rollback (E8-01) |
| `confidence` | softmax score | routing, escalation (W5-04) |
| input hash | fingerprint (W1-04) | dedup, eval joins (W16-01) |
| latency | measured | SLA tracking (W15-05) |

Provenance is what makes the component *debuggable*: a wrong answer in production traces to (model, revision, input hash) — and the input hash joins the trace to the eval set (W16-01's seed-and-grow).

## 3. The pipeline position (the seam)

```
W4 ingestion ─► corpus ─► [THIS COMPONENT: classify/route/mask] ─► W4 retrieval ─► answers
```

The seam questions (answered in the README, not improvised):

- What does the component receive — raw text, cleaned text, or chunks?
- What does it emit — labels only, or labels + spans + scores?
- What consumes its output — the router (W6-04), the guardrails (W5-04), the retriever?
- What happens on failure — empty label, escalate, or raise?

Each answer is a design decision with tests (file 03's rubric) — the seam is where components meet, and seams are where systems fail.

## 4. Monitoring hooks from day one

```python
import json, time

def monitored_classify(text: str) -> ClassificationResult:
    t0 = time.perf_counter()
    result = classify_ticket(text)
    log_event({                                   # W10-04's JSONL, component edition
        "component": "classifier", "model": result.model, "revision": result.revision,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        "label": result.label, "confidence": result.confidence,
        "input_chars": len(text)})
    return result
```

The hooks are three lines now and the difference between debuggable and mysterious later (W10-04's argument). Log: latency, confidence, model/revision, input hash — and the events feed W16-01's eval growth (E8-02's shadow data).

## Exercises

1. Write the contract (dataclass + docstring) for your component *before* implementing; implement to the contract.
2. Edge-case conformance: empty input, 10k-char input, non-English, emoji-only — verify each behavior matches the contract's error section.
3. Provenance test: two calls with the same input → identical provenance fields; change the revision → provenance changes (and only provenance).
4. The seam test: wire the component into your W3 bot (or a stub); verify the consumer only uses contract fields — no reaching into model internals.
5. Monitoring conformance: the log schema matches the W10-04 events; one week of simulated events loads into the W16-01 eval format.

## Pitfalls

- **Consumers reaching into internals** — if the bot reads `clf.model.config`, the seam is broken; the contract is the only surface
- **Contract drift** — implementation and documented contract diverge silently; the docstring and tests assert the same thing
- **Version omitted from results** — results without model/revision are unauditable (W2-01's pin rule, contract edition)
- **Error behavior undocumented** — "it raises sometimes" is not a contract; the error section lists every case
- **Monitoring added after the incident** — hooks are day-one (W10-04's instrumentation), not post-mortem

## Resources

- W2-06 parent (the protocol), W10-04 (instrumentation), W16-01 (versioning) — composed here
- W4-01/W13-03 (the consumers of this contract)
- [dataclasses docs](https://docs.python.org/3/library/dataclasses.html) — the contract vehicle
