# Deep-Dive: Checkpointing & Human-in-the-Loop

Parent overview: [`../06-checkpointing-human-in-loop.md`](../06-checkpointing-human-in-loop.md)

The durability week: checkpointers (threads, storage, durability),
`interrupt_before` approval design, human state edits mid-run, and time
travel — replay and fork debugging.

## File map

| File | What it covers |
|---|---|
| [`01-checkpointers.md`](01-checkpointers.md) | Threads, durability, storage choice |
| [`02-interrupts.md`](02-interrupts.md) | `interrupt_before`, approvals, resumes |
| [`03-state-editing.md`](03-state-editing.md) | Human corrections mid-run |
| [`04-time-travel.md`](04-time-travel.md) | Replay and fork debugging |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-checkpointers.md` — the durability substrate.
2. `02-interrupts.md` — the pause/approve/resume contract.
3. `03-state-editing.md` — corrections, not just approvals.
4. `04-time-travel.md` — replay and fork as debugging tools.

## Prerequisites

- [`../01-langgraph-foundations/04-invoke-stream-inspect.md`](../01-langgraph-foundations/04-invoke-stream-inspect.md)
  — thread configs and `get_state_history`.
- [`../02-project-story-generator/02-wait-pattern.md`](../02-project-story-generator/02-wait-pattern.md)
  — the WAIT pattern this file grounds.