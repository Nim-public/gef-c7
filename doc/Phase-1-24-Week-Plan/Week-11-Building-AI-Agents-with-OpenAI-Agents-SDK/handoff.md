# Handoff — Week 11 Building AI Agents with OpenAI Agents SDK: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK.md` | generated overview — do not modify |
| `01-agents-sdk-quickstart.md` | topic deep-dive |
| `02-tools-handoffs-guardrails.md` | topic deep-dive |
| `03-multi-agent-orchestration.md` | topic deep-dive |
| `04-voice-agents.md` | topic deep-dive |
| `05-observability-eval-agents.md` | topic deep-dive |
| `06-practice-agents-sdk-capstone.md` | topic deep-dive |
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

#### `01-agents-sdk-quickstart.md` → subfolder `01-agents-sdk-quickstart/`

Deep-dive files to create (suggested titles — refine as you write):

1. SDK anatomy — Agent/Runner/RunResult fields
2. Loop mechanics — the 4 documented steps, max_turns
3. Structured output_type — Pydantic final answers
4. Sessions — SQLite persistence across turns
5. Tracing — spans, dashboards, local export

#### `02-tools-handoffs-guardrails.md` → subfolder `02-tools-handoffs-guardrails/`

Deep-dive files to create (suggested titles — refine as you write):

1. function_tool — schemas from signatures, gating with is_enabled
2. Handoffs — control transfer, descriptions, last_agent
3. Input guardrails — tripwires, judge-agents, exceptions
4. Output guardrails — citation/schema validation
5. The W3-02 battery mechanized as pytest

#### `03-multi-agent-orchestration.md` → subfolder `03-multi-agent-orchestration/`

Deep-dive files to create (suggested titles — refine as you write):

1. Handoff pattern — router→specialist topology
2. Chaining — sequential refinement with typed outputs
3. Delegation — manager with agents-as-tools
4. State passing — context, outputs, summaries
5. Anti-patterns — ping-pong, spirals, bloat

#### `04-voice-agents.md` → subfolder `04-voice-agents/`

Deep-dive files to create (suggested titles — refine as you write):

1. Cascade stack — STT→agent→TTS with budget table
2. Turn-taking — VAD, endpointing, barge-in
3. Minimal demo — push-to-talk implementation
4. Realtime vs cascade — decision and costs

#### `05-observability-eval-agents.md` → subfolder `05-observability-eval-agents/`

Deep-dive files to create (suggested titles — refine as you write):

1. Trace/span model — generation/tool/handoff spans
2. Replay debugging — failed-run root cause workflow
3. Export to harness — merged W10-04+trace rows
4. Regression suites — trajectory assertions

#### `06-practice-agents-sdk-capstone.md` → subfolder `06-practice-agents-sdk-capstone/`

Deep-dive files to create (suggested titles — refine as you write):

1. Port methodology — W10 agent to SDK primitives
2. Comparison table — same cases, both implementations
3. Trace debugging — planted failure root cause
4. Verdict — lines saved vs capabilities gained

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [ ] `01-agents-sdk-quickstart/`
- [ ] `02-tools-handoffs-guardrails/`
- [ ] `03-multi-agent-orchestration/`
- [ ] `04-voice-agents/`
- [ ] `05-observability-eval-agents/`
- [ ] `06-practice-agents-sdk-capstone/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
