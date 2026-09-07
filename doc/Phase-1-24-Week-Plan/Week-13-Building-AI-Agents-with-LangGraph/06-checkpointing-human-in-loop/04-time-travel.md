# Time Travel — Replay and Fork Debugging

**What you'll learn:** `get_state_history` + `update_state` as the
debugging superpower: replay a run from any checkpoint, fork it with a
changed input, and compare branches — the W10 bisect, now with a rewind
button.

## 1. The history walk

```python
config = {"configurable": {"thread_id": "task-3"}}
history = list(graph.get_state_history(config))
# each entry: a StateSnapshot with .values, .next, .config, .created_at

for snap in reversed(history):        # oldest first
    print(snap.next, list(snap.values.keys())[:3])
```

Every checkpoint is a full state snapshot with its next-node pointer —
the execution path, stored. The W10 bisection (find the last good span)
becomes a loop over this list.

## 2. Replay from a checkpoint

```python
past = history[-3]                    # three steps ago
replay_config = past.config
# re-run from that exact checkpoint:
result = graph.invoke(None, replay_config)
```

Re-running from a past checkpoint replays the *remaining* graph with
that state — deterministic nodes reproduce; model calls re-sample (pin
temperature 0 for reproducible replays). The replay is the post-mortem
workflow (W10 file 05-02, W11 file 06-03) with a native mechanism.

## 3. Forking — change one thing, rerun

```python
before_answer = next(s for s in history if s.next == ("answer",))

fork_config = graph.update_state(
    before_answer.config,
    values={"query": "Which chart shows Q3 EBITDA?"},   # the one change
)
fork_result = graph.invoke(None, fork_config)
```

| Use | Mechanism |
|---|---|
| "what if the query were clearer?" | fork with edited query |
| "was the retrieval the problem?" | fork from pre-retrieval with better terms |
| A/B on one node | fork, compare branches in the store |

The fork creates a *new branch* of history — the original run is
untouched. Branch comparison (same metrics, two outcomes) is the
cleanest counterfactual debugging available anywhere in this program.

## 4. Debugging workflows with time travel

| Question | Tool |
|---|---|
| where did it go wrong? | history walk + `next` pointers |
| would better input have fixed it? | fork with edited input |
| is the failure deterministic? | replay ×5 at temperature 0 |
| what did the state look like *before*? | `snap.values` from history |

The four questions are the W10 post-mortem template, with native
mechanics. The post-mortem artifact gains a fork link: the reviewer can
replay the counterfactual themselves.

## 5. The fork etiquette (branches are data)

| Rule | Why |
|---|---|
| fork with `update_state`, never by editing history | the original run is evidence |
| name the branch intent in the state | `{"fork_reason": "clearer query test"}` |
| compare branches on the same metrics | the counterfactual must be measured |
| prune abandoned forks on the retention schedule | branch sprawl is checkpoint bloat |

Time travel creates *data* — branches are part of the run's record and
follow the retention policy. The post-mortem links both branches; the
store keeps both; the policy cleans them later.

## Exercises

1. Walk the history of a failing run; identify the first bad snapshot;
   replay from one step before — confirm the failure reproduces (or
   doesn't, at temperature 0 vs 0.7).
2. Fork drill: fork a failing run with a corrected query; compare the
   branches' outcomes; commit both branch ids in the post-mortem.
3. Determinism drill: replay the same checkpoint 5×; measure variance;
   classify the failure (logic vs sampling) — the W11 drill, one API
   call now.
4. Etiquette drill: fork three branches for three "what if" questions;
   record each intent; prune the uninformative ones per the retention
   schedule.

## 6. The time-travel pin note

**Task:** extend `reports/sdk-versions.md` with the time-travel stack:
history API usage, fork procedure, retention interplay, and the
determinism-drill command.

**Worked approach:** time travel is the debugging layer's crown — the
pin note records the replay/fork procedure and the drill that proves
branch isolation.

**Pass criterion:** note committed; the determinism drill green as
recorded.