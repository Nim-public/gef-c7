# Story State — Chapters, World, Options

**What you'll learn:** the state schema for an interactive story: what
persists across human pauses, what the model generates, and the option
contract that makes choices structured.

## 1. The state

```python
from typing_extensions import TypedDict, Annotated
import operator

class StoryState(TypedDict):
    premise: str
    world: dict                      # the mutable world JSON
    chapters: Annotated[list[str], operator.add]   # accumulate
    options: list[str]               # current choices (overwritten)
    chosen: str                      # the human's pick
    done: bool
```

| Field | Reducer | Why |
|---|---|---|
| `premise` | overwrite | fixed at start |
| `world` | overwrite (whole JSON) | the model rewrites it coherently |
| `chapters` | append | stories accumulate |
| `options` | overwrite | current fork's choices only |
| `chosen` | overwrite | set by the human |

The world-as-JSON is the interesting design choice: instead of tracking
facts piecemeal, each generation rewrites a *whole world document* —
coherence by construction, validated by a schema (Pydantic, file 01).

## 2. The nodes

```python
def generate_chapter(state: StoryState) -> dict:
    chapter, options, world = llm_story_step(
        state["premise"], state["world"], len(state["chapters"]))
    return {"chapters": [chapter], "world": world, "options": options}

def apply_choice(state: StoryState) -> dict:
    world = apply_world_update(state["world"], state["chosen"])
    return {"world": world, "chosen": ""}      # consumed
```

Three nodes and two edges make the game: `generate → (pause) → apply →
generate …` with the END edge when the story completes. The pause is
file 02's subject; the application is file 03's.

## 3. Options as structured output

```python
class StoryStep(BaseModel):
    chapter: str
    world_update: dict
    options: list[str] = Field(min_length=2, max_length=4)
```

`options` constrained 2–4 keeps the human's choice manageable; the
schema is the UI's contract (a Gradio radio group renders it directly —
the W9 explorer pattern, one more surface).

## Exercises

1. Build the state + two nodes; run one full generation; verify the
   world JSON evolves coherently across 3 chapters.
2. Schema drill: constrain options 2–4; prompt the model to emit 6; the
   schema must clamp or reject — validation at the seam.
3. Session drill: pause mid-story (file 02's pattern), resume in a
   *new process*; the world and chapters survive — checkpointing proof.

## Pitfalls

- Piecemeal world updates (model patches facts) — contradictions
  accumulate; whole-document rewrites stay coherent.
- Unbounded `chapters` — the bounded reducer (file 03) caps the story;
  cap and finish gracefully.
- Options without the length bound — 9-option walls kill interactivity;
  the schema is the UX.