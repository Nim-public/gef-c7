# Deep-Dive: Project — Story Generator (Interactive Graph)

Parent overview: [`../02-project-story-generator.md`](../02-project-story-generator.md)

The story generator is the canonical *interactive* graph: generate →
WAIT for human choice → apply → loop. This subfolder builds the state,
the WAIT pattern, the choice-application node with fallbacks, and the
transferable shape behind interactive flows.

## File map

| File | What it covers |
|---|---|
| [`01-story-state.md`](01-story-state.md) | Chapters, world, options as graph state |
| [`02-wait-pattern.md`](02-wait-pattern.md) | Pausing for human choice |
| [`03-choice-application.md`](03-choice-application.md) | World updates with fallback |
| [`04-transferable-pattern.md`](04-transferable-pattern.md) | Interactive flows generally |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Build order

1. `01-story-state.md` — the state that carries a story.
2. `02-wait-pattern.md` — pausing without threads.
3. `03-choice-application.md` — applying choices safely.
4. `04-transferable-pattern.md` — the pattern everywhere else.

## Prerequisites

- [`../01-langgraph-foundations/`](../01-langgraph-foundations/) — state,
  cycles, bounds.
- [`../06-checkpointing-human-in-loop/`](../06-checkpointing-human-in-loop/)
  — the pause/resume mechanics (built there, used here).
