# HITL Gates — Approval Design and Measured Rates

**What you'll learn:** human-in-the-loop as a *measured* mechanism: which
steps gate, how the approval UI works, and the gate-rate math that keeps
human attention affordable.

## 1. What gates (the triage table)

| Action class | Gate? | Rationale |
|---|---|---|
| read-only retrieval | no | the W9 read-only posture: nothing to approve |
| answer delivery | spot-check | sampled audit, not per-answer |
| first write tool | **always** | new failure class; blast radius |
| spend > $X (API calls) | threshold | cost is a consent boundary |
| corpus mutation | **always + diff** | irreversible without versioning |

```python
GATE_POLICY = {
    "read": False, "answer": "sample", "write": True,
    "spend_over_usd": 0.50, "corpus_mutate": True,
}

def needs_gate(action: dict, policy=GATE_POLICY) -> bool:
    if action["class"] == "write":
        return True
    if action.get("cost_usd", 0) > policy["spend_over_usd"]:
        return True
    return action["class"] == "corpus_mutate"
```

The policy is a committed artifact, like the tool surface: gates are
decisions with reasons, not vibes.

## 2. The gate UX — approve what, with what context

A gate must show, in one screen: the *proposed action* (tool + args),
the *evidence* that led here (last 2 trace steps), the *diff* (for
mutations), and three buttons: approve / edit / reject-with-reason.

```python
def gate_payload(action: dict, trace: list[dict]) -> dict:
    return {
        "action": f"{action['tool']}({action['args']})",
        "evidence": trace[-2:],
        "diff": action.get("diff", ""),
        "options": ["approve", "edit", "reject"],
    }
```

Reject-with-reason is the valuable one: every rejection becomes a
trajectory annotation (file 01's store) — the reason field is training
data for prompt fixes (file 05).

## 3. Gate-rate math — the attention budget

| Metric | Formula | Healthy range |
|---|---|---|
| gate rate | gated runs / total runs | <20% |
| approval rate | approved / gated | >60% (else the policy over-gates) |
| median gate latency | human decision time | <60 s |
| gate value | incidents caught / gates | must be >0, else policy is theater |

```python
def gate_report(runs: list[dict]) -> dict:
    gated = [r for r in runs if r.get("gated")]
    return {
        "gate_rate": len(gated) / max(len(runs), 1),
        "approval_rate": mean(r["gate_outcome"] == "approve" for r in gated),
        "caught": sum(1 for r in gated if r["gate_outcome"] == "reject"),
    }
```

The report runs per eval batch and lands in the same table family as
file 02 — gates are a system component with SLAs, not a ritual.

## 4. Gates in the demo: rehearsed, not improvised

Demo-day pattern: pre-stage one gated action (a write to a scratch corpus
copy), approve it live, narrate the diff. The rehearsal proves the *worst*
path works; un-rehearsed gates are where agents freeze on stage.

## Exercises

1. Write `GATE_POLICY` for your capstone; wire `needs_gate` into the
   loop; verify read-only runs gate nothing (0 gates on 25 runs).
2. Simulated-HITL drill: a "human" that approves 80% / rejects 20%
   (scripted); measure gate rate and approval rate over 50 runs.
3. Reject-reason mining: take 5 scripted rejections; write the prompt-fix
   each reason implies (file 05's input) — the loop that makes gates pay.

## Pitfalls

- Gating reads "for safety" — noise trains humans to rubber-stamp; gate
  by blast radius, not anxiety.
- Gates without measured rates — an unmeasured gate is either dead weight
  or a hidden bottleneck; the report decides which.
- Reject reasons discarded — they are the cheapest alignment signal you
  will ever collect; annotate and mine them.

## Resources

- Your tool surface (file 03) — the class column of the triage table.
- [`../05-prompt-context-engineering-agentic/`](../05-prompt-context-engineering-agentic/)
  — where reject reasons become prompt fixes.
