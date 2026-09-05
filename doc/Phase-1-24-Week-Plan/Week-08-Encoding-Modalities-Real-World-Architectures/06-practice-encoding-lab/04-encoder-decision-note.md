# Encoder Decision Note — Capstone Integration

**What you'll learn:** turn the week's labs into the one-page decision memo
that Weeks 09–16 will treat as the source of truth for encoders, fusion,
and the revisit triggers.

## 1. The memo template (fill with your numbers)

```markdown
# Encoder decision — GEF C7 capstone (Week 08)

## Decisions
| Slot | Pick | Runner-up | Deciding number |
|---|---|---|---|
| Image encoder | clip-b32 (512) | resnet-50 | geometry: offdiag 0.61 vs 0.55, R@1 0.42 vs 0.39 |
| Text encoder | minilm-l6 (384) | — | unchanged from Week 04 |
| Audio path | ASR text first, CLAP later | wav2vec2 pool | content lives in words (lab E) |
| Video | frame-12 + CLIP pool-mean | temporal model | static content corpus |
| Fusion | late (rank fusion) | concat head | robustness curve shape |

## Evidence
- Geometry lab: reports/geometry-lab.md (50 images, probes table)
- CLIP matrix: reports/clip-matrix.md (n=214 pairs, R@1 both directions)
- Fusion ablation: reports/fusion-ablation.md (4 cells + robustness curve)

## Revisit triggers
- Screenshot share > 30% → retest OCR-first indexing
- Rerank eval ≥ +2 R@1 → add ITM reranker (week 13)
- Action-heavy video appears → temporal encoder pilot

## Costs (measured)
- Index build: 6.2 min CPU for 214 units
- Query: 35 ms text encode + 12 ms FAISS search
```

Every cell names a *number from your own runs*; every number names the
report that produced it. That is what makes this a decision record rather
than an opinion.

## 2. What the next weeks consume

| Consumer | Field it reads | Why |
|---|---|---|
| Week 09 (audio) | audio path row | builds ASR sidecars per this decision |
| Week 10 (agents) | costs table | plans tool-call latency budgets |
| Week 12 (eval) | fusion row | evaluates *this* fusion, not a fantasy |
| Week 13 (integration) | revisit triggers | the upgrade checklist |

## 3. The discipline of "runner-up" and "trigger"

Two fields make the memo honest: **runner-up** forces you to name what you
rejected and why; **trigger** turns every rejected option into a condition,
not a loss. When Week 13 re-reads this memo, the triggers are the agenda —
and unmet triggers are permission to *not* chase upgrades.

## Exercises

1. Fill the template from your lab reports; every deciding number must trace
   to a committed report file — no "from memory" cells.
2. Swap drill: pick one decision and argue the runner-up in three sentences
   (steelman it); if you cannot, your deciding number was weak — re-measure.
3. Cost check: re-run the index-build timing twice; if the two runs differ
   >20%, find the warm-up pollution (the Week-07 determinism lesson again).

## Pitfalls

- Memo numbers that exist in no report — regenerate or delete; the memo is derived data.
- Triggers without measurement commands — "retest OCR-first" needs the command that would do it.
- Deciding audio/video paths before their weeks' labs — mark them "provisional, confirms week 9/10" rather than pretending.

## Resources

- The lab reports referenced above (all committed under `reports/`).
- Your Week-07 capstone inventory — the memo supersedes its provisional encoder cells.
