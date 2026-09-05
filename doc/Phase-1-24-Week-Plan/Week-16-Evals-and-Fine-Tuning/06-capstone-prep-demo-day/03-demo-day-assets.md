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

## 5. The demo-day runbook (the minute-by-minute plan)

```text
0:00 welcome + the four-pillar architecture slide (one page)
1:00 RAG demo (seeded query, citations shown)
3:00 SQL demo (query shown, number verified)
5:00 VOICE demo (the cascade + latency overlay)
7:00 HITL demo (the gate, approval, resume)
9:00 the failure drill (one component killed, fallback shown)
10:00 the metrics page (the four pillars' table)
11:00 Q&A (the acceptance command runs live if asked)
```

The runbook is the demo's minute-by-minute plan — every segment timed,
every fallback placed, the Q&A prepared. The acceptance command is the
Q&A's ace: if asked "does it really work", the command runs live.

## 6. The demo-day checklist (the morning-of list)

```text
[ ] accept.py --full green on the demo machine
[ ] the seeded demo run rehearsed twice
[ ] the fallback drills rehearsed (the failure section)
[ ] the artifacts committed (transcripts, charts, tables)
[ ] the overlay numbers matching the ledger's p50s
[ ] the network checked (or the offline path ready)
[ ] the runbook printed (the minute-by-minute plan)
```

The checklist is the demo's pre-flight — seven items, each verifiable
in minutes. The morning-of list exists because demo failures are
environment failures (network, projector, stale state) far more often
than code failures.

## Exercises

1. Build the demo script; run it end-to-end twice; byte-identical
   outputs (seeded) or explained variance.
2. Overlay drill: verify the metrics line prints for every pillar; the
   numbers match the ledger's p50s.
3. Fallback rehearsal: run the five failure drills in demo order; the
   fallbacks fire visibly; the committed transcript covers them.
4. Runbook drill: rehearse the §5 plan with a timer; the segments fit;
   the Q&A's acceptance command rehearsed.
5. Checklist drill: run the §6 list on the demo machine the morning of;
   all seven green before the audience arrives.

## 7. The demo-day pin note (the kit's manifest)

**Task:** extend `reports/sdk-versions.md` with the demo kit: script
version, seed, the overlay's data source, the fallback rehearsal date,
and the runbook location.

**Worked approach:** the kit's manifest records what the demo runs and
when it was rehearsed — the demo's claims auditable down to the seed.

**Pass criterion:** note committed; the rehearsal evidence cited.