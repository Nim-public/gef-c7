# Extension E9 — Memory & Long-Term Agents

> Extensions overview: [../README.md](../README.md)

**Builds on:** W10-02 (memory taxonomy) · W4 (retrieval) · E8 (moving-baseline question)

**Practice build:** [04-practice-memory-agent.md](04-practice-memory-agent.md)

---

## Why this extension matters

W10-02's memory taxonomy (history, scratchpad, episodic, semantic) described *types*; this week builds the *architectures* that make agents useful over weeks and months: MemGPT/Letta-style hierarchical memory, semantic caching, context compression, and the design of persistent memory that improves without poisoning itself. This also answers E8-04's bridge question: agents that change over time by design need distributional evaluation — and this week builds that too.

## What you will be able to do after this week

- [ ] Explain hierarchical memory architectures (core memory / recall / archival) and their retrieval policies
- [ ] Implement semantic caching (response + embedding-level) with invalidation
- [ ] Apply context compression across long agent runs
- [ ] Design persistent long-term memory with write policies, decay, and privacy controls
- [ ] Evaluate a memory-augmented agent with distributional baselines (moving-target evals)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-memory-architectures.md](01-memory-architectures.md) | MemGPT/Letta hierarchy, write policies, retrieval | 3 h |
| 2 | [02-semantic-caching-compression.md](02-semantic-caching-compression.md) | Response caching, prompt compression, LLMLingua | 2–3 h |
| 3 | [03-long-term-memory-design.md](03-long-term-memory-design.md) | Designing persistent memory: write rules, decay, privacy | 3 h |
| 4 | [04-practice-memory-agent.md](04-practice-memory-agent.md) | Memory-augmented capstone agent (practice) | 4 h |

## Environment setup

```powershell
pip install letta MemoryOS      # Letta = the open MemGPT successor (verify current API)
pip install llmlingua           # compression (W18-03)
```

## Self-check before E10

1. Your agent "remembers" a user preference from 3 weeks ago that the user has since reversed. Which memory component failed — and what write/update policy fixes it?
2. Semantic caching returns a *similar* cached answer for a *different* question. What similarity threshold and cache-key design prevents this?
3. MemGPT's core/recall/archival split maps to which W10-02 rows? Name the retrieval policy for each.
4. A memory-augmented agent's eval baseline moves weekly. What does a static eval set measure in that case — and what must replace it?
5. What's the privacy difference between remembering "user prefers short answers" and remembering "user mentioned their divorce"? Where's your line, and where is it enforced?
