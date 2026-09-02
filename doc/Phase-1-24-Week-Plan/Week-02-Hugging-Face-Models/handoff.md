# Handoff — Week 02 Hugging Face Models: Deep Expansion Phase

> **Purpose:** the next agent session expands every `NN-*.md` topic file in this folder into its **own subfolder** containing multiple, more detailed files. This document is the complete brief — read it fully, then follow the session prompt at the bottom.

---

## 1. Current folder state

| File | Role |
|---|---|
| `README.md` | week index — do not modify |
| `Week-02-Hugging-Face-Models.md` | generated overview — do not modify |
| `01-huggingface-platform.md` | topic deep-dive |
| `02-ready-to-use-models.md` | topic deep-dive |
| `03-nlp-tasks.md` | topic deep-dive |
| `04-modern-models.md` | topic deep-dive |
| `05-small-language-models.md` | topic deep-dive |
| `06-capstone-task-huggingface-integration.md` | topic deep-dive |
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

#### `01-huggingface-platform.md` → subfolder `01-huggingface-platform/`

Deep-dive files to create (suggested titles — refine as you write):

1. Hub anatomy — models/datasets/spaces, discovery filters, trending signals
2. Model-card critical reading — license/data/limitations checklist applied to 3 models
3. huggingface_hub programmatic access — download, cache, pin revisions, auth
4. Datasets library — load/stream/process, memory-mapped large data
5. Spaces — study, fork, publish a Gradio demo

#### `02-ready-to-use-models.md` → subfolder `02-ready-to-use-models/`

Deep-dive files to create (suggested titles — refine as you write):

1. pipeline() anatomy — tokenizer+model+postprocess, batching, device placement
2. Sentiment analysis — score semantics, domain shift, the sanity-test protocol
3. NER — token classification, aggregation, PII masking composition
4. Zero-shot classification — NLI mechanics, hypothesis templates, label wording
5. Encoder vs LLM-API decision framework — latency/cost/determinism benchmarks

#### `03-nlp-tasks.md` → subfolder `03-nlp-tasks/`

Deep-dive files to create (suggested titles — refine as you write):

1. Summarization — BART family, length controls, chunk-map-reduce for long docs
2. Extractive QA — spans, scores, the retrieval sandwich
3. Generative QA — text2text, hallucination measurement
4. Translation — MarianMT/NLLB, back-translation quality checks
5. Sentence embeddings — similarity, dedup, semantic search patterns

#### `04-modern-models.md` → subfolder `04-modern-models/`

Deep-dive files to create (suggested titles — refine as you write):

1. CLIP — zero-shot classification and raw embeddings for retrieval
2. Whisper — model tiers, timestamps, translation, telephony audio
3. Local LLM generation — chat templates, max_new_tokens, small-model roster
4. Diffusion — pipeline components, guidance/steps/seeds
5. Hardware planning — params→GB math, quantization preview, tier routing

#### `05-small-language-models.md` → subfolder `05-small-language-models/`

Deep-dive files to create (suggested titles — refine as you write):

1. SLM landscape — Qwen/Llama/Phi/Gemma/SmolLM families and licenses
2. Local serving — transformers vs Ollama vs LM Studio, OpenAI-compatible endpoints
3. Quantization basics — 4-bit trade-offs, GGUF previews
4. SLM vs API decision table — cost/latency/privacy measurements

#### `06-capstone-task-huggingface-integration.md` → subfolder `06-capstone-task-huggingface-integration/`

Deep-dive files to create (suggested titles — refine as you write):

1. Task selection — the matrix applied to your capstone
2. Model selection protocol — shortlist, widget tests, pinning
3. Mini-eval design — 20 examples, pass criteria, failure notes
4. Integration seam — function contracts and pipeline position

## 5. Work order & pacing

- Expand files in numeric order (`01` → last), one subfolder at a time.
- After each subfolder: verify all inner files exist, are ≥4 KB, and cross-links resolve.
- If the session runs low on context: stop after the current subfolder, tick its checkbox in §7, and leave a continuation note — the next session resumes from the checklist.

## 6. Progress checklist (tick as you complete each subfolder)

- [ ] `01-huggingface-platform/`
- [ ] `02-ready-to-use-models/`
- [ ] `03-nlp-tasks/`
- [ ] `04-modern-models/`
- [ ] `05-small-language-models/`
- [ ] `06-capstone-task-huggingface-integration/`

## 7. Next session prompt (paste into a fresh agent session)

```text
In the GEF C7 repository root (the folder containing doc/ and scripts/): open
doc/Phase-1-24-Week-Plan/Week-02-Hugging-Face-Models/handoff.md and follow it completely.
Expand EVERY NN-*.md topic file listed there into its own subfolder (named after the
file stem) containing 4-6 detailed files per the expansion convention and per-file
expansion plan in that handoff. Same quality and structure as the parent guides —
runnable code, exercises, pitfalls, resources, 4-8 KB per file. Verify framework
APIs with context7 MCP before writing framework examples. Work in numeric order,
tick the progress checklist in handoff.md as you complete each subfolder, do not
modify parent files or other weeks, and report the created tree when done.
```
