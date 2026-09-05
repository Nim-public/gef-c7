# Demo-Day Assets — Script, Metrics, Fallback

**What you'll learn:** the demo-day kit: the scripted walkthrough (with
seeded queries and printed evidence), the live metrics overlay, and the
fallback plan for every failure mode — the W9-02/W13-06 demo
discipline, final form.

## 1. The demo script

```python
# scripts/demo_day.py
PILLARS = [
    ("RAG", "Which chart shows Q3 margin?"),
    ("SQL", "What was total revenue in Q3?"),
    ("VOICE", "How do I export my data?"),
    ("HITL", "Ingest the new quarterly report"),
]

for name, query in PILLARS:
    result = run(query)
    print(f"== {name} == mode={result.mode} {result.latency_ms}ms")
    print(render_user(result))
    print(f"citations: {result.citations}\n")
```

| Asset | Rule |
|---|---|
| scripted queries | seeded, reproducible — no typing live |
| evidence printed | citations, SQL, latency per answer |
| run tuples | every generated artifact shows its provenance |
| fallbacks | pre-tested (the W14 degradation drills) |

The demo script is the four-pillars demo (W14 file 06-03) plus the
run-tuple printing — the reviewer sees the answer *and* its provenance
in one screen.

## 2. The metrics overlay (the demo's honesty display)

```text
RAG answer: 2.9s | 4.1k tokens | 3 citations [u042][u047][u051]
SQL answer: 1.4s | 0.9k tokens | verified ✓
```

The overlay is one line per answer: mode, latency, tokens, citation
count, verification status. It is the harness's live projection — the
demo shows the system *and* its measurements.

## 3. The fallback rehearsal (the demo's insurance)

| Failure | Rehearsed fallback |
|---|---|
| model API down | the fallback model (W11) serves |
| a tool errors | the instructive error + partial answer |
| the KB misses | the honest refusal |
| TTS/voice down | the text rendering |
| the projector dies | the committed transcript walks the demo |

The rehearsal is the chaos drills (W15 file 02) run in demo sequence —
every rehearsed failure has a fallback that was *executed* before, not
imagined.

## Exercises

1. Build the demo script; run it end-to-end twice; byte-identical
   outputs (seeded) or explained variance.
2. Overlay drill: verify the metrics line prints for every pillar; the
   numbers match the ledger's p50s.
3. Fallback rehearsal: run the five failure drills in demo order; the
   fallbacks fire visibly; the committed transcript covers them.