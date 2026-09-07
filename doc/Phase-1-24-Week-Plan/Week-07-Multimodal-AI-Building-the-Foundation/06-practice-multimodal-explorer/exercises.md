# Exercises — Practice: Explorer, Audit, Metrics, Inventory

Stretch tasks and the self-review rubric for the week's practice deliverable.
Order follows the build guide; parts A–D map to files 01–04.

## 1. Explorer hardening (Part A stretch)

**Task:** add keyboard-driven review mode: random unit → you tag it
`ok | sideways | black | wrong-license` → labels append to
`data/manifests/review-labels.parquet`. Export a summary count per label.

**Worked approach:** state lives in `gr.State`, not globals (Gradio restarts
state on reload); the label write appends with the same UTC timestamp
convention as the manifest. Twenty labeled units is the target — that is
enough to catch systematic EXIF/alpha bugs, which are never random.

**Pass criterion:** labels file is append-only, never rewritten; summary
regenerates from the parquet alone.

## 2. Audit as a gate (Part B stretch)

**Task:** make `audit_alignment.py` the CI gate for *data* (as tests gate
code): a workflow step runs it and fails on errors; add the JSON output as a
PR comment.

**Worked approach:** the JSON format from file 02's exercise feeds a small
comment-renderer; keep the comment under 30 lines (link to the full report
artifact instead of pasting it). The gate's job is visibility, not prose.

**Pass criterion:** a PR that touches `data/raw/` without re-running ingest
fails the audit with a hash mismatch on the exact units touched.

## 3. Metrics demo with the tail view (Part C stretch)

**Task:** add a "score drift" view: compare this week's mini-run parquet to
last week's by `unit_id` and list the ten biggest CLIPScore changes.

**Worked approach:** the drift list is the early-warning system for silent
preprocessing changes (a settings bump moves scores uniformly; a bug moves
them sporadically — the pattern tells you which happened). Store runs under
versioned filenames (`metrics-mini-run-v3.parquet`) per the alignment
pipeline's stamp discipline.

## 4. Inventory stress test (Part D stretch)

**Task:** simulate Week 08: flip the audio row's sidecar cell from "pending"
to "asr-ready", bump settings version, re-run `emit_inventory` and the
alignment audit. Confirm: inventory updates, audit still gates green, and
the only README diff is the audio row.

**Worked approach:** this is a *rehearsal* of the real Week 08 transition —
20 minutes now, and the eventual transition is mechanical instead of
exploratory. If the audit goes red, the missing step is usually the
sidecar-status field the validation catalog's V8 check expects.

## 5. Self-review rubric (grade yourself before the week ends)

| Criterion | Evidence | Points |
|---|---|---|
| Explorer renders every modality with metadata | screenshot or 3-click walkthrough note | 3 |
| Audit reproducible on fresh clone | timed fresh-clone loop note | 3 |
| Metrics paired with artifacts, tail reviewed | `metrics-notes.md` with 3 diagnoses | 3 |
| Inventory generated, pending cells dated | README diff + script | 3 |
| Tests: parity, audio contract, determinism | green suite in `tests/` | 4 |

**Pass bar:** 14/16 to move to Week 08; anything less, the gap is in
`tests/` (the 4-pointer) more often than not — the suite is the week's real
deliverable because Weeks 08+ refactor on top of it.

## Pitfalls recap

- Review labels stored in the app's memory — state must survive reload; parquet or it did not happen.
- CI comment rendering raw markdown tables broken by pipes in unit_ids — escape or slugify.
- Self-review graded by vibes — each row cites a *file or command* as evidence, or it does not count.
