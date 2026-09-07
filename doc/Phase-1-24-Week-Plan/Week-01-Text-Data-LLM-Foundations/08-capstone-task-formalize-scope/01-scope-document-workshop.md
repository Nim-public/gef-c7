# 08.1 — Scope Document Workshop

> Subfolder index: [README.md](README.md) · Parent: [../08-capstone-task-formalize-scope.md](../08-capstone-task-formalize-scope.md)

---

## What you'll learn

- Every section of the scope template, completed for one project with the reasoning shown
- The difference between a scope document and a wish list
- Versioning the scope from day one (W16-01's discipline, applied to plans)

## 1. The worked example (section by section)

Project used here: **"Support-intelligence assistant"** — triage tickets, answer from the knowledge base, surface numbers.

### Problem (2–4 sentences that name a user)

> Support engineers at Acme handle 400 tickets/week across email and portal. Today they triage manually (~6 min each) and search three systems for answers. The assistant triages automatically and drafts grounded replies.

*Why this passes:* a named user (support engineer), a named cost (6 min/ticket), a named scope (triage + replies). "Help people with support" would fail — no user, no cost, no boundary.

### Core capability (one sentence, input → output)

> Given a ticket, produce a category, a priority, and a draft reply with citations.

### I/O modalities

Text in (tickets), structured out (JSON triage + cited draft). Tables needed for volumes. No images/audio in v1 — *explicitly deferred* (that's the modality discipline: name what you're NOT doing).

### Non-goals (the section that saves you)

> No voice interface, no automatic sending, no multi-language in v1, no fine-tuning (prompting + RAG first per W3-05), no Slack integration in v1.

Each non-goal is a decision a reviewer would otherwise discover at week 20.

### Team & cadence

Roles: ingestion (W4 skills), modeling (W2/W5), evals (W5-05/W16-01), demo (W9-01). Two meetings/week, one demo/fortnight. Names, not "the team".

## 2. Section-by-section failure patterns

| Section | Wish-list version | Scope version |
|---|---|---|
| Problem | "Support is hard" | 400 tickets/week, 6 min triage each |
| Capability | "AI-powered assistant" | ticket → category+priority+draft+citations |
| Data | "we'll find something" | 400 tickets exported, schema attached |
| Metrics | "good answers" | ≥85% triage accuracy, faithfulness ≥ 0.9 |
| Non-goals | (absent) | 6 explicit deferrals |

The pattern: **numbers, names, boundaries** — three properties, everywhere.

## 3. Versioning the scope

The scope doc is versioned like the eval set (W16-01):

```markdown
# Capstone Scope v3 — 2026-11-20
## Changes from v2
- Dropped multilingual (no data); moved to v4 candidates
- Added chart-generation after mentor session 2
- Data source switched: portal export (400) instead of crawl (unreliable)
```

Every change names its cause. When a mentor asks "why did you drop multilingual?", the answer is a dated decision, not a memory.

## 4. The scope-review checklist (self-review before the mentor reviews)

- [ ] A user is named, and the cost of the problem is estimated
- [ ] Core capability is one sentence with typed input/output
- [ ] Every modality decision has a deferral note (not just inclusion)
- [ ] Data sources are specific (export paths, schemas) — ≥100 rows already in hand
- [ ] One metric with a target number exists
- [ ] Non-goals listed and defended
- [ ] Every "later" item has a version number where it returns

## Exercises

1. Write the scope doc for your project using the template; then attack it yourself with the checklist — fix every failure before moving on.
2. The wish-list converter: take a friend's vague project idea and convert it to a scoped version — the conversion skill is the deliverable.
3. Version drill: simulate a mentor session (inject 3 changes: drop a feature, switch a data source, add a metric) — produce v2 with the changelog.
4. Boundary stress: for each non-goal, write the one-sentence answer you'd give a stakeholder who asks for it anyway.
5. Compare two scopes (yours + a peer's) against §2's failure table — which wish-list patterns survive in each?

## Pitfalls

- **Scope as a feature list** — features without users, costs, and boundaries are wishes
- **Metrics without targets** — "improve accuracy" vs "≥85% on the held-out set by week 12"
- **Non-goals forgotten** — every unlisted non-goal is a future scope-creep negotiation
- **Data section describing hopes** — "we plan to collect" is not a data source; have rows in hand
- **No versioning** — v1 with no changelog means v2 decisions have no accountability trail

## Resources

- W1-08 parent (the template + worked scopes), W16-01 (versioning), W1-08 §2 (data table) — composed here
- W16-06 (the 1:1 checklist) — where this scope doc goes next
