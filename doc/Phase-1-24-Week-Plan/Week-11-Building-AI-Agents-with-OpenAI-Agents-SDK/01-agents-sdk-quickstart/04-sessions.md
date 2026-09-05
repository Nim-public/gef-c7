# Sessions — SQLite Persistence Across Turns

**What you'll learn:** `SQLiteSession` as the host-side history store:
what it persists, the CRUD surface, and how it replaces the history tier
of your W10 memory taxonomy — with the trimming rules still yours.

## 1. The object and its lifecycle

```python
from agents import SQLiteSession

session = SQLiteSession("user_123", "conversations.db")

r1 = Runner.run_sync(agent, "Which chart shows Q3 margin?", session=session)
r2 = Runner.run_sync(agent, "What margin does it report?", session=session)
# r2's model call includes r1's items — "it" resolves
```

Pass the same session to multiple `Runner.run` calls and history carries
across — the W10 episodic/history split, with SQLite doing the storage.

## 2. The CRUD surface

| Operation | Call | Notes |
|---|---|---|
| read all | `await session.get_items()` | ordered list of items |
| append | `await session.add_items(items)` | what the runner does per turn |
| pop last | `await session.pop_item()` | surgical undo of one exchange |
| clear | `await session.clear_session()` | fresh episode, same id |

```python
items = await session.get_items()
print(len(items), items[0])        # e.g., 6 items, first is the user turn
last = await session.pop_item()    # undo a bad exchange before a re-run
```

`pop_item` is the session's best-kept trick: an eval harness can undo its
own last turn between assertions without clearing the episode.

## 3. Session vs your memory tiers (W10 file 03)

| W10 tier | SDK home | Still manual? |
|---|---|---|
| History | `SQLiteSession` | no — persistence is handled |
| Scratchpad | your tool + notes | yes |
| Episodic | your trajectory parquet | yes |
| Semantic | LanceDB | yes |

The SDK handles *storage and replay* of history; it does **not** fit the
context. The fitter (W10 file 05) still runs per step — it just reads
from the session instead of an in-memory list. Session + unbounded
episodes is the new long-context trap, not a solved one.

## 4. Session hygiene rules (the fitter's session clauses)

| Rule | Implementation |
|---|---|
| one session per user/thread | session id = `user_thread` slug |
| episodes, not marathons | clear or rotate at task boundaries |
| trim before the model, not after | fitter reads items, trims, passes trimmed list |
| exclude poison | `include_in_history=False` on fallbacks (W11 file 02) |

```python
items = await session.get_items()
trimmed = fit_history(items, budget=2500)     # your fitter's history rule
result = Runner.run_sync(agent, query, session=session)  # session feeds runner
# note: to *serve* trimmed history, pass items as input instead of session
result = Runner.run_sync(agent, [trim(items), user_msg(query)])
```

The last lines are the pattern that reconciles sessions with budgets:
the session is the *store of record*; the trimmed list is what you *send*.
Sessions persist everything; the model sees the fit.

## Exercises

1. Multi-turn drill: two `Runner.run` calls over one session; print
   `get_items()` after each; identify every item type (user, assistant,
   tool call, tool output) — the wire format, now persistent.
2. Undo drill: run a bad query, `pop_item`, run a corrected one; verify
   the model never saw the bad exchange (check `raw_responses` inputs).
3. Budget drill: grow an episode to 40 items; run with your fitter's
   trimmed-list pattern; confirm tokens-in stays under budget while the
   session retains everything.

## Pitfalls

- Sharing a session across users — session id *is* the isolation
  boundary; slug it per user/thread.
- Assuming the session trims for you — it replays everything; the fitter
  must intervene between store and model.
- Sessions as a semantic-memory substitute — retrieval needs embeddings
  (your LanceDB); SQLite gives you replay, not recall.

## Resources

- SDK sessions guide + `SQLiteSession` reference (context7:
  `/websites/openai_github_io_openai-agents-python`).
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/03-memory-taxonomy.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/03-memory-taxonomy.md)
  — the tiers this file integrates.
