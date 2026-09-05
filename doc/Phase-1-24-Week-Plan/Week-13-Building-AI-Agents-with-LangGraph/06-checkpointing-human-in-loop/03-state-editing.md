# State Editing — Human Corrections Mid-Run

**What you'll learn:** `update_state` as the correction mechanism: fix a
wrong value, inject missing context, or override a bad classification —
with the edits recorded as first-class audit events.

## 1. The mechanism

```python
# mid-run correction: the classifier got it wrong
snap = graph.get_state(config)
assert snap.values["classification"]["category"] == "billing"  # wrong

new_config = graph.update_state(
    config,
    values={"classification": {**snap.values["classification"],
                                "category": "technical",
                                "reason": "human correction: refers to API keys"}},
)

graph.invoke(None, new_config)   # resume from where it paused
```

`update_state` writes a *new checkpoint* with the edit applied — the
correction is part of the history, not an overwrite of it. The
trajectory store gains a `human_edit` event; the audit trail stays
complete.

## 2. What humans may edit (the edit policy)

| Editable | Not editable | Why |
|---|---|---|
| classifications, labels | tool results | results are evidence |
| proposed answers/drafts | embeddings | derived data recomputes |
| priorities, routing hints | hashes, timestamps | identity fields |
| add context (missing info) | *other threads* | isolation |

The policy is the W10 gate table, extended: edits to *content* the human
owns are fine; edits to *evidence* (tool outputs) or *identity* (hashes)
corrupt the audit trail and are refused.

## 3. The edit protocol (what the UI sends)

```python
def apply_human_edit(edit: dict) -> str:
    allowed = {"classification", "proposed_response", "priority", "context_note"}
    field = edit["field"]
    assert field in allowed, f"field '{field}' is not human-editable"
    new_cfg = graph.update_state(CONFIG, values={field: edit["value"]})
    log_edit(edit)                        # trajectory + audit trail
    return new_cfg["configurable"]["checkpoint_id"]
```

| Rule | Implementation |
|---|---|
| edits are allow-listed per field | `allowed` set |
| edits are logged | `log_edit` with reason + editor |
| edits create checkpoints (never overwrite) | `update_state` semantics |
| edited runs re-enter gates | the interrupted node re-checks |

## 4. The correction battery

| Case | Expected |
|---|---|
| wrong classification corrected | downstream nodes see the new label |
| draft answer edited | send uses the edited text |
| edit to a tool result | refused by policy |
| edit without a reason | refused (the reason is the audit) |

The battery is the edit policy as tests — four cases, four refusals or
acceptances, provable.

## Exercises

1. Implement the edit protocol; run the correction drill (wrong
   classification fixed mid-run); verify downstream sees the correction.
2. Refusal drill: attempt to edit a tool result and a timestamp; both
   refused with instructive errors.
3. Audit drill: after 3 corrections, `get_state_history` shows every
   edit as a checkpoint; the trajectory store has the `human_edit`
   events.

## Pitfalls

- Edits applied by overwriting state outside `update_state` — no
  checkpoint, no history, no audit; the API is the only door.
- Edit policies that allow evidence edits — the audit trail becomes
  fiction; the allow-list is the wall.
- Corrections without reasons — the reject-reason mining loop (W10)
  starves; require the reason.