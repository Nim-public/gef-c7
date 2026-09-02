# 04 — Capstone 2.0: The Future Roadmap

> E10 index: [README.md](README.md)

**Core topic:** *The post-course roadmap — capstone 2.0 planning, specialization tracks, and the portfolio that compounds.*

---

## What you'll learn

- The specialization tracks your 26 weeks have prepared you for
- Capstone 2.0 planning: the next release of your project as a product
- The portfolio that compounds: artifacts, evidence, and public work
- The gap-closing plan (E10-00's self-check, formalized)

## 1. Specialization tracks (choose your deepening)

Every track extends the same capstone with one deep layer — the W1–16 stack is the base for all of them:

| Track | Deepening | From your stack |
|---|---|---|
| **RAG systems engineer** | GraphRAG at scale, reranker/embedder fine-tuning (E1-04), eval infrastructure as a product | W4–6, W16, E1, E2 |
| **Agent platform engineer** | multi-agent frameworks, MCP tool ecosystems, agent CI (E3-04), reliability (W15) | W10–15 |
| **Applied vision/document AI** | document intelligence pipelines (E4), multimodal RAG (W9), detection/segmentation | W7–9, E4 |
| **Voice & realtime AI** | realtime voice production (E5-03), telephony, voice UX | W8, W11-04, E5 |
| **AI security engineer** | red-teaming as a service, sandboxing, safety evals (E7), compliance | W3-02, W23 |
| **LLMOps/platform** | registries, cost optimization, observability as a product (E8), eval infra | W15, E8 |

The track decision uses the same evidence pattern as every W2-05/W10-04 choice: which track's *first artifact* can you build in 2 weeks with what you already have?

## 2. Capstone 2.0 planning (the product release)

Your W16-06 checklist got the demo ready; 2.0 treats the capstone as a product with users:

| Dimension | 1.0 (demo) | 2.0 (product) |
|---|---|---|
| users | mentors + you | 5–10 real users (pilot) |
| data | your curated corpus | growing corpus + ingestion pipeline (W4-05) |
| evaluation | static harness (W16-01) | online signals + regression CI (E8-02) |
| deployment | Spaces/local (W9-01) | production serving (W15-03) + canary (E8-02) |
| cost | unmeasured | ledger + budgets (E8-03) |
| security | battery (E7) | threat model + sandbox (E7-04) |
| memory | sessions (W11-01) | persistent, policy-gated (E9-03) |

The 2.0 roadmap = the gap column turned into sprints (W16-06 §3's format), each with an exit artifact and a metric. The pilot users are the leverage: real usage logs (W10-04) feed eval sets (W16-01), alignment data (E1-01), and cost models (E8-03) — everything compounds.

## 3. The portfolio that compounds

| Artifact | Where it lives | What it proves |
|---|---|---|
| **The system** (repo + deployed URL) | GitHub + Spaces | you ship end-to-end LLM systems |
| **The eval harness** (harness + results + versioning) | repo `eval/` | you measure before claiming |
| **The security section** (threat model + battery) | repo `security/` | you design for adversaries |
| **The ops manual** (registry, CI/CD, dashboards) | repo `llmops/` | you operate, not just build |
| **Adoption notes** (research → experiments) | repo `research/` | you stay current on evidence |
| **Write-ups** (3–5 technical blog posts) | blog/HF | you communicate — the E10-03 teach-backs |

Each 26-week file you built maps to one of these — the portfolio is the program, reorganized for the outside world. The write-ups (E10-03 ex. 5's teach-backs) are the highest-leverage missing piece for most engineers: the same work, made legible.

## 4. The gap-closing plan (from E10-00's self-check)

| Gap | First artifact that closes it | Week-equivalent |
|---|---|---|
| eval discipline gaps | move all claims to versioned harness runs | W16-01 |
| security evidence | run the E7 practice red-team | E7-05 |
| serving experience | vLLM deployment + benchmarks | W15-03 |
| depth in one framework | contribute/extend one (LangGraph tool, Agno toolkit) | W13/W12 |
| research fluency | 4 adoption notes (E10-03 §2) | E10-03 |

Sequencing rule: close gaps that *block the 2.0 roadmap* first (§2), portfolio gaps second — the product drives the learning, which is the pattern this entire program ran (capstone tasks driving frameworks).

## Exercises

1. Choose the track (§1) with the two-week first-artifact test; write the artifact's spec (one page).
2. Draft the 2.0 roadmap (§2): 4 sprints from the gap column, each with an exit artifact + metric.
3. Portfolio audit: score your current artifacts (§3) 0–5; the two lowest scores are your next two sprints.
4. Write the 2.0 pitch (5 sentences): product, users, differentiator (your measured metrics), architecture, and the next milestone.
5. Publish one write-up (E10-03 ex. 5): the memory-agent value table (E9-04) or the framework verdict (W14-06) — the strongest artifact you have, made legible.

## Pitfalls

- **Track-hopping** — starting all six specializations shallowly; the two-week artifact test forces commitment
- **2.0 without users** — a pilot with zero real users is 1.0 with a roadmap
- **Portfolio as a code dump** — artifacts without write-ups prove nothing to outsiders (§3's legibility rule)
- **Roadmap without metrics** — every sprint needs an exit artifact *and* a number (W16-01's discipline)
- **Learning without shipping** — the compounding portfolio (§3) exists because artifacts shipped beat courses consumed

## Resources

- Everything in `doc/` — the base you're extending
- Anthropic/OpenAI engineering blogs (E10-03's tier-1 sources) — where 2.0 ideas come from
- The W16-06 checklist (§4 of this file's predecessor) — the demo-day foundation 2.0 builds on
- Your own harnesses — the instruments that make capstone 2.0 claims true
