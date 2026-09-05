# Checkpointers — Threads, Durability, Storage Choice

**What you'll learn:** the checkpoint layer: what a checkpoint holds,
the thread_id identity model, storage backends by durability need, and
the retention discipline.

## 1. What a checkpoint is

```python
config = {"configurable": {"thread_id": "task-3"}}
graph.invoke(inputs, config)          # writes checkpoints at each super-step

snap = graph.get_state(config)
snap.values        # full state
snap.next          # next node(s)
snap.config        # the checkpoint's own config (for forking — file 04)
```

A checkpoint is a full state snapshot taken *between nodes* — the
resume point, the replay point, and the fork point. Threads (thread_id)
own checkpoint sequences; one thread = one episode = one resumable
story.

## 2. Storage backends

| Backend | Durability | Use |
|---|---|---|
| `MemorySaver` | process-only | tests, demos in one process |
| `SqliteSaver` | file-persisted | single-machine capstone, demo day |
| `PostgresSaver` | server-grade | multi-user, production-ish |

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("data/checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

The capstone default: **SqliteSaver** — durable across restarts (the
crash drill from the story generator proves it) with zero ops. Postgres
when the demo is multi-user; Memory only for tests, and only because it
is explicit.

## 3. The checkpoint's contents (what durability buys)

| Stored | Enables |
|---|---|
| full state values | resume anywhere |
| next-node pointer | resume *correctly* |
| pending tasks (interrupts) | HITL gates survive restarts |
| history (all checkpoints) | replay and fork (file 04) |

The crash drill is the checkpoint's acceptance test: kill at any point,
resume from the same thread, and the run continues *from the same node*
— not from the beginning.

## 4. Retention and hygiene

| Rule | Why |
|---|---|
| thread per episode | isolation (sessions rule) |
| checkpoint retention window | unbounded history grows forever |
| checkpoints excluded from git | they are runtime data (`data/`) |
| one checkpointer per graph | mixing savers loses history |

```python
# prune: keep last N checkpoints per thread (SqliteSaver needs manual runs)
# document the policy in reports/checkpoint-policy.md
```

## Exercises

1. Run a task with MemorySaver; kill the process; confirm state is gone
   (the negative proof). Repeat with SqliteSaver; confirm resume.
2. Thread-isolation drill: two threads, interleaved invocations; verify
   no state bleed.
3. Policy drill: write `reports/checkpoint-policy.md` (backend, thread
   scheme, retention); implement the prune command.

## Pitfalls

- MemorySaver in the demo and a crash in the demo — durability is the
  *point*; Sqlite minimum for anything you show.
- Thread ids reused across tasks — history bleeds; slug per episode.
- Checkpoint files committed to git — runtime data belongs in `data/`
  (the .gitignore already covers it).