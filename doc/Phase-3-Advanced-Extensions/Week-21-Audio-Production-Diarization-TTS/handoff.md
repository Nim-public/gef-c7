# Handoff — Week 21 Audio Production Diarization TTS: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `01-diarization-speech-analytics.md` | topic deep-dive |
| `02-tts-voice-cloning.md` | topic deep-dive |
| `03-realtime-voice-production.md` | topic deep-dive |
| `04-practice-meeting-assistant.md` | topic deep-dive |
| `handoff.md` | this brief |

## 2. Expansion convention (applies to EVERY `NN-*.md` file)

1. Create subfolder `NN-<slug>/` named exactly after the file stem (e.g., `01-dpo-preference-optimization.md` → `01-dpo-preference-optimization/`).
2. Inside, create **4–6 detailed files**:
   - `README.md` — subtopic index: what this deep-dive covers, file map, study order, prerequisites (link back to `../NN-<slug>.md`).
   - `01-<subtopic>.md` … `0N-<subtopic>.md` — one deep-dive per major subtopic, following the expansion plan below.
   - `exercises.md` — expanded exercise set with worked approaches.
   - optionally `solutions.md` and `quiz.md` (self-assessment).
3. Each file: **4–8 KB**, same structure as the parent guides (What you'll learn → concepts with runnable code → tables → Exercises → Pitfalls → Resources).
4. The parent `NN-<slug>.md` stays **unchanged** — it remains the week-level overview.
5. Depth expectation: subfolders go **beyond** the parent — edge cases, end-to-end worked examples, failure drills, comparisons, performance notes — never a reformat of the parent.
6. Subfolder READMEs link back to the parent; deep-dive files cross-link other weeks' files by relative path when they build on them.

## 3. Quality rules (non-negotiable)

- Windows/PowerShell: `py` (not `python`), `.venv\Scripts\Activate.ps1`. Use **repo-relative paths** in all examples (`doc/...`, `data/...`, `scripts/...`) — never machine-specific absolute paths.
- All code **runnable**; verify framework APIs via **context7 MCP** before writing framework examples (note the library id used).
- Brief pedagogical comments allowed; no filler prose; every concept paired with a runnable artifact.
- Exercises tie to the capstone (GEF C7: RAG + agents over the learner's own corpus/tables/media).
- Do **not** modify: `README.md`, `Week-XX-*.md` overviews, other weeks' folders, `doc/GEF-C7-Final-Schedule.md`.
- **No compression, no placeholders** — full detail in every file (the user has explicitly rejected compressed outputs).

## 4. Per-file expansion plan

#### `01-diarization-speech-analytics.md` → subfolder `01-diarization-speech-analytics/`

Deep-dive files to create (suggested titles — refine as you write):

1. pyannote pipelines — speaker turns, known/unknown counts
2. Transcript merge — overlap-weighted assignment
3. Hard cases — crosstalk, label churn, interjections
4. Analytics — talk-time, interruptions, commitments

#### `02-tts-voice-cloning.md` → subfolder `02-tts-voice-cloning/`

Deep-dive files to create (suggested titles — refine as you write):

1. TTS landscape — API voices vs open models
2. Quality knobs — reference samples, sentence splitting
3. Voice cloning — consent line and disclosure
4. Agent integration — sentence streaming, expansion

#### `03-realtime-voice-production.md` → subfolder `03-realtime-voice-production/`

Deep-dive files to create (suggested titles — refine as you write):

1. VAD/endpointing — turn-taking machinery
2. Barge-in — playback interruption and cancellation
3. Telephony — 8kHz, echo, jitter handling
4. Voice observability — per-stage metrics

#### `04-practice-meeting-assistant.md` → subfolder `04-practice-meeting-assistant/`

Deep-dive files to create (suggested titles — refine as you write):

1. Meeting ingestion — merge pipeline with flags
2. RAG with speaker citations — turn-group chunks
3. Commitment extraction — verified vs transcript
4. TTS summary — expansion and consent

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [ ] `01-diarization-speech-analytics/`
- [ ] `02-tts-voice-cloning/`
- [ ] `03-realtime-voice-production/`
- [ ] `04-practice-meeting-assistant/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-3-Advanced-Extensions/Week-21-Audio-Production-Diarization-TTS/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
