# Handoff — Week 16 Evals and Fine Tuning: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-16-Evals-and-Fine-Tuning.md` | generated overview — do not modify |
| `01-eval-strategy-ragas.md` | topic deep-dive |
| `02-synthetic-data.md` | topic deep-dive |
| `03-fine-tuning-fundamentals.md` | topic deep-dive |
| `04-lora-qlora.md` | topic deep-dive |
| `05-capstone-task-llamaindex-retrieval.md` | topic deep-dive |
| `06-capstone-prep-demo-day.md` | topic deep-dive |
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

#### `01-eval-strategy-ragas.md` → subfolder `01-eval-strategy-ragas/`

Deep-dive files to create (suggested titles — refine as you write):

1. Ragas revision — four metrics, diagnosis patterns
2. Slice analysis — per route/doc-type tables
3. Offline vs online — golden sets and live signals
4. Dataset versioning — immutable, changelog, held-out slices

#### `02-synthetic-data.md` → subfolder `02-synthetic-data/`

Deep-dive files to create (suggested titles — refine as you write):

1. Seed expansion — paraphrase/variation generation
2. Persona grids — coverage cells and weights
3. Adversarial generation — red-team data at scale
4. Validation — labels, diversity, leakage, distribution

#### `03-fine-tuning-fundamentals.md` → subfolder `03-fine-tuning-fundamentals/`

Deep-dive files to create (suggested titles — refine as you write):

1. SFT data — formatting, masking, distribution matching
2. Tokenization & loaders — templates, truncation audits
3. Training loop — args, schedules, checkpoints, best-pick
4. Overfitting diagnosis — eval-during-train discipline

#### `04-lora-qlora.md` → subfolder `04-lora-qlora/`

Deep-dive files to create (suggested titles — refine as you write):

1. LoRA math — low-rank delta, parameter counting
2. Adapter config — targets, r, alpha, dropout
3. QLoRA — 4-bit base training on one GPU
4. Parity checks — merged vs adapter serving

#### `05-capstone-task-llamaindex-retrieval.md` → subfolder `05-capstone-task-llamaindex-retrieval/`

Deep-dive files to create (suggested titles — refine as you write):

1. LlamaIndex essentials — readers/nodes/index/query engine
2. Settings pinning — embedder/chunker, not defaults
3. Shared-interface comparison — both engines, one harness
4. Ship/adopt/reject decision — evidence-based

#### `06-capstone-prep-demo-day.md` → subfolder `06-capstone-prep-demo-day/`

Deep-dive files to create (suggested titles — refine as you write):

1. Architecture freeze — 1:1 checklist
2. Sprint roadmap — W17-24 exit artifacts
3. Demo-day assets — script, metrics, fallback
4. Version 1.0 definition — the five bars

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [x] `01-eval-strategy-ragas/`
- [x] `02-synthetic-data/`
- [x] `03-fine-tuning-fundamentals/`
- [x] `04-lora-qlora/`
- [x] `05-capstone-task-llamaindex-retrieval/`
- [x] `06-capstone-prep-demo-day/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-16-Evals-and-Fine-Tuning/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
