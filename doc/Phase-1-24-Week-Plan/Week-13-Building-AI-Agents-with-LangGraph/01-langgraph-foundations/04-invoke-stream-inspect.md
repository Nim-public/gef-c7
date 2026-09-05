# Invoke, Stream, Inspect — Reading the Execution Path

**What you'll learn:** the three ways to run a graph and what each
shows: `invoke` for results, streaming for progress, and state
inspection for the execution path — the W10 trace, graph-native.

## 1. The three run modes

```python
# 1. invoke: final state only
result = graph.invoke({"query": q}, config)

# 2. stream: node-by-node updates as they happen
for event in graph.stream({"query": q}, config, stream_mode="updates"):
    print(event)            # {node_name: <partial state update>}

# 3. inspect: the full path after the fact
snapshot = graph.get_state(config)
print(snapshot.next)         # what would run next
print(snapshot.values)       # current state
```

| Mode | Use | W10 equivalent |
|---|---|---|
| `invoke` | eval harness, CI | `Runner.run` |
| `stream` | UIs, progress, first-token | gr.Progress |
| `get_state` / history | debugging, replay (file 06) | trajectory inspection |

## 2. Streaming updates = the live trace

```python
for event in graph.stream(inputs, config, stream_mode="updates"):
    for node, update in event.items():
        print(f"[{node}] {list(update.keys())}")
# [classify] ['query_class']
# [retrieve] ['retrieved']
# [answer]   ['answer']
```

The stream *is* your trajectory capture — node name + partial state per
step. The W10 trajectory schema fills from here exactly as it did from
spans (W11 file 05-03): steps, tools, tokens — same store, new capture.

## 3. Inspecting state mid-run and after

```python
snap = graph.get_state(config)
snap.values          # the full current state
snap.next            # the node(s) that would run next
snap.tasks           # pending tasks (interrupts live here — file 06)

hist = list(graph.get_state_history(config))
len(hist)            # every step's snapshot — the full execution path
```

`get_state_history` is the time-travel substrate (file 06): every
checkpoint, in order, with the next-node pointer. For debugging: find
the last snapshot before the failure, read its state — the exact W10
bisect, one API call.

## 4. Configs: thread_id and the run identity

```python
config = {"configurable": {"thread_id": "eval-task-3"}}
result = graph.invoke(inputs, config)
```

`thread_id` is the session key (W11 sessions' equivalent) — it scopes
checkpointing, history, and interrupts. The trajectory store's
`session_id` maps to it; the pin note records the mapping.

## 5. The three-views parity test (the capture contract)

```python
def test_three_views_agree(config):
    final = graph.invoke(inputs, config)                       # view 1
    stream_events = list(graph.stream(inputs, config,
                                      stream_mode="updates"))  # view 2
    hist = list(graph.get_state_history(config))               # view 3
    steps_invoke = len([k for k in final if final[k]])
    steps_stream = len({n for e in stream_events for n in e})
    steps_history = len(hist) - 1
    assert abs(steps_invoke - steps_history) <= 1
```

The three views (result, live, record) must agree on the step count —
the W11 capture-parity test, graph edition. When they disagree, one
capture is wrong, and the merge into the trajectory store inherits the
lie.

## Exercises

1. Run one task three ways (invoke/stream/history); produce the three
   views of the same run; verify the step counts agree.
2. Stream-drill: build the live-trace printer; feed a multi-hop query;
   confirm the node sequence matches the W11 trace for the same query.
3. History drill: run a failing task; use `get_state_history` to find
   the pre-failure snapshot; name the failing node from `next`.
4. Parity drill: implement the §5 test; run over 5 tasks; document any
   systematic gap (retry turns are the usual suspect).

## Pitfalls

- Streaming as the *only* capture — stream events are transient; the
  store keeps the row (W11's parity lesson).
- Thread ids reused across eval tasks — session isolation is the
  thread_id's job; slug per task.
- Reading `snapshot.values` as immutable truth — it is the *current*
  state; history is the record.