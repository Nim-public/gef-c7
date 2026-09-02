# 03 — Designing Long-Term Memory

> E9 index: [README.md](README.md)

**Core topic:** *Persistent long-term memory — write policies, decay, conflict resolution, privacy — designed, not improvised.*

---

## What you'll learn

- The memory lifecycle: propose → validate → store → retrieve → update → decay → delete
- Conflict resolution when memories contradict (the reversal problem, formalized)
- Decay and consolidation (what fades, what consolidates)
- Privacy architecture for memory (the line, enforced in code)

## 1. The memory lifecycle

```
experience (turn, outcome, user signal)
   │ 1. PROPOSE: extraction candidate ("user prefers X", "fact: Y")
   │ 2. VALIDATE: policy check (sensitive? duplicate? sourced?)     ← your code, not the model's
   │ 3. STORE: typed slot (core/archival) with provenance + timestamp
   │ 4. RETRIEVE: paged into context on relevance (E9-01)
   │ 5. UPDATE: reversals/corrections propagate (W10-02's reversal rule)
   │ 6. DECAY/CONSOLIDATE: stale entries fade or merge
   ▼ 7. DELETE: erasure requests reach every tier (E9-01's pitfall)
```

Every stage is *your* code with explicit rules — the difference between a memory system and a slowly-growing liability.

## 2. Conflict resolution (memories that contradict)

| Conflict | Resolution |
|---|---|
| preference reversal ("no longer Hindi") | **supersede**: replace core entry, keep history in recall |
| fact vs fact ("policy is 5 days" vs "policy is 7 days") | **provenance wins**: newer timestamp + source authority |
| user vs corpus ("user says 5 days", doc says 7) | **corpus for facts, user for preferences** — and surface the conflict |
| two users, shared memory | **tenant isolation** (W5-03) — never share across users |
| agent's own claim vs user correction | **user wins**, log the correction (W16-02's data quality) |

```python
def reconcile(existing: dict, incoming: dict) -> dict:
    """Last-writer-wins by (authority, timestamp); never lose the audit trail."""
    authority = {"user_correction": 3, "doc": 2, "agent_inference": 1}
    if authority[incoming["source"]] >= authority[existing["source"]]:
        return {**incoming, "supersedes": existing["id"]}
    return existing          # keep, but record the rejected claim for review
```

## 3. Decay and consolidation

Not all memories deserve equal persistence:

- **Recency weighting** — retrieval scores decay with age unless *reconsolidated* (used again recently refreshes the score — the SpacingRepetition pattern)
- **Consolidation** — a periodic job compresses related episodic memories into semantic ones (W10-02's taxonomy): ten "user prefers short answers" episodes → one core-memory line with provenance count
- **Reinforcement on use** — memories that get retrieved and *used* (the answer relied on them, no 👎) strengthen; memories never retrieved decay out

```python
def consolidation_pass(memories: list[dict]) -> list[dict]:
    clusters = cluster_by_embedding([m["text"] for m in memories])   # W16-02's dedup, dual-use
    consolidated = []
    for cluster in clusters:
        if len(cluster) >= 3:                                        # repeated pattern → semantic memory
            consolidated.append({"text": summarize(cluster),
                                 "provenance": [m["id"] for m in cluster],
                                 "strength": len(cluster)})
        else:
            consolidated.extend(cluster)
    return consolidated
```

## 4. Privacy: the line, in code

The E9-00 self-check's question deserves an enforced answer:

```python
SENSITIVE_TOPICS = ["health", "relationship", "finance_detail", "legal_trouble"]

def write_gate(proposal: dict) -> bool:
    if classify_topic(proposal["text"]) in SENSITIVE_TOPICS:
        return store_encrypted(proposal)          # encrypted tier, restricted retrieval
    return store_normal(proposal)

def user_erasure(user_id: str) -> None:           # the right to be forgotten
    delete_from("core", user_id=user_id)
    delete_from("archival", user_id=user_id)
    delete_from("recall", user_id=user_id)        # all three tiers (E9-01's pitfall)
```

Rules: sensitive topics → encrypted tier with restricted retrieval; erasure reaches every tier; memory contents never leak across tenants (W5-03); the *policy table* lives in the README (E9-01 §2's discipline).

## Exercises

1. Implement the lifecycle (§1) with all seven stages as functions; run a 30-day simulated usage log through it. Report memory counts per stage over time.
2. Conflict drill: three contradicting preferences (sources: user, doc, agent-inference) — verify `reconcile` picks by authority and keeps the audit trail.
3. Consolidation drill: 12 near-duplicate episodes → 1 semantic memory with provenance; retrieval still finds it (test with the original phrasings).
4. Erasure drill: `user_erasure` across all three tiers — then a retrieval probe; zero leaks = pass. Include the *cache* tier (E9-02's staleness).
5. Privacy line: write your capstone's sensitive-topic list + the enforcement code; test with 10 borderline disclosures (health hints, financial stress, legal mentions).

## Pitfalls

- **Memory without provenance** — unverifiable memories can't be audited, corrected, or erased properly (W7-01's manifest rules, memory edition)
- **Consolidation losing provenance** — merged memories must carry their source ids (§3's `provenance` field)
- **Agent-inferred memories treated as user-confirmed** — the authority table (§2) exists because models infer wrongly; weight accordingly
- **Decay tuned to zero** — memory that never fades drowns retrieval (E9-01's pitfall) — and never fades *compliantly*
- **Testing memory with the same session that wrote it** — cross-session persistence is the feature; test it across sessions and after restarts

## Resources

- Packer et al., *MemGPT* (E9-01) — §5 memory management
- [Letta docs](https://docs.letta.com/) — archival memory + tags/metadata
- W10-02 (taxonomy), W5-03 (isolation), W16-02 (data quality) — composed here
- Zhang et al., *A Survey on the Memory Mechanism of LLM-based Agents* — the formal survey
