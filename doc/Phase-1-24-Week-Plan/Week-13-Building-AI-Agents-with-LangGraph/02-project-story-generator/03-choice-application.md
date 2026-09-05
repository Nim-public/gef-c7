# Choice Application — World JSON Updates with Fallback

**What you'll learn:** applying a free-text human choice to a structured
world: schema-validated rewrites, fallback when the choice is
out-of-distribution, and the coherence rules that keep long stories
sane.

## 1. The application node

```python
def apply_choice(state: StoryState) -> dict:
    pick = state["chosen"]
    if pick in state["options"]:
        world = llm_world_update(state["world"], pick)     # structured path
    else:
        world = llm_absorb_free_text(state["world"], pick)  # fallback path
    return {"world": world}
```

Two paths: choices from the option list take the structured route;
free-text ("I want to befriend the whale instead") takes the fallback —
which must *integrate* the player's idea into the world schema, not
ignore it.

## 2. The world schema (coherence by construction)

```python
class World(BaseModel):
    location: str
    characters: list[str]
    items: list[str]
    mood: str
    open_threads: list[str]      # unresolved plot hooks

    @field_validator("characters")
    @classmethod
    def no_duplicates(cls, v):
        assert len(v) == len(set(v)), "duplicate characters"
        return v
```

| World field | Update rule |
|---|---|
| `location` | set by movement choices |
| `characters` | append new, never silently remove |
| `open_threads` | append on promises, remove on resolutions |
| `mood` | overwritten per chapter |

The validators are the coherence police: duplicates rejected, threads
tracked. Long stories die from dropped threads — the field makes
dropping *visible*.

## 3. The fallback ladder (choice absorption)

| Choice type | Route | Example |
|---|---|---|
| listed option | direct world update | "follow the whale song" |
| free text, in-world | `llm_absorb_free_text` | "befriend the whale" |
| free text, world-breaking | negotiation response | "I become the sea god" → |
| | | "the world resists; here's what you *can* do" |
| incoherent | ask again (loop with counter) | "asdf" → re-prompt |

```python
def apply_world_update(world: dict, choice: str) -> dict:
    for attempt in range(2):
        candidate = llm_world_update(world, choice)
        try:
            return World(**candidate).model_dump()
        except ValidationError as e:
            last = e
    # fallback: keep the world, note the failed choice
    return {**world, "open_threads": world["open_threads"] +
            [f"(unresolved: {choice[:40]})"]}
```

The fallback keeps the *story alive*: a failed integration becomes an
open thread rather than a crash. The player's agency is preserved; the
schema's invariants hold.

## 4. Coherence rules (long-story discipline)

| Rule | Why |
|---|---|
| whole-world rewrite each step | no patch drift |
| threads tracked explicitly | promises kept visible |
| characters never silently vanish | continuity |
| chapter text references world fields | grounding the prose |

The coherence checks run as a post-generation validator — a graph node
that reads the chapter, checks world references, and appends to
`errors` when the text contradicts the world (the loop detector's
story-edition).

## Exercises

1. Implement the application node with the two routes; test all four
   choice types; verify the fallback keeps stories alive.
2. Schema drill: duplicate a character in `world_update`; the validator
   rejects; the retry rewrites — the schema as game master.
3. Thread drill: make a promise in chapter 1 ("I'll return the pearl");
   verify `open_threads` carries it to chapter 4 until resolved.

## Pitfalls

- Free-text choices silently ignored — the fallback absorbs them; the
  player's agency is the product.
- World updates that bypass the schema — coherence dies in five
  chapters; validate at the seam.
- Retry loops without the counter — the incoherent choice loops
  forever; the 2-attempt cap is the bound (file 01-03).