# Extension E10 — Specialization & Benchmark Literacy

> Extensions overview: [../README.md](../README.md)

**Builds on:** everything — this is the capstone-and-beyond week.

**Practice build:** [04-capstone-future-roadmap.md](04-capstone-future-roadmap.md)

---

## Why this extension matters

The program taught you to *build*; this week teaches you to *evaluate claims and keep learning* — the two skills that outlast any framework. **Benchmark literacy**: reading MMLU/SWE-bench/arena scores without being fooled, and choosing the benchmark that matches your claim. **Interpretability basics**: opening the model's reasoning enough to debug and defend it. **A research workflow**: tracking the field, reading papers efficiently, and turning findings into capstone improvements.

## What you will be able to do after this week

- [ ] Read a benchmark claim and identify what it does and doesn't establish
- [ ] Match your capstone claims to appropriate evaluation designs (task-specific > leaderboard)
- [ ] Run a basic interpretability probe (attention inspection, logit lens) on your own agent
- [ ] Maintain a research-tracking workflow that turns papers into capstone improvements
- [ ] Plan the capstone 2.0 roadmap: what to build next, in which specialization

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-benchmark-literacy.md](01-benchmark-literacy.md) | Benchmarks, contamination, arena, task-eval design | 3 h |
| 2 | [02-interpretability-basics.md](02-interpretability-basics.md) | Attention analysis, probing, logit lens on your agent | 3 h |
| 3 | [03-staying-current.md](03-staying-current.md) | Paper-reading workflow, source tracking, eval-driven adoption | 2–3 h |
| 4 | [04-capstone-future-roadmap.md](04-capstone-future-roadmap.md) | Capstone 2.0 + specialization tracks | 2 h |

## Self-check before "graduation"

1. A vendor claims "SOTA on MMLU". Name three things that claim does *not* tell you about your capstone.
2. Your agent cites a doc that doesn't contain the quoted sentence. Which W16/E-week artifact would have caught it — and why didn't it?
3. Interpretability probe: your agent routes "billing" questions wrong for non-English tickets. What would you look at first — attention maps, embeddings, or the routing classifier's inputs?
4. Two papers this month claim retrieval improvements. What's the minimum experiment you'd run before adopting either? (Your W4-05 harness answers this — state the protocol.)
5. What's the single highest-leverage skill gap *you* have after 26 weeks — and what's the first artifact that closes it?
