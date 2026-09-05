# Observation Formatting — Errors as Instructive Prompts

**What you'll learn:** every observation is a prompt the model reads next:
results formatted for decision-making, errors phrased as guidance — with
the A/B evidence from your own traces.

## 1. Results: format for the next decision

```python
def format_hits(hits: list[dict]) -> str:
    if not hits:
        return ("No units matched. Try broader terms, a different modality, "
                "or check spelling of names/codes.")
    lines = [f"[{h['unit_id']}] score={h['score']:.2f} "
             f"({h['modality']}) {h['text'][:120]}"
             for h in hits]
    return "\n".join(lines) + f"\n[{len(hits)} hits; use get_unit_text for full text]"
```

Three decisions the format must enable: *is anything relevant*, *which id
to read next*, *when to stop*. Scores visible → stop-rule learnable; ids
verbatim → citable; empty-state instruction → the model's fallback is
written for it.

| Element | Why it earns its place |
|---|---|
| `score=0.61` | the model learns its own stop threshold |
| ids as `[u042]` | copy-paste safe for citation and next calls |
| first 200 chars | relevance judgment without full-text cost |
| count tail | sets expectation before the model asks |

## 2. Errors: the three-part hint

Every error observation carries: *what happened*, *what valid input looks
like*, *what to do next*.

```python
def error_observation(e: Exception) -> str:
    if isinstance(e, ValidationError):
        return (f"Invalid arguments: {e.message}. "
                f"Expected: query (string), k (1-20). Fix and retry.")
    if isinstance(e, ToolError):
        return f"{e.hint}"                     # registry's contract hint
    return (f"{type(e).__name__}: {e}. Do not repeat this call unchanged; "
            f"adjust arguments or use a different tool.")
```

The A/B evidence from the foundations file applies here: generic errors
(`"error occurred"`) produce 2–3 extra recovery steps; instructive hints
recover in one. The delta is *your* measurement, not folklore — run the
hint drill from file 02's exercises on your traces.

## 3. Truncation at field boundaries

```python
def truncate_obs(text: str, budget: int = 600) -> str:
    if len(text) <= budget:
        return text
    cut = text[:budget]
    last_nl = cut.rfind("\n")
    return (cut[:last_nl] if last_nl > budget // 2 else cut) + " …[truncated]"
```

The fitter (file 02) sets the budget; this function honors it at
line boundaries. Truncating mid-token or mid-JSON is how observations
become noise; the property test from the fitter exercises (ids/numbers
survive) covers this function too.

## 4. The observation spectrum — one table

| Situation | Observation | Teaches the model |
|---|---|---|
| 0 hits | "No units matched; try X" | fallback behavior |
| 3 hits | scored, id'd lines | ranking trust + stop rule |
| full text too long | field-boundary truncation | what exists beyond |
| wrong arg type | schema + expected types | the schema, in context |
| unknown id | valid id shapes + next action | the corpus's id grammar |
| timeout | "narrow the query" | budget awareness |

Every row is a *prompt-engineering artifact* with a battery case in
Tier 1 — the observation spectrum is where your agent actually learns
the corpus.

## Exercises

1. Implement `format_hits` + `error_observation`; replay three real error
   traces and confirm the new observations are self-explanatory (read
   them cold, as the model must).
2. Format A/B: scored-lines vs prose-paragraph observations on 5
   multi-hit queries; measure steps-to-answer — the format evidence for
   your style choice.
3. Truncation test: craft a 2k-token observation with ids at the end;
   verify `truncate_obs` keeps a citable id or clearly signals absence.

## Pitfalls

- Observations that leak absolute paths or system text — model-visible
  surface; same firewall as prompts.
- Errors as bare exception strings — `KeyError: 'unit_id'` teaches
  nothing; wrap at the registry boundary.
- Truncating the *score* line to save tokens — the stop-rule signal is
  the cheapest token you spend.

## Resources

- [`../02-tools-and-memory/02-tool-registry.md`](../02-tools-and-memory/02-tool-registry.md)
  — the hints this file formats.
- [`../01-agents-foundations/03-demo-trajectories.md`](../01-agents-foundations/03-demo-trajectories.md)
  — the traces that show formatting working.
