# Handoff — Week 01 Text Data LLM Foundations: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-01-Text-Data-LLM-Foundations.md` | generated overview — do not modify |
| `01-tokenization-and-text-representation.md` | topic deep-dive |
| `02-string-manipulation-and-regex.md` | topic deep-dive |
| `03-pandas-structured-data.md` | topic deep-dive |
| `04-file-handling-and-web-crawling.md` | topic deep-dive |
| `05-ml-fundamentals.md` | topic deep-dive |
| `06-from-neural-networks-to-llms.md` | topic deep-dive |
| `07-llm-concepts-and-demos.md` | topic deep-dive |
| `08-capstone-task-formalize-scope.md` | topic deep-dive |
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

#### `01-tokenization-and-text-representation.md` → subfolder `01-tokenization-and-text-representation/`

Deep-dive files to create (suggested titles — refine as you write):

1. Word vs character vs subword tokenization — with a from-scratch BPE trainer, merge visualizations, and vocabulary-size experiments
2. Special tokens & attention masks — padding strategies, chat templates, per-model differences, padding-without-mask failure demos
3. One-hot / multi-label encodings — sklearn encoders, sparse-vector problems, where embeddings must replace them
4. Embeddings & similarity visualization — cosine vs dot vs L2, PCA/UMAP on a real corpus, toy-vector geometry labs
5. Tokenizer API deep-dive — tiktoken vs HF tokenizers vs tokenizers-lib, cost accounting, multilingual/emoji edge cases

#### `02-string-manipulation-and-regex.md` → subfolder `02-string-manipulation-and-regex/`

Deep-dive files to create (suggested titles — refine as you write):

1. String methods mastery lab — immutability, slicing, split/join pipelines, Counter-based corpus analysis with edge cases
2. f-strings as prompt templating — formatting specs, nested templates, escaping rules, a render_prompt utility
3. Unicode deep dive — code points vs bytes, NFC/NFKC, normalization bugs, multilingual cleaning pipeline
4. Regex fundamentals — the four re functions, 20 worked patterns, greedy vs lazy, compile/VERBOSE
5. Regex applied — PII extraction, cleaning pipelines, sentence-aware chunk splitting, validation guardrails

#### `03-pandas-structured-data.md` → subfolder `03-pandas-structured-data/`

Deep-dive files to create (suggested titles — refine as you write):

1. DataFrames from zero — Series/dtypes, loading, the first-look ritual, memory basics
2. Selection & indexing — loc/iloc/at/iat, chained-indexing traps, copy-on-write
3. Filtering & vectorization — boolean masks, isin/between/str, query(), vectorized column creation
4. Aggregation — groupby mechanics, named agg, pivot_table, crosstab, time resampling
5. Joins — merge kinds, validate, suffixes, concat; the join sanity-check ritual
6. Missing data & dtypes — dropna/fillna policies, dtype surprises, mini-project with tests

#### `04-file-handling-and-web-crawling.md` → subfolder `04-file-handling-and-web-crawling/`

Deep-dive files to create (suggested titles — refine as you write):

1. File I/O done right — pathlib, encoding, globbing, corpus manifests
2. CSV deep dive — dialects, dtypes, chunked streaming, when CSV is the wrong format
3. JSON & JSONL — nesting, json_normalize, append-friendly datasets, round-trip losses
4. PDF extraction — pypdf vs pdfplumber vs OCR, layout traps, quality auditing
5. Web crawling — requests+BS4 loop, robots/ethics, retries/backoff, caching raw HTML
6. End-to-end corpus builder — crawl → clean → JSONL → pandas project

#### `05-ml-fundamentals.md` → subfolder `05-ml-fundamentals/`

Deep-dive files to create (suggested titles — refine as you write):

1. The ML definition — features/labels/examples, the f(x;θ) loop with diagrams
2. Task taxonomy — classification/regression/generation, losses per task, worked examples
3. Gradient descent from scratch — the 12-line loop, LR sweeps, convergence behavior
4. Evaluation discipline — splits, stratification, metric selection, confusion matrices by hand
5. Text classification hands-on — TF-IDF ticket router, error analysis, baseline discipline
6. Overfitting/underfitting — diagnosis plots, regularization, the test-set rules

#### `06-from-neural-networks-to-llms.md` → subfolder `06-from-neural-networks-to-llms/`

Deep-dive files to create (suggested titles — refine as you write):

1. Neural network mechanics — neurons, activations, parameter counting in PyTorch
2. The training loop traced — forward/loss/backward/step on a real model
3. Embeddings as learned representations — from one-hot to semantic space
4. The Transformer at 10,000 ft — attention, context window, encoder vs decoder
5. Pre-training vs instruction tuning — behavior comparison labs
6. Model selection — reading cards, size/memory math, license checks

#### `07-llm-concepts-and-demos.md` → subfolder `07-llm-concepts-and-demos/`

Deep-dive files to create (suggested titles — refine as you write):

1. Chat completions deep dive — roles, usage accounting, cost per call
2. Multi-turn state management — history lists, trimming, summarization, cost growth
3. Sampling controls — temperature/top_p/max_tokens experiments with plots
4. Log probabilities — confidence, zero-shot classification, routing signals
5. Streaming & autoregressive generation — the token loop made visible
6. Pre-training → SFT → RLHF — what each stage changes, with demos

#### `08-capstone-task-formalize-scope.md` → subfolder `08-capstone-task-formalize-scope/`

Deep-dive files to create (suggested titles — refine as you write):

1. Scope document workshop — template walkthrough with a fully worked example
2. Data requirements deep dive — sources, volume, licensing, PII, label needs
3. Feasibility analysis — checks, red flags, go/no-go decisions
4. Dataset sourcing lab — HF/Kaggle/gov/crawling hands-on with licensing notes
5. Mentor-pitch preparation — the 5-slide version of the scope

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [x] `01-tokenization-and-text-representation/`
- [x] `02-string-manipulation-and-regex/`
- [x] `03-pandas-structured-data/`
- [x] `04-file-handling-and-web-crawling/`
- [x] `05-ml-fundamentals/`
- [x] `06-from-neural-networks-to-llms/`
- [x] `07-llm-concepts-and-demos/`
- [x] `08-capstone-task-formalize-scope/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-01-Text-Data-LLM-Foundations/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
