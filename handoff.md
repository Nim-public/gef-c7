# Handoff — GEF C7 Study-Guide Build

> Status: **COMPLETE.**
> - **Core program: Weeks 0–16 fully built** (`doc/Phase-1-24-Week-Plan/`, `Phase-0/`, `Phase-2/`)
> - **Advanced extensions: E1–E10 fully built** (`doc/Phase-3-Advanced-Extensions/`, Weeks 17–26 equivalent — 10 supplementary deep-dive weeks beyond the official curriculum)
> - The schedule's Weeks 17–24 remain the student capstone phase (no curriculum files needed); demo-day preparation lives in `Week-16-.../06-capstone-prep-demo-day.md`.

---

## 1. Final state

| Artifact | Location | Status |
|---|---|---|
| Master schedule (source of truth) | `doc/GEF-C7-Final-Schedule.md` | done |
| ODS→MD converter | `scripts/ods_to_md.py` | done |
| Splitter (master → phase/week folders) | `scripts/split_schedule.py` | done (only regenerates `Week-XX-*.md` overviews; detail files are safe) |
| Week 1–16 study guides | `doc/Phase-1-24-Week-Plan/Week-01..16*/` | done, full detail |
| Phase-2 capstone + demo day | `doc/Phase-2-Capstone/` | done |
| Extensions E1–E10 | `doc/Phase-3-Advanced-Extensions/Week-17..26*/` | done, full detail (56 files + overview) |
| **Week-level handoffs** | `**/Week-*/handoff.md` (26 files) | done — each briefs a next session to expand every `NN-*.md` into a subfolder of deeper multi-file study guides; generator: `scripts/gen_week_handoffs.py` |
| doc README | `doc/README.md` | done (describes both phases) |
| This handoff | `handoff.md` | current |

## 2. Extension weeks (E1–E10) summary

| # | Folder | Topic | Practice build |
|---|---|---|---|
| E1 | Week-17 | DPO/RLHF/distillation, embedder+reranker fine-tuning | alignment lab |
| E2 | Week-18 | Knowledge graphs, GraphRAG (local/global), long context | graphrag over corpus |
| E3 | Week-19 | Code agents (SWE patterns), browser agents, computer use, CI | repo QA+fix agent |
| E4 | Week-20 | Detection/segmentation, document AI/OCR, vision agents | doc-to-knowledge pipeline |
| E5 | Week-21 | Diarization, TTS/cloning, realtime voice production | meeting assistant |
| E6 | Week-22 | Speculative decoding, grammar-constrained decoding, GGUF | decoding lab |
| E7 | Week-23 | OWASP deep dive, jailbreak taxonomy, red-teaming, sandboxing | red-team the agent |
| E8 | Week-24 | Registries, prompt CI/CD, A/B+shadow+canary, cost, OTel | full LLMOps loop |
| E9 | Week-25 | Memory architectures, semantic caching, long-term memory design | memory-augmented agent |
| E10 | Week-26 | Benchmark literacy, interpretability, research workflow, roadmap | capstone 2.0 roadmap |

## 3. Conventions (identical across all weeks)

- Topic file structure: H1 + breadcrumb + schedule/topics (bold) → `## What you'll learn` → numbered concept sections with runnable code → tables → `## Exercises` (5, capstone-tied) → `## Pitfalls` (5–6 bolded) → `## Resources` (4–6).
- README structure: breadcrumb → "Why this week matters" → outcomes checklist → study-order table → env setup → self-check questions.
- Windows/PowerShell (`py`, `.venv\Scripts\Activate.ps1`); brief pedagogical comments allowed; cross-links between weeks by relative path; framework names verified against docs (see §4).
- Capstone continuity thread runs across all 26 weeks (W1 scope → … → W15 hardening → W16 evals/LoRA/LlamaIndex → E1 alignment → … → E10 roadmap). Formal schedule tasks framed as "Weekly task"; extension builds as "Practice build".
- Never touch the generated `Week-XX-<Name>.md` overview files.

## 4. API verification registry (context7 ids used)

`/openai/openai-agents-python`, `/prefecthq/fastmcp`, `/langchain-ai/langgraph`, `/crewaiinc/crewai`, `/agno-agi/docs`, `/run-llama/llama_index`, `/websites/langchain_oss_python_langchain`, `/websites/ragas_io_en_stable`, `/lancedb/lancedb`, `/openai/openai-python`, `/huggingface/course`, `/huggingface/diffusers`, `/huggingface/trl`, `/dottxt-ai/outlines`

Re-verify any framework example before production use — APIs move faster than course content.

## 5. Possible future work (not started)

- **Deep-expansion sessions**: run each week's `handoff.md` prompt (26 available) to create per-topic subfolders with multi-file deep dives
- Solutions/reference implementations for the practice builds (one repo per week)
- Slide decks per week (the MD files are the source material)
- A quiz/self-assessment bank per week
- Translations (e.g., Hindi) of the study guides
- Updating guides when master schedule changes (`scripts/split_schedule.py` regenerates the skeleton; `scripts/gen_week_handoffs.py` regenerates week handoffs)
