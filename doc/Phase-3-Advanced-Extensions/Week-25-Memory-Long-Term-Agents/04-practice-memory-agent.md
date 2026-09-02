# 04 — Practice: The Memory-Augmented Agent

> E9 index: [README.md](README.md) · **Due: before E10**

*(Practice build — the capstone agent gains designed, persistent, privacy-gated memory — and the moving-baseline evaluation that comes with it.)*

---

## 1. Deliverable

```
memory-agent/
  memory/
    lifecycle.py           # propose → validate → store → retrieve → update → decay → delete (E9-03 §1)
    policies.py            # write gates, sensitive tiers, authority table (§2/§4)
    consolidation.py       # decay + consolidation job (E9-03 §3)
  agent.py                 # W11/W14 agent with memory pages (E9-01's hierarchy)
  eval/
    moving_baseline.py    # distributional eval (E8-04's bridge question, implemented)
    results.md            # memory value table + privacy audit
  README.md               # design, policies, privacy line
```

Demo: a 3-session conversation — the agent recalls a preference from session 1 (session 2), applies a *reversal* (session 3), and answers a question that requires consolidated memory — plus one privacy drill (erasure) and one memory-poisoning defense.

## 2. Requirements (graded)

### Memory design (E9-03)
- [ ] All seven lifecycle stages implemented and logged (provenance on every memory)
- [ ] Authority table + `reconcile` conflict resolution demonstrated (preference reversal, fact-vs-fact, user-vs-agent)
- [ ] Sensitive-topic write gate with encrypted tier; erasure across all tiers verified by retrieval probe

### Agent integration
- [ ] Memory pages (core/recall/archival) budgeted per turn (W10-05) — page-in logs shown
- [ ] Consolidation job: ≥10 episodes → semantic memory with provenance (E9-03 §3)
- [ ] Cross-session persistence verified after a process restart (durable checkpointer/backing store)

### Evaluation (E8-04's moving baseline)
- [ ] Memory value table: task success with memory vs without, on preference-reliant and fact-reliant tasks
- [ ] Distributional baseline: weekly rolling eval (W16-01's slices over time) — the agent's behavior tracked across 3 evaluation weeks (simulated)
- [ ] Privacy audit: 10 borderline disclosures — storage tier and retrieval visibility per one; zero cross-tenant leaks

## 3. Rubric

| Area | Weight |
|---|---|
| Memory lifecycle completeness (7 stages, provenance) | 25% |
| Policies (write gates, authority, sensitive tiers) | 25% |
| Agent integration (budgets, paging, persistence) | 20% |
| Moving-baseline evaluation | 20% |
| README (design + privacy) | 10% |

## 4. README design sections (answer explicitly)

1. **Memory schema**: tiers, fields, provenance format — and the policy table (E9-01 §2)
2. **Conflict resolution**: your authority table + 3 real reconciliations from the demo
3. **Privacy architecture**: the sensitive-topic line, encryption tier, erasure — with the drill results
4. **The memory value table**: what memory *buys* (measured) vs its cost (tokens, complexity, privacy surface)
5. **E10 bridge**: your capstone's final benchmark claim — which benchmark (task-specific? agent? domain?) would you submit it to, and what would a reviewer attack first? (E10's literacy, pre-applied.)

## 5. Stretch (pick one)

- Letta migration: move your memory implementation onto Letta's primitives (E9-01) — what did the framework add/hide vs your hand-rolled lifecycle?
- Forgetting curve: implement SpacingRepetition-style decay (E9-03 §3) with real usage logs — retrieval precision before/after
- Cross-agent memory: two agents (triage + analytics) sharing an archival store with tenant scoping — the W14-05 topology, memory edition

Bring the memory value table to your next mentor session: "the agent remembers" is only a demo until the value table shows what memory buys, what it costs, and what the privacy line protects.
