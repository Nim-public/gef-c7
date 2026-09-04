# 02.5 — Encoder vs LLM: The Measured Decision

> Subfolder index: [README.md](README.md) · Parent: [../02-ready-to-use-models.md](../02-ready-to-use-models.md)

---

## What you'll learn

- The benchmark protocol: same cases, both systems, honest numbers
- The cost model with real math
- The hybrid architecture (route by confidence/difficulty)
- The decision table for your capstone

## 1. The benchmark protocol (both systems, same cases)

```python
import json, time

CASES = json.load(open("eval/tickets40.jsonl"))       # 40 labeled cases (W2-06 §4)

def bench(system_fn, name):
    latencies, results = [], []
    for case in CASES:
        t0 = time.perf_counter()
        out = system_fn(case["input"])
        latencies.append(time.perf_counter() - t0)
        results.append(out)
    correct = sum(r == c["expected"] for r, c in zip(results, CASES))
    return {"system": name, "accuracy": correct / len(CASES),
            "p50_ms": round(sorted(latencies)[len(latencies)//2] * 1000, 1),
            "p95_ms": round(sorted(latencies)[int(len(latencies)*0.95)] * 1000, 1)}

encoder_fn = lambda t: clf(t[:512])[0]["label"]          # W2-02 pipeline
llm_fn     = lambda t: llm_classify(t)["category"]       # W3-01 zero-shot

print(bench(encoder_fn, "encoder"))
print(bench(llm_fn, "llm-zero-shot"))
```

The protocol rules (W5-05/W16-01 discipline): same cases, same decision rule, frozen settings, n reported. Latency percentiles, not averages — the tail is what users feel.

## 2. The cost model with real math

Per 1,000 tickets (100 tokens each):

| Component | Encoder (self-host) | LLM API (4o-mini) |
|---|---|---|
| compute | ~0 (amortized CPU) | 100k in + 30k out ≈ $0.023 |
| infra | one always-on CPU core | none |
| at 1M/day | ~1 core + ops | ~$23/day ≈ $700/mo |

The encoder's "free" is amortized infra — the honest framing is *marginal cost per ticket ≈ 0* vs *marginal cost per ticket ≈ $0.02–0.05*. At 1M/day the delta is $20k+/mo — which is why the W15-04 router exists.

## 3. The hybrid architecture (route by confidence/difficulty)

```python
def classify(text: str) -> dict:
    enc_out = clf(text[:512])[0]                     # cheap, fast, first
    if enc_out["score"] >= 0.85:
        return {"label": enc_out["label"], "via": "encoder"}     # confident → done
    llm_out = llm_classify(text)                     # only the hard tail
    return {"label": llm_out, "via": "llm"}
```

Calibrate the confidence threshold on your labeled data (W5-04 ex. 3's reliability diagram): pick the encoder-score cutoff where the encoder's precision on *its own confident subset* equals your quality bar. Measure the escalation rate — if >30% escalate, the encoder isn't earning its keep; if <5%, maybe you can lower the threshold.

## 4. The decision table (measured, for your capstone)

| Dimension | Encoder | LLM API | Your measurement |
|---|---|---|---|
| accuracy (40 cases) |  |  |  |
| p50/p95 latency |  |  |  |
| $/1k tickets |  |  |  |
| label-set flexibility | fixed | dynamic |  |
| determinism | same in → same out | sampling variance |  |
| explanation | none | can explain |  |

Fill the last column from your benchmark runs — this table is the W15-04 router's justification and the W2-06 deliverable's comparison section.

## Exercises

1. Run the full protocol (§1) on your 40 cases with both systems — produce the complete decision table (§4).
2. Confidence-calibrated routing: implement §3's hybrid; sweep the encoder threshold ∈ {0.6, 0.7, 0.8, 0.9} — plot accuracy vs escalation rate; pick the operating point.
3. Cost modeling at scale: 1M tickets/day — encoder infra cost vs API cost, with the router's split applied; where's the break-even?
4. Determinism audit: same 40 cases, 3 runs per system — encoder identical every time? LLM drift quantified?
5. Explanation value: for 10 disagreements between the systems, have the LLM explain its label — how often does the explanation reveal a labeling error in *your* gold data? (The baseline itself can be wrong.)

## Pitfalls

- **Comparing systems on different eval sets** — the W1-05 dataset was built for the encoder; the LLM needs the same cases, same gold labels
- **Latency measured cold** — first-call model load vs warm; benchmark warm, report cold separately
- **Escalation logic without logging** — the router's decisions must be observable or it's undebuggable (W10-04)
- **Encoder threshold fixed forever** — drift (W5-02) moves the calibration; re-run the sweep quarterly (E8-02)
- **One system, one eval** — both systems on the same cases, or the comparison is invalid (the W14-04 parity rule)

## Resources

- W2-02 parent (both systems), W1-05 (the classical baseline), W15-04 (router) — composed here
- W16-01 (eval versioning) — the protocol's versioning layer
- [OpenAI pricing page](https://openai.com/api/pricing/) — the cost-model inputs
