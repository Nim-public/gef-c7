# 03 — Staying Current: The Research-to-Practice Workflow

> E10 index: [README.md](README.md)

**Core topics:** *Tracking the field, reading papers efficiently, and turning findings into capstone improvements — without chasing every release.*

---

## What you'll learn

- A source triage system: what to read deeply, skim, or ignore
- The 30-minute paper-reading protocol
- The adoption gate: turning a finding into a measured capstone change
- A weekly routine that keeps you current in ~3 hours/week

## 1. Source triage (the filter that prevents drowning)

| Source | Cadence | Depth |
|---|---|---|
| **HF blogs / OpenAI / Anthropic engineering blogs** | weekly | read fully — practice-oriented, high signal |
| **arXiv (cs.CL, cs.LG)** | weekly skim (abstracts) | deep-read only the 1–2 that hit your roadmap |
| **Twitter/X + LinkedIn ML circles** | daily, 10 min | leads only — verify before believing |
| **YouTube deep-dives (Karpathy, 3Blue1Brown, Welch Labs)** | monthly | watch fully when the topic is on your roadmap |
| **GitHub trending / new model releases** | weekly | note, don't chase |
| **Vendor changelogs** (models you *use*) | on release | read fully — silent changes are your risk (W16-01) |

The rule from W2-01 and W16-01 repeats at research scale: **the only papers that matter this quarter are the ones your eval harness can test.**

## 2. The 30-minute paper protocol

Three passes (Keshav's "three-pass" method, compressed):

1. **Pass 1 (5 min)** — title, abstract, figures, conclusion. Decision: relevant to my roadmap? If no → archive.
2. **Pass 2 (10 min)** — intro, method figures, results tables. Extract: the *one* idea, the *eval setup*, the *cost/conditions*.
3. **Pass 3 (15 min)** — the math/details *only if* adopting. Reproduce mentally: what would I change in my capstone, and what would my harness measure?

Then the adoption gate (W16-01's workflow):

```markdown
## Paper adoption note — <paper>
Idea: <one sentence>
Applies to: <capstone component>
Minimum experiment: <the harness run that would validate it>
Cost: <hours/GPU/$>
Verdict after experiment: <adopted | rejected — with numbers>
```

This is the W5-02 bake-off and W15-05 ledger applied to research: no adoption without a measured run on *your* eval set.

## 3. The weekly routine (3 hours, sustainable)

| Slot | Activity |
|---|---|
| Mon 20 min | skim arXiv abstracts + HF blog → triage into read-now/later/ignore |
| Wed 30 min | deep-read the top paper (protocol §2) → adoption note |
| Fri 30 min | run the minimum experiment from the best adoption note |
| Fri 60 min | capstone improvement sprint (the adopted change, through the CI gates — E8-01) |
| ongoing | changelog watches (models in production); incident post-mortems |

The compounding effect: 4 measured adoptions/month × 12 months = a capstone that improves on evidence, not hype. That habit is the actual E10 deliverable (file 04).

## 4. Signal hygiene (what to distrust)

| Signal | Distrust because |
|---|---|
| benchmark-only posts | contamination + scaffolding (E10-01) |
| demo videos | no error rates; selection bias |
| "10× faster/cheaper" without setup | what mix? what baseline? (W15-03's freeze rule) |
| synthetic evals | W16-02's circular trap |
| hype-cycle absolutes ("RAG is dead") | usually a niche finding oversold (W18-03's balance) |

The verification instinct you've built all program — measure on *your* data, hold out, pin versions — is the filter.

## Exercises

1. Run the triage on one week of sources; produce a read-now/later/ignore list with one-line reasons.
2. Full protocol on one paper relevant to your capstone (any from this course's resource lists); write the adoption note; run the minimum experiment.
3. Build your source list (§1) — 5 blogs, 3 arXiv searches, 2 changelogs — into a feed (RSS/notifications) you can process in 20 minutes.
4. Rejection audit: review your W15-05 optimization ledger's *rejected* hypotheses — what pattern do the rejections share? (Your personal Goodhart detector.)
5. Teach-back: write a 500-word explainer of one paper's idea for your team — the fastest comprehension test there is.

## Pitfalls

- **Shiny-object drift** — adopting every new framework (five in one month — you've seen the temptation, W12–14) instead of deepening measured wins
- **Reading conclusions, skipping conditions** — "X improves RAG" papers always have setup conditions; §2 pass 2 extracts them
- **No adoption gate** — research notes that never become experiments are entertainment
- **Social-media as ground truth** — leads, never evidence
- **Burnout cadence** — 3 h/week sustainable beats 10 h/week for two weeks then nothing

## Resources

- Keshav, *How to Read a Paper* — the three-pass method
- [Hugging Face Daily Papers](https://huggingface.co/papers) · [arxiv-sanity](https://arxiv-sanity-lite.com/) — skim infrastructure
- Karpathy's YouTube + [Zero to Hero](https://karpathy.ai/zero-to-hero.html) — the deep-dive tier
- Your own W4-05/W10-04/W16-01 harnesses — the adoption gate's measuring instruments
