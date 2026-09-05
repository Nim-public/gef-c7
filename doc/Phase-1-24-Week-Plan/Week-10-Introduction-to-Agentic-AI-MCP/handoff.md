# Handoff — Week 10 Introduction to Agentic AI MCP: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-10-Introduction-to-Agentic-AI-MCP.md` | generated overview — do not modify |
| `01-agents-foundations.md` | topic deep-dive |
| `02-tools-and-memory.md` | topic deep-dive |
| `03-mcp-servers-fastmcp.md` | topic deep-dive |
| `04-measuring-agents-patterns.md` | topic deep-dive |
| `05-prompt-context-engineering-agentic.md` | topic deep-dive |
| `06-practice-first-mcp-agent.md` | topic deep-dive |
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

#### `01-agents-foundations.md` → subfolder `01-agents-foundations/`

Deep-dive files to create (suggested titles — refine as you write):

1. Agent definition — loop, tools, memory, control-flow transfer
2. Hand-rolled ReAct loop — the 50-line implementation traced
3. Demo trajectories — single-tool, multi-tool, impossible
4. When NOT to use agents — the pipeline boundary

#### `02-tools-and-memory.md` → subfolder `02-tools-and-memory/`

Deep-dive files to create (suggested titles — refine as you write):

1. Function-calling protocol — schema→decision→execute→observe
2. ToolRegistry — jsonschema validation, error contracts
3. Memory taxonomy — history/scratchpad/episodic/semantic
4. Context budgeting — truncation, compression, per-layer costs

#### `03-mcp-servers-fastmcp.md` → subfolder `03-mcp-servers-fastmcp/`

Deep-dive files to create (suggested titles — refine as you write):

1. MCP architecture — hosts/clients/servers/transports
2. FastMCP server — tools/resources/prompts from decorators
3. Client batteries — deterministic tests + real-LLM paths
4. Capstone tool surface — read-only-first design

#### `04-measuring-agents-patterns.md` → subfolder `04-measuring-agents-patterns/`

Deep-dive files to create (suggested titles — refine as you write):

1. Trajectory instrumentation — logs, tokens, steps per run
2. Three-dimension metrics — success/efficiency/process
3. HITL gates — approval design and rates
4. LLM-as-judge — trajectory scoring and calibration

#### `05-prompt-context-engineering-agentic.md` → subfolder `05-prompt-context-engineering-agentic/`

Deep-dive files to create (suggested titles — refine as you write):

1. Agentic constitution — the 7-rule system prompt
2. Observation formatting — errors as instructive prompts
3. Context fitter — priorities, truncation, paging
4. Failure phrasing — A/B measured rewording

#### `06-practice-first-mcp-agent.md` → subfolder `06-practice-first-mcp-agent/`

Deep-dive files to create (suggested titles — refine as you write):

1. Agent assembly — loop + registry + MCP tools
2. Eval set design — 10 tasks with expected routes
3. Red-team battery integration — injection through tools
4. Metrics table — the W10-04 harness output

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [x] `01-agents-foundations/`
- [x] `02-tools-and-memory/`
- [x] `03-mcp-servers-fastmcp/`
- [ ] `04-measuring-agents-patterns/`
- [ ] `05-prompt-context-engineering-agentic/`
- [ ] `06-practice-first-mcp-agent/`

## 7.1 Continuation note (2026-09-05, session 2)

Subfolders 01–03 are complete (README + 4 deep-dives + exercises each,
all ≥4 KB, committed on `week-10-expansion`). Next session: resume at
`04-measuring-agents-patterns/` per the §4 plan, then 05, then 06; tick
each box here as you finish. Cross-links already in place point to
`../04-measuring-agents-patterns/` from files 02/03 — those targets are
created next.

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-10-Introduction-to-Agentic-AI-MCP/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
