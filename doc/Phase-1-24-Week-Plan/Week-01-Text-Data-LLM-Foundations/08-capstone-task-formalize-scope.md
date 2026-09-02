# 08 — Weekly Task: Formalize Your Capstone Scope

> Week 1 index: [README.md](README.md) · **Due: before Week 2 (by 12 Sep)**

**Task (from the schedule):** *Formalize capstone project scope based on data requirements and feasibility.*

Why this lands in Week 1, before any frameworks: **data determines feasibility.** Teams that pick an idea first and hunt for data in Week 10 rebuild from zero in Week 12. You'll do it in the right order: idea → data → feasibility → scope.

---

## 1. Deliverable

A **one-page scope doc** (`capstone-scope.md`) committed in your team repo, covering every section of the template below. You'll defend it in a 1:1 mentor call, and revise it across the program — v1 here, tightened after Week 4 (retrieval) and Week 10 (agents).

## 2. Scope doc template

```markdown
# Capstone Scope — <Project Name>          (v1, Week 1)

## Problem
Who has this problem, what do they do today, and what does the AI do?
(2–4 sentences. If you can't name the user, you don't have a project yet.)

## Core capability
One sentence: "Given <input>, produce <output>."

## Input / output modalities
Text only? Tables? Images/audio (→ needs Weeks 7–9)? Structured DB (→ Week 6)?
Multiple agents/tools (→ Weeks 10–14)?

## Data requirements            ← the heart of this task
| Item | Answer |
|---|---|
| Sources (URLs / files / APIs / own DB) |  |
| Volume (docs / rows / hours of audio) |  |
| Format (PDF, JSONL, SQL dump, HTML) |  |
| Access today? (have it / can download / must crawl / must buy) |  |
| Licensing & PII (redistribution? personal data?) |  |
| Labels needed? (eval sets, ground truth) |  |
| Languages / domains |  |

## Feasibility checks
- [ ] I can get a ≥100-item representative sample **this week**
- [ ] Text extraction works (for PDFs: page 1 of 3 sample files extracts cleanly)
- [ ] No PII/secret data without a handling plan
- [ ] Baseline with no-LLM heuristics defined (what's "good enough"?)
- [ ] Rough LLM cost per item estimated (tokens × price, file 07)
- [ ] One metric defined for success (accuracy / faithfulness / latency budget)

## Non-goals (v1)
Explicitly out of scope, postponed ideas, "later" list.

## Team
Members, roles (ingestion / modeling / eval / demo), meeting cadence.
```

## 3. Three worked example scopes (calibrated to this program)

### A. RAG over internal documentation

- **Problem:** support engineers grep through 400 scattered PDFs/wiki pages.
- **I/O:** question in English → cited answer with source links. *Text-only.*
- **Data:** export wiki + PDFs (~400 docs, 60 MB). Access: have it. PII: audit needed. Labels: build a 50-question eval set with known answers.
- **Feasibility:** sample 20 PDFs, run `pypdf` extraction today (file 04); if >20% of pages extract as garbage → different corpus or add OCR.
- **Maps to:** Weeks 4–6 (RAG, tabular), Week 5 (evaluation), Week 16 (Ragas).

### B. Support-ticket triage & routing agent

- **Problem:** tickets wait in one queue; humans assign category, priority, team.
- **I/O:** ticket text → category + priority + drafted reply + routing. *Text + a table of historical tickets.*
- **Data:** export tickets (CSV/JSON) with past human labels — labels already exist for evaluation. Access: have it. PII: mask emails/phones (file 02 regex!).
- **Feasibility:** baseline = the Week 1 TF-IDF classifier (file 05) — if it's ≥70% F1, the LLM version has a measurable bar to beat.
- **Maps to:** Week 2 (HF models), Week 5 (chatbot + guardrails), Week 13 (LangGraph router project).

### C. Product catalog enrichment (multimodal)

- **Problem:** 5,000 products have images + terse titles; marketing needs descriptions + attribute tags.
- **I/O:** product image + text → description + category + attributes. *Image + text → text.*
- **Data:** catalog dump (CSV) + image URLs. Access: have it. Labels: 100 hand-annotated examples for eval.
- **Feasibility:** confirm image URLs are fetchable at scale (file 04 crawler) — dead links kill this scope.
- **Maps to:** Weeks 7–9 (multimodal RAG), Week 16 (evals).

Note the pattern: each scope names **which program weeks it exercises** — that's the cleanest feasibility test of all, since the program must be able to teach you to build it.

## 4. Where to find data (if you don't have your own)

| Source | Best for | Notes |
|---|---|---|
| [Hugging Face Datasets](https://huggingface.co/datasets) | text corpora, QA pairs, multi-modal | check license per dataset |
| [Kaggle](https://www.kaggle.com/datasets) | tabular, business-flavored | competitions = ready eval sets |
| [data.gov.in](https://data.gov.in) / [data.gov](https://data.gov) | public-sector data | often messy — real-world practice |
| Wikipedia / Project Gutenberg | clean long-form text corpora | per-terms scraping with file 04 patterns |
| Your own domain data | everything | the differentiator — mentors push for it |
| `quotes/books.toscrape.com` | crawling practice only | too small for a capstone |

**Self-data rule (from the program FAQ):** bringing your own capstone idea means bringing your own dataset — budget time for it now.

## 5. Feasibility red flags

- Data requires a contract/approval you don't control (timeline risk → have plan B)
- Ground truth doesn't exist and can't be built in a week → you can't evaluate anything (Week 16 pain)
- "We'll collect the data during the capstone" — no
- Success metric is "looks good" — name a number
- One person is the only source of knowledge about the data (bus factor 1)

## 6. Checklist before calling it done

- [ ] One page or less
- [ ] Data section filled with *specific* sources, not "we'll find something"
- [ ] Sample data actually downloaded (≥100 items) and eyeballed
- [ ] One measurable success criterion
- [ ] Non-goals listed
- [ ] Reviewed against Week 1 concepts: token costs estimated (file 07), data formats verified (file 04), any table data loadable in pandas (file 03)

Bring the draft to Thursday Office Hours (10 Sep) — mentors punch holes in scope docs, and that's the point.
