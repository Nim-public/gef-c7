# Handoff — Week 14 Advanced AI Workflows with LangChain MCP: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-14-Advanced-AI-Workflows-with-LangChain-MCP.md` | generated overview — do not modify |
| `01-langchain-foundations.md` | topic deep-dive |
| `02-project-csv-analyzer.md` | topic deep-dive |
| `03-project-code-review-agent.md` | topic deep-dive |
| `04-agentic-rag-langchain.md` | topic deep-dive |
| `05-workflow-assistant-mcp.md` | topic deep-dive |
| `06-practice-langchain-mcp.md` | topic deep-dive |
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

#### `01-langchain-foundations.md` → subfolder `01-langchain-foundations/`

Deep-dive files to create (suggested titles — refine as you write):

1. Prompt templates — versioned, validated, file-loaded
2. LCEL composition — pipelines, streaming, fallbacks/retries
3. Structured output — Pydantic-validated chains
4. create_agent — the modern agent API mapped

#### `02-project-csv-analyzer.md` → subfolder `02-project-csv-analyzer/`

Deep-dive files to create (suggested titles — refine as you write):

1. Tool surface — profile/pandas/chart with guards
2. Sandbox discipline — restricted eval, malicious probes
3. Four features — chat/summary/analyze/visualize wiring
4. Numeric grounding — numbers_supported checks

#### `03-project-code-review-agent.md` → subfolder `03-project-code-review-agent/`

Deep-dive files to create (suggested titles — refine as you write):

1. Deterministic scan layer — AST/ruff findings
2. LLM review layer — structured Finding models
3. Report generation — deterministic severity sort
4. Diff-aware review — full-file context, line hints

#### `04-agentic-rag-langchain.md` → subfolder `04-agentic-rag-langchain/`

Deep-dive files to create (suggested titles — refine as you write):

1. Three-source routing — vector/SQL/web agent
2. Decomposition — sub-question generation
3. Self-improving loops — logs to eval sets
4. Graph parity — W13-01 equivalence testing

#### `05-workflow-assistant-mcp.md` → subfolder `05-workflow-assistant-mcp/`

Deep-dive files to create (suggested titles — refine as you write):

1. MCP adapter — multi-server client configuration
2. Scope containment — paths, tokens, allow-lists
3. Smart automation — gated cross-server chains
4. Cross-server injection testing

#### `06-practice-langchain-mcp.md` → subfolder `06-practice-langchain-mcp/`

Deep-dive files to create (suggested titles — refine as you write):

1. Framework verdict — the 5-framework table
2. Tool budget and topology decisions
3. Four pillars end-to-end demos
4. Regression and safety integration

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [ ] `01-langchain-foundations/`
- [ ] `02-project-csv-analyzer/`
- [ ] `03-project-code-review-agent/`
- [ ] `04-agentic-rag-langchain/`
- [ ] `05-workflow-assistant-mcp/`
- [ ] `06-practice-langchain-mcp/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-14-Advanced-AI-Workflows-with-LangChain-MCP/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
