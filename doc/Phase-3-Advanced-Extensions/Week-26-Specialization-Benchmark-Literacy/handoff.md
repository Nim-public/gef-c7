# Handoff — Week 26 Specialization Benchmark Literacy: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `01-benchmark-literacy.md` | topic deep-dive |
| `02-interpretability-basics.md` | topic deep-dive |
| `03-staying-current.md` | topic deep-dive |
| `04-capstone-future-roadmap.md` | topic deep-dive |
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

#### `01-benchmark-literacy.md` → subfolder `01-benchmark-literacy/`

Deep-dive files to create (suggested titles — refine as you write):

1. Benchmark categories — what each measures and hides
2. Contamination/saturation — failure lenses
3. Claim checklists — reading vendor scores
4. Your capstone claim — design and limits

#### `02-interpretability-basics.md` → subfolder `02-interpretability-basics/`

Deep-dive files to create (suggested titles — refine as you write):

1. Attention inspection — maps on real inputs
2. Logit lens — depth trajectories
3. Probing agent decisions — routing/retrieval failures
4. Interpretability reports — mechanistic explanations

#### `03-staying-current.md` → subfolder `03-staying-current/`

Deep-dive files to create (suggested titles — refine as you write):

1. Source triage — tiers, cadence, filters
2. Three-pass paper protocol — 30 minutes
3. Adoption gate — minimum experiments
4. Weekly routine — sustainable 3 hours

#### `04-capstone-future-roadmap.md` → subfolder `04-capstone-future-roadmap/`

Deep-dive files to create (suggested titles — refine as you write):

1. Specialization tracks — six options, first artifacts
2. Capstone 2.0 — product planning with pilots
3. Compounding portfolio — artifacts and write-ups
4. Gap-closing plan — blockers first

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [ ] `01-benchmark-literacy/`
- [ ] `02-interpretability-basics/`
- [ ] `03-staying-current/`
- [ ] `04-capstone-future-roadmap/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-3-Advanced-Extensions/Week-26-Specialization-Benchmark-Literacy/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
