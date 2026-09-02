# 06 — Capstone Preparation & Demo Day

> Week 16 index: [README.md](README.md)

**Session topics (W17–24 preview + program close):** *Project teams formation. Introduction to roadmap, learning path & expectations + mentoring structure & pitching overview. Session on deployment. 1:1 with mentor to close on project roadmap. Sprint sessions to present Version 1.0. Final project demonstration + Graduation (schedule shared closer to Week 16). Demo Day: top projects and teams demonstrate in front of AI enthusiasts and the ecosystem.*

---

## What this file is

The bridge into the capstone phase: everything W1–16 built, frozen into an architecture, a roadmap, and a demo narrative. Work through this before your 1:1 mentor session — it turns eight weeks of open building into a plan.

---

## 1. The capstone goal (from the program)

> *By the end, a **production-ready, multi-agent AI application** that integrates retrieval ranking, response evaluation, and explainability.*

Score your current capstone against it honestly:

| Requirement | Your current state | Gap |
|---|---|---|
| **Multi-agent** (W10–14) |  | e.g., router→specialist graph exists? |
| **Retrieval ranking** (W4–6, W9, W16) |  | hybrid+rerank evaluated? LlamaIndex decision made? |
| **Response evaluation** (W5, W16) |  | Ragas runs wired into CI? |
| **Explainability** (citations, traces) |  | every answer auditable? |
| **Production-ready** (W15) |  | budgets, retries, tracing, routing measured? |

The gaps list *is* your W17–24 roadmap skeleton.

## 2. The final architecture freeze (do this in the 1:1)

One page, the decisions you've accumulated:

```
DATA:    corpus (W7 manifest) + tables (W6 schema) + multimodal assets (W7)
STORES:  SQLite (W6) + LanceDB multi-vector (W9-02) + FTS
RETRIEVAL: hybrid+rerank (W5-03) [+ LlamaIndex per W16 task] [+ multimodal patterns W9-03]
AGENTS:  framework chosen (W14-06 verdict) + router graph (W13-03) + HITL gates (W13-06)
SAFETY:  W3-02 battery + W5-04 guards + W13-06 interrupts + W15-02 platform filters
SERVING: W15-03 serving config + W15-04 caching/routing + W15-01 budgets
EVALS:   golden set vN (W16-01) + Ragas CI (W15-02) + online 👍/👎 (W9-05)
```

Freeze rule: **architecture freeze at 1:1** — new components need a mentor's yes, because every addition costs integration weeks you now don't have.

## 3. The sprint roadmap (W17–24, eight weeks)

| Sprint | Focus | Exit artifact |
|---|---|---|
| W17–18 | close retrieval + agent core | all four demo pillars working on real data |
| W19–20 | hardening + eval (W15/W16 applied to everything) | regression suite green; metrics table |
| W21–22 | deployment + demo prep (W15 serving; W9-01 UI) | deployed app + demo script |
| W23–24 | polish, rehearsals, **final demonstration + graduation** | demo day |

Each sprint ends with a **pitch** (the mentoring structure): 5 minutes, live system, the metric slide. Rehearse early — W23's demo day is a rehearsal, not the first attempt (file 06's checklist).

## 4. Demo-day checklist (start it now, not W23)

- [ ] **One-line pitch**: "We built X that does Y for Z, evaluated by [metric]"
- [ ] **Live demo path** (3 minutes): the flagship question → grounded cited answer → chart → escalation handled gracefully. *Scripted, rehearsed, with recorded fallback.*
- [ ] **Metrics slide** (file W16-01): the before/after table — the capstone's whole story in one slide
- [ ] **Architecture slide** (W13-03's diagram style): what reviewers will ask about
- [ ] **Failure story**: one thing that failed and how you diagnosed it — the most credible slide in the deck
- [ ] **Live-fallback plan**: recorded demo if the venue Wi-Fi dies (it will try)
- [ ] Deployment: public URL (HF Spaces/W9-01 pattern) or recorded video fallback

## 5. The version 1.0 definition

"Production-ready" for demo day means:

1. Works on **real data end-to-end** (not synthetic-only)
2. **Grounded + cited** answers, with the insufficiency escape firing correctly
3. **Guardrails** active and demonstrated (injection, off-domain, HITL)
4. **Measured**: the metrics table exists and improved over baselines
5. **Deployed** somewhere a stranger can click

Anything beyond that is stretch — cut features, keep the quality bars. (W10-04's three dimensions: demo day judges quality, but cost/latency questions will come.)

## 6. The 1:1 mentor checklist (bring this)

- [ ] Scope doc v3 (W1-08's template, now with the final architecture)
- [ ] Framework verdict (W14-06) + retrieval decision (W16-05)
- [ ] Sprint plan (§3) with dates
- [ ] Metrics baseline (W14-06/W15-05 tables)
- [ ] Demo-day target metric + evidence plan (§4)
- [ ] Risks: top 3 with mitigations (the W1-08 red flags, revisited)
