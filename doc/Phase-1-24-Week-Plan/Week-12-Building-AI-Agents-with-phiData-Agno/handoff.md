# Handoff — Week 12 Building AI Agents with phiData Agno: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-12-Building-AI-Agents-with-phiData-Agno.md` | generated overview — do not modify |
| `01-agno-introduction.md` | topic deep-dive |
| `02-knowledge-and-databases.md` | topic deep-dive |
| `03-custom-tools-toolkits.md` | topic deep-dive |
| `04-analytics-agent-financial.md` | topic deep-dive |
| `05-agentic-rag-with-phidata.md` | topic deep-dive |
| `06-capstone-task-crewai-workflow.md` | topic deep-dive |
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

#### `01-agno-introduction.md` → subfolder `01-agno-introduction/`

Deep-dive files to create (suggested titles — refine as you write):

1. Agno agent structure — model/instructions/tools/knowledge fields
2. Playground — UI, run history, tool inspection
3. Framework mapping — W10/W11/W12 completion table
4. phiData→Agno migration — imports and API notes

#### `02-knowledge-and-databases.md` → subfolder `02-knowledge-and-databases/`

Deep-dive files to create (suggested titles — refine as you write):

1. Knowledge bases — LanceDB integration, hybrid search type
2. Ingestion by source — PDF/CSV/JSON/RDBMS paths
3. Grounding rules — instructions, insufficiency battery
4. Dual-pipeline design — knowledge vs SQL tool selection

#### `03-custom-tools-toolkits.md` → subfolder `03-custom-tools-toolkits/`

Deep-dive files to create (suggested titles — refine as you write):

1. Function tools — schemas from hints and docstrings
2. Toolkit classes — grouping, scoping, per-task flags
3. Advanced data tools — charts, schema, verification
4. Toolkit testing — the client battery toolkit edition

#### `04-analytics-agent-financial.md` → subfolder `04-analytics-agent-financial/`

Deep-dive files to create (suggested titles — refine as you write):

1. Prebuilt finance toolkits — YFinance usage and limits
2. Analytics over your tables — guarded SQL composition
3. Numeric-hallucination defenses — verification hooks
4. Reasoning display — audit trails in answers

#### `05-agentic-rag-with-phidata.md` → subfolder `05-agentic-rag-with-phidata/`

Deep-dive files to create (suggested titles — refine as you write):

1. Fixed vs agentic RAG — the decision analysis
2. Three-power agent — toolkit routing design
3. Route accuracy — measurement vs W6-04 router
4. Cost/quality trade — token and latency tables

#### `06-capstone-task-crewai-workflow.md` → subfolder `06-capstone-task-crewai-workflow/`

Deep-dive files to create (suggested titles — refine as you write):

1. CrewAI essentials — roles/tasks/crew/process
2. Role design — least-privilege specialist split
3. Process choice — sequential vs hierarchical measured
4. Comparison vs W11 — same cases table

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [x] `01-agno-introduction/`
- [x] `02-knowledge-and-databases/`
- [x] `03-custom-tools-toolkits/`
- [x] `04-analytics-agent-financial/`
- [x] `05-agentic-rag-with-phidata/`
- [x] `06-capstone-task-crewai-workflow/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-12-Building-AI-Agents-with-phiData-Agno/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
