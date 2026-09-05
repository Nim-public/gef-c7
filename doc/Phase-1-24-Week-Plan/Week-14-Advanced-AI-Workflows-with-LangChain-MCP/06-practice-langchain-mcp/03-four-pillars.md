# Four Pillars — RAG, SQL, Voice, HITL End-to-End

**What you'll learn:** the demo: four pillars, each shown end-to-end in
five minutes — grounded RAG with citations, verified SQL analytics,
voice interaction, and a human-gated workflow — all from one system.

## 1. The demo script

```python
# scripts/four_pillars_demo.py
PILLARS = [
    ("RAG",     run_rag_query,        "Which chart shows Q3 margin?"),
    ("SQL",     run_analytics_query,  "What was total revenue in Q3?"),
    ("VOICE",   run_voice_query,      "How do I export my data?"),
    ("HITL",    run_gated_flow,       "Ingest the new quarterly report"),
]

for name, fn, query in PILLARS:
    result = fn(query)
    print(f"== {name}: {result.mode} | {result.latency_ms}ms ==")
    print(render_user(result))
```

| Pillar | Shows | Weeks |
|---|---|---|
| RAG | citations, grounding, refusals | 4, 7, 9, 12 |
| SQL | verified numbers, provenance | 6, 12, 13 |
| Voice | the cascade, latency table | 11 |
| HITL | interrupt, approve, resume | 13, 14 |

The demo is the program's face — four pillars, one system, each with
its artifacts (citations, SQL, audio, audit trail) visible.

## 2. The demo's discipline (what makes it reviewable)

| Element | Rule |
|---|---|
| seeded | fixed queries, reproducible outputs |
| measured | the latency table prints per pillar |
| degradable | each pillar degrades visibly if its stack dies |
| auditable | every claim cites its artifact |

The W9-04 metrics demo, W13 accept.py, and the W14 acceptance drill —
merged into one script. The demo runs from a fresh clone (the standing
requirement) and prints its own evidence.

## 3. The failure drills (each pillar dies gracefully)

| Drill | Expected |
|---|---|
| KB down | RAG pillar refuses honestly |
| warehouse down | SQL pillar reports, voice says "data unavailable" |
| TTS down | voice pillar renders text |
| human absent | HITL pillar pauses, resumes later |

The degradation ladder (W8 file 04, W9, W13) applied per pillar — the
demo's last act is killing one component per pillar and showing the
flagged fallback.

## Exercises

1. Build the demo script; run all four pillars; every pillar prints its
   mode, latency, and artifacts.
2. Degradation drill: kill one component per pillar; verify flagged
   fallbacks; restore.
3. Fresh-clone drill: run from a clean clone; the ingest + demo pipeline
   completes under 10 minutes (or the slow stage gets a documented
   cache).

## Pitfalls

- Demos that only show happy paths — the degradation drill is part of
  the demo; the failure is the feature.
- Pillars that share no artifacts — the four pillars are one system; the
  citation a RAG answer shows must be the same unit the store indexes.
- Demo scripts that need "just one tweak first" — fresh-clone or it does
  not exist.