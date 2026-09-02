# 06 — Checkpointing, Human-in-the-Loop & Time Travel

> Week 13 index: [README.md](README.md)

**Optional deepening** — the session topics don't list this explicitly, but the router/codegen projects need it the moment they leave the demo stage. LangGraph's persistence layer is the cleanest HITL mechanism in the program, and it formalizes the W10-04 approval gates.

---

## What you'll learn

- Checkpointers: what persists, when, and why every graph in production needs one
- Interrupts (`interrupt_before`/`interrupt_after`) — pausing a graph for human approval
- Resuming runs; time-travel debugging (replay from any checkpoint)
- The W10-04 HITL pattern, graph edition

## 1. Checkpointers: the graph's save system

A **checkpointer** saves the full state after every super-step, keyed by a `thread_id` (a conversation/run id):

```python
from langgraph.checkpoint.memory import MemorySaver      # demo; use SqliteSaver/Postgres in prod
# from langgraph.checkpoint.sqlite import SqliteSaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

cfg = {"configurable": {"thread_id": "ticket-1001"}}
result = app.invoke({"ticket": "charged twice"}, cfg)    # state saved under ticket-42
```

What this buys (each is a production requirement you already justified):

| Feature | W10 analog |
|---|---|
| crash recovery (resume mid-graph) | JSONL run logs, now executable |
| multi-turn state per conversation | W1-07 history, graph-native |
| pause/resume for HITL | W10-04's approval gates |
| audit ("what did the graph see at step 3?") | W10-04 traces, queryable |

Durable backend (`SqliteSaver("checkpoints.db")`, Postgres) for anything that survives a restart — `MemorySaver` is for labs only.

## 2. Interrupts: HITL as a graph property

Pause *before* a sensitive node executes, get human approval, resume:

```python
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["issue_refund"],     # pause before this node runs
)

cfg = {"configurable": {"thread_id": "t-1001"}}
app.invoke({"ticket": "…refund request…"}, cfg)      # runs until issue_refund, then stops

# inspect what WOULD happen:
state = app.get_state(cfg)
print(state.next)                                    # ('issue_refund',)

# human approves (or edits state) → resume:
app.invoke(None, cfg)                                # None = continue from checkpoint
```

This is W10-04's `maybe_execute` pattern, upgraded: the graph *stops*, the full state is durable, and approval is a state inspection + resume rather than an inline `input()`. The approval UI can live anywhere (Gradio button, Slack) — it just resumes the thread.

```python
# editing state before resume (human corrections):
app.update_state(cfg, {"ticket": "…sanitized ticket text…"})
app.invoke(None, cfg)
```

## 3. Time travel — debugging by rewinding

Because every super-step is checkpointed, you can **fork a run from any past state**:

```python
history = list(app.get_state_history(cfg))   # all checkpoints, newest first
for s in history:
    print(s.metadata["step"], s.next, list(s.values.keys())[:3])

# re-run from an earlier checkpoint as if the mistake never happened:
past = history[3]
app.invoke(None, {"configurable": {"thread_id": cfg["configurable"]["thread_id"],
                                   "checkpoint_id": past.config["configurable"]["checkpoint_id"]}})
```

Debugging workflows this enables: replay the trajectory *from the bad tool call* with a fixed tool; A/B a different edge condition from the same fork; compare counterfactual branches (what if the router had chosen SQL?). The W10-04 "one trajectory = one replayable unit" discipline, native.

## 4. The HITL design (putting it together for the capstone)

| Node type | Interrupt? | Approver |
|---|---|---|
| retrieval, classification | no | — |
| `draft_reply` | interrupt *after* (review the draft) | agent operator |
| `issue_refund`, `send_email` | interrupt *before* | human owner (W10-04's least-power rule) |
| unknown-urgency paths | interrupt (clarify) | end user |

Same metrics as W10-04: approval rate, denials, time-to-approval — all derivable from checkpoint metadata. The `log` reducer field (file 03) plus checkpoints give you a complete, replayable audit trail.

## Exercises

1. Add `SqliteSaver` to your ticket router; run 3 tickets in the same thread — verify state accumulates (conversation memory, file 02's taxonomy).
2. `interrupt_before=["escalate"]`: route a high-urgency ticket; inspect `state.next`; approve; resume. Log the full checkpoint chain.
3. Human-correction drill: interrupt before `draft_reply`, `update_state` with a corrected ticket text, resume — did the draft use the correction?
4. Time travel: from a completed run, fork from step 2 with a different route decision (edit state) — compare final answers of both branches.
5. Budget check: measure per-super-step checkpoint overhead (SQLite) on a 10-node run — is persistence cost acceptable at your capstone's volume?

## Pitfalls

- **`MemorySaver` in production** — process restart = amnesia; durable checkpointer or nothing
- **Interrupts without a resume path** — a paused graph waits forever; every interrupt needs a UI/timeout policy (W10-04's budget-the-interruptions rule)
- **Thread id collisions** — two users sharing a `thread_id` share a *brain*; scope ids per user/session
- **Resuming with stale state after long waits** — data changed mid-approval; re-validate at resume (W6-02's least-power + freshness)
- **Checkpointing sensitive content** — full states include PII that passed through; retention policy for the checkpoint store (W7-01 metadata discipline)

## Resources

- LangGraph [persistence concepts](https://langchain-ai.github.io/langgraph/concepts/persistence/) — checkpointers, threads, resume
- LangGraph [human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) — `interrupt_before`/`interrupt_after`, `update_state`
- LangGraph [time travel how-to](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/) — replay/fork recipes
- W10-04 (HITL design), W13-01 (state model) — the foundations formalized here
