# GEF C7 — Generative AI Engineering Program

## What this curriculum is for

This is the **GEF C7 — Generative AI Engineering Program** schedule (cohort 7), a 24-week live-training curriculum that takes working engineers from foundations to building production-grade GenAI applications.

**Goal:** by the end, participants build a **production-ready, multi-agent AI application** with retrieval ranking, response evaluation, and explainability.

**Who it's for:**

- Software developers/engineers transitioning into AI/LLM engineering
- Data-science professionals deepening into Generative AI
- Senior engineering leaders implementing AI-driven solutions
- Prerequisite: Python programming knowledge (Base Camp phase refreshes it)

**What it covers, in order:**

1. **Weeks 0–3 — Foundations:** Python refresher, FastAPI/Streamlit app building, NLP/LLM basics, Hugging Face, prompt engineering, transformer architecture
2. **Weeks 4–6 — Retrieval:** RAG fundamentals, vector DBs (FAISS, LanceDB), hybrid search, Text2SQL, tabular RAG
3. **Weeks 7–9 — Multimodal AI:** modality encoding, CLIP/BLIP, multimodal RAG with image/video/audio
4. **Weeks 10–14 — Agentic AI:** MCP servers, OpenAI Agents SDK, phiData (Agno), LangGraph, LangChain + MCP
5. **Weeks 15–16 — Production & fine-tuning:** reliability, LangSmith tracing, vLLM/RouteLLM optimization, Ragas evals, LoRA/QLoRA
6. **Weeks 17–24 — Capstone:** team project built with mentors, ending in a Demo Day

In short: a career-transition program producing **enterprise-grade AI engineers** who can ship real-world RAG + multi-agent applications in Python.

## Repository layout

```
doc/
├── GEF-C7-Final-Schedule.md          Master schedule (full program in one file)
├── Program-Important-Information.md  Mentors, prerequisites, goals, capstone FAQ
├── Phase-0-Onboarding-Base-Camps/    Week 0 — onboarding + Base Camps 1-3
├── Phase-1-24-Week-Plan/             Weeks 1-16 — one folder per week + break week
├── Phase-2-Capstone/                 Weeks 17-24 capstone + Demo Day
└── Phase-3-Advanced-Extensions/      10 supplementary deep-dive weeks (E1-E10,
                                      beyond the official curriculum — see its README)
```

Each `Week-nn-*` folder contains the week's schedule (`Week-nn-*.md`) plus detailed study guides: per-topic files with concepts, runnable examples, tools, exercises, pitfalls, and resources. Topic detail notes live alongside inside the same week folder.

The master schedule (`GEF-C7-Final-Schedule.md`) is the source of truth — week files are generated from it.

## Scripts

Run with Python 3.13+ (no third-party dependencies):

```powershell
# Regenerate the raw markdown dump from the source .ods spreadsheet
py scripts/ods_to_md.py [INPUT.ods] [-o OUTPUT.md]

# Regenerate the per-phase / per-week folder structure from the master schedule
py scripts/split_schedule.py [SOURCE.md] [-o OUTPUT_DIR]
```
