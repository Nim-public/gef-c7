# Exercises — Checkpointing & Human-in-the-Loop

Expanded set with worked approaches. The deliverable: durable
checkpoints with a policy, interrupt-based gates, the edit protocol with
refusals, and a fork-based post-mortem.

## 1. Checkpoint durability (from 01-checkpointers)

**Task:** the crash drill on SqliteSaver (kill mid-run, resume, same
node); the negative proof on MemorySaver (state gone); the
thread-isolation drill (two threads, no bleed).

**Worked approach:** the negative proof matters as much as the positive —
MemorySaver *losing* state is what makes Sqlite's durability meaningful.
The isolation drill is the sessions rule, one more surface.

**Pass criterion:** Sqlite resume from the same node; Memory loses;
threads isolated.

## 2. Interrupt gates (from 02-interrupts)

**Task:** wire `interrupt_before` on the two gated nodes; run the three
decisions (approve/edit/reject) through the resume contract; verify no
advance without a decision (the invariant test).

**Worked approach:** the invariant test (paused until state changes) is
the gate's honesty check — the graph *cannot* advance past a WAIT
without the human's state update.

**Pass criterion:** three decisions exercised; the no-advance invariant
green; the gate policy mapped to the interrupt list.

## 3. The edit protocol (from 03-state-editing)

**Task:** implement the allow-listed edit protocol; run the correction
drill (classification fixed mid-run); run both refusal drills (tool
result, missing reason).

**Worked approach:** the refusals are the policy's teeth — editing tool
results or skipping reasons breaks the audit trail, and the protocol
must say no with instructive errors.

**Pass criterion:** correction lands downstream; both refusals fire;
every edit logged with a reason.

## 4. Fork post-mortem (from 04-time-travel)

**Task:** take a failing run from your eval set; walk the history; fork
with a corrected input; compare branches; commit the post-mortem with
both branch ids.

**Worked approach:** the fork is the counterfactual — "with a clearer
query, does it pass?" answered mechanically. The post-mortem template
(W10/W11) gains the fork link as its evidence.

**Pass criterion:** post-mortem committed with both branch outcomes;
the determinism classification (temperature 0 ×5) included.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Durability proven (positive + negative) | crash drills | 4 |
| Gates: three decisions + invariant test | interrupt tests | 4 |
| Edit protocol + refusals + audit | protocol tests | 4 |
| Fork post-mortem with branch comparison | reports/post-mortem.md | 3 |
| Checkpoint policy page | reports/checkpoint-policy.md | 2 |

**Pass bar:** 15/18 to close Week 13. The durability drill (4-pointer)
is the checkpointing week's foundation — every HITL flow above it
stands on the crash test.

## Pitfalls recap

- MemorySaver in anything you show — the crash drill's negative proof is
  why Sqlite is the floor.
- Resumes with new inputs instead of `None` — that starts a new run; the
  resume contract is `update_state` then `invoke(None)`.
- Forks without branch records — the counterfactual is evidence; commit
  both branches.