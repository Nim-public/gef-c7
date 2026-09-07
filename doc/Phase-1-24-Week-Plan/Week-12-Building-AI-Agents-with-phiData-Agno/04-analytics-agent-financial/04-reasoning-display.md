# Reasoning Display — Audit Trails in Answers

**What you'll learn:** the answer format that makes the agent's reasoning
auditable: what the user sees, what the reviewer sees, and the structural
fields (`sql_used`, `citations`, `caveats`) that bind claims to evidence.

## 1. The display contract

```python
class AnalysisResult(BaseModel):
    answer: str                          # the claim, units explicit
    sql_used: list[str]                  # the provenance of every number
    rows_considered: int
    citations: list[str]                 # unit_ids for textual claims
    charts: list[str] = []               # artifact paths
    caveats: list[str] = []              # verification flags, gaps
```

| Field | Audience | Rule |
|---|---|---|
| `answer` | user | units stated; no naked numbers |
| `sql_used` | reviewer | every numeric claim maps to a query |
| `citations` | reviewer + user | unit_ids, clickable in your UI |
| `caveats` | everyone | verification flags and gaps, always visible |

The display contract is the W9-04 answer contract, upgraded for
numbers: citations for text, SQL for figures, caveats for honesty.

## 2. Rendering: user view vs reviewer view

```python
def render_user(r: AnalysisResult) -> str:
    lines = [r.answer]
    if r.caveats:
        lines += ["**Caveats:**"] + [f"- {c}" for c in r.caveats]
    return "\n".join(lines)                # clean, honest, no SQL wall

def render_reviewer(r: AnalysisResult) -> str:
    lines = [render_user(r), "", "**Provenance**"]
    for i, q in enumerate(r.sql_used):
        lines.append(f"query {i+1}:\n```sql\n{q}\n```")
    lines.append(f"citations: {r.citations}")
    return "\n".join(lines)
```

Two renderings, one object: the user sees the answer and caveats; the
reviewer sees the full chain. The UI toggles (a Gradio tab, a Playground
expandable) — the *data* is identical, the projection differs.

## 3. Reasoning display vs reasoning transparency (the boundary)

| Show | Don't show |
|---|---|
| SQL used | the model's full chain-of-thought |
| verification verdicts | internal scratchpad text |
| search queries used | other users' data |
| row counts | raw dumps beyond limits |

The audit trail is *structured artifacts* (queries, citations, verdicts)
— not the model's private reasoning. This keeps answers auditable
without shipping your prompt engineering or leaking between sessions.

## 4. The audit trail in the harness (the metrics tie-in)

| Display field | Harness check |
|---|---|
| `sql_used` non-empty when numeric | output guardrail |
| `citations` ⊆ retrieved | the standing citation gate |
| `caveats` present when verification flagged | mismatch-drill rubric |
| `charts` exist on disk | artifact existence check |

```python
def numeric_gate(r: AnalysisResult, context) -> bool:
    numeric = any(ch.isdigit() for ch in r.answer)
    return (not numeric) or bool(r.sql_used)
```

The guardrail is one line: *numbers require SQL provenance* — the whole
file in one assertion, running in the W11 regression suite.

## 5. The display in the demo (the review-day view)

The demo shows both renderings live: user view for the answer, reviewer
view on demand. One toggle proves the whole file — the data is identical,
the audiences are served, and the caveats never disappear.

## Exercises

1. Implement both renderers; verify the reviewer view contains every
   `sql_used` query and the user view contains none.
2. Guardrail drill: craft an answer with a number and empty `sql_used`;
   `numeric_gate` must fail it; add the case to the suite.
3. Caveat-relay drill: trigger a verification mismatch; confirm the
   caveat appears in the *user* view — honesty must be user-visible, not
   reviewer-only.

## Pitfalls

- SQL walls in user view — provenance is for reviewers; the user needs
  the answer and the caveats.
- Caveats as reviewer-only fields — flags that users never see are
  dishonest by omission; render them.
- Audit trails stored outside the trajectory store — the display comes
  from the typed result; the store keeps it queryable.

## Resources

- Your typed-output validators (W11 file 01-03) — the fields' enforcers.
- [`../03-custom-tools-toolkits/03-advanced-data-tools.md`](../03-custom-tools-toolkits/03-advanced-data-tools.md)
  — the tools producing these fields.