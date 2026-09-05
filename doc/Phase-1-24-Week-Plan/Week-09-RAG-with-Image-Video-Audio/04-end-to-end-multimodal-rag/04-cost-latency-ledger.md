# Cost and Latency Ledger — Per-Stage Measurement

**What you'll learn:** the ledger that turns "it works" into "it works at
X ms and $Y per answer": one instrumented harness, per-stage timings, and
the p50/p95 table the decision memo and tool contract cite.

## 1. Instrumenting the pipeline

```python
import time
from contextlib import contextmanager

STAGES = ["route", "retrieve", "hydrate", "generate", "audit"]

@contextmanager
def stage(name: str, ledger: dict):
    t0 = time.perf_counter()
    yield
    ledger.setdefault(name, []).append((time.perf_counter() - t0) * 1000)

def answer_measured(query: str) -> dict:
    led = {}
    with stage("route", led):
        r = route_query(query)
    with stage("retrieve", led):
        hits = retrieve(query, k=12)
    with stage("hydrate", led):
        hits = [hydrate(h["unit_id"], h["score"]) for h in hits]
    with stage("generate", led):
        resp = answer(query)               # inner stages re-measured separately
    with stage("audit", led):
        ok = resp.get("audit", {}).get("ok", True)
    resp["ledger"] = {k: round(v[-1], 1) for k, v in led.items()}
    return resp
```

The ledger travels *with the response* — every answer carries its own
timings, which is what makes the p95 table honest (no cherry-picked
demo runs).

## 2. The ledger table (commit it per eval run)

| Stage | p50 ms | p95 ms | Notes |
|---|---|---|---|
| route | 0.1 | 0.2 | regex |
| retrieve (P1) | 14 | 31 | 3 searches + RRF |
| retrieve (P3) | 9 | 22 | CLIP path only |
| hydrate | 3 | 6 | batched join |
| generate (P1) | 380 | 620 | LLM summary |
| generate (P3) | 2400 | 4100 | VLM, 2 images |
| audit | 0.3 | 0.5 | regex |

Read rule: the *tail* is the contract number — Week 10's agent budgets
p95 × expected chain depth, never p50.

## 3. Cost columns

| Stage | Unit cost | Per answer |
|---|---|---|
| P1 generate | LLM API $/1k tokens | ~$0.002 |
| P3 generate | tokens × VLM pricing | ~$0.02 |
| embedding (query) | local | ~0 |

The quota's purpose becomes a dollar line: P3 at 10% of 1k answers/day =
$20/day vs $2 all-P1. The memo quotes both.

## Exercises

1. Instrument the full path; run your 25-query set twice; produce the
   p50/p95 table per mode; verify run-to-run p95 drift <20% (else find the
   warm-up pollution).
2. Chain simulation: 3 calls per agent turn × p95 — write the latency
   budget a Week-10 agent can promise.
3. Cost model: compute daily cost at your demo's query rate for
   (a) current quota, (b) no quota, (c) P1-only; the memo cites (a) with
   (c) as the floor.

## Pitfalls

- Measuring generate inside the same stage as retrieval — separate stages
  or the table is unattributable.
- p95 from fewer than 20 samples — unstable; your 25-query set ×2 runs is
  the floor for a first table.
- Quoting laptop numbers for the deployed app — re-measure post-deploy
  (W9 file 01 exercise 4's discipline).

## Resources

- Your deployment latency report (W9 file 01) — the local vs deployed
  comparison this ledger extends.
- The tool contract (W9 file 01) — the consumer of these numbers.
