# Contributing to GEF C7 Study Guides

Thanks for contributing! This repo holds study guides for the GEF C7 GenAI engineering curriculum. Read this file, then `doc/README.md` for the layout.

## Quick start

```powershell
git clone https://github.com/Nim/gef-c7.git
cd gef-c7
py -m venv .venv
.\.venv\Scripts\Activate.ps1
# study-guide content needs no dependencies; scripts are stdlib-only
```

## Repository structure

```
doc/
├── GEF-C7-Final-Schedule.md        source of truth for the curriculum
├── Phase-1-24-Week-Plan/Week-01..16*/   core course weeks
├── Phase-2-Capstone/               capstone + demo day
├── Phase-3-Advanced-Extensions/    extension weeks E1-E10 (Weeks 17-26)
└── README.md                       detailed repo guide
scripts/                            generation tooling
```

## Content conventions (enforced in review)

1. **Week folder layout** — `README.md` (index), `NN-<topic>.md` (topic files), final numbered file = practice/task build. Generated `Week-XX-*.md` overview files are never hand-edited.
2. **Topic file structure** — What you'll learn → numbered concept sections with runnable code → tables → Exercises (5, capstone-tied) → Pitfalls (bolded) → Resources. 4–8 KB per file.
3. **Runnable code only** — every example executes as written. Windows/PowerShell syntax (`py`, `.venv\Scripts\Activate.ps1`), repo-relative paths, no machine-specific absolute paths.
4. **Capstone continuity** — exercises and builds reference the learner's own RAG/agent stack; cross-link other weeks with relative paths.
5. **Verify APIs** — check framework usage against current docs (context7 MCP or official docs) before writing examples; note the version you checked.
6. **No secrets, no real PII** — use `.env` patterns and synthetic data. Never commit API keys, real transcripts, or media.
7. **License** — contributions are released under the repo license ([The Unlicense](LICENSE.md) — public domain).

## Adding content

- **New week/topic**: follow an existing week folder as the template. Keep the numbered-file convention.
- **Deep expansion**: week folders contain a `handoff.md` with the expansion convention (one subfolder per `NN-*.md` file, 4–6 detailed files inside). Follow its per-file expansion plan and tick its progress checklist.
- **Fixes**: corrections to facts, code, or links are always welcome — keep the change minimal and cite the source of the correction.

## Scripts

```powershell
py scripts/ods_to_md.py            # regenerate markdown from the source .ods
py scripts/split_schedule.py       # regenerate the phase/week folder skeleton
py scripts/gen_week_handoffs.py    # regenerate week handoff.md files
```

Do not hand-edit generated files (`Week-XX-*.md` overviews); regenerate or change the generator.

## Evaluation honesty

Any claim of improvement must come from the repo's eval methodology (held-out cases, pinned judge/model versions, reported sample sizes). "It works" without numbers will be asked to become numbers.

## Reporting issues

Open an issue with: what you expected, what happened, and the smallest reproduction (file + line for content errors).
