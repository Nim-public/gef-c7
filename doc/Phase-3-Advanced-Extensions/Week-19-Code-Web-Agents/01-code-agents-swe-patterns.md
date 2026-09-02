# 01 — Code Agents: The SWE-Agent Pattern

> E3 index: [README.md](README.md)

**Core topic:** *SWE-agent-style systems — navigating a repository, localizing the change, editing, and validating.*

---

## What you'll learn

- The SWE-agent loop: navigate → localize → edit → validate
- Repo tools with interface design that agents can actually use (the paper's key lesson)
- Localization: finding *where* to change before *what* to change
- A working repo-QA + edit agent over your capstone

## 1. The loop (SWE-bench's lesson)

The SWE-agent paper (Yang et al., 2024) showed that *how the model interacts with the repo* matters as much as the model: agents fail on clunky interfaces and succeed with tight ones. The canonical loop:

```
request ─► [navigate: structure, search] ─► [localize: files/functions to change]
        ─► [edit: minimal patch] ─► [validate: run tests/linters] ─► iterate or done
```

Four phases, each with its own tool bias — and the paper's **interface design lesson**: tools should return *exactly the information the next phase needs* in a compact, structured form. A `grep` tool returning 500 raw lines wastes the context (W10-05); one returning file:line + matched sentence feeds localization directly.

## 2. Repo tools (interface-first design)

```python
from langchain_core.tools import tool
from pathlib import Path
import subprocess

ROOT = Path.cwd().resolve()          # run from the repo root — no machine-specific paths

@tool
def repo_map(dir: str = ".") -> str:
    """Project tree (2 levels) with file sizes — use first to orient."""
    base = (ROOT / dir).resolve()
    lines = []
    for p in sorted(base.rglob("*")):
        if any(part in {".git", ".venv", "__pycache__", "node_modules"} for part in p.parts):
            continue
        rel = p.relative_to(base)
        if len(rel.parts) <= 2:
            lines.append(f"{'📁' if p.is_dir() else '📄'} {rel} "
                         f"({p.stat().st_size if p.is_file() else '-'} B)")
    return "\n".join(lines[:80])

@tool
def grep_code(pattern: str, glob: str = "*.py") -> str:
    """Search code by regex. Returns 'file:line: matched line' — max 40 hits, one line each."""
    hits = []
    for p in ROOT.rglob(glob):
        if ".git" in p.parts or ".venv" in p.parts: continue
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if re.search(pattern, line):
                hits.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()[:120]}")
                if len(hits) >= 40: return "\n".join(hits) + "\n(truncated — narrow the pattern)"
    return "\n".join(hits) or "no matches"

@tool
def read_file(path: str, start: int = 1, count: int = 60) -> str:
    """Read a file window (file, 1-based start line, line count) with line numbers."""
    p = (ROOT / path).resolve()
    if not str(p).startswith(str(ROOT)): return "ERROR: outside workspace"
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    sel = lines[start-1 : start-1+count]
    return "\n".join(f"{start+i}: {l}" for i, l in enumerate(sel))
```

Interface rules visible here: **path containment** (workspace-root check — the W10-02 security rule for filesystems), **line numbers** (localization + precise edits), **truncation with notice**, **orientation-first** (`repo_map` documented as the entry tool).

## 3. Localization + edit + validate

```python
@tool
def apply_edit(path: str, old: str, new: str) -> str:
    """Replace an exact string in a file (W10-style edit). Fails loudly if not unique/found."""
    p = (ROOT / path).resolve()
    if not str(p).startswith(str(ROOT)): return "ERROR: outside workspace"
    src = p.read_text(encoding="utf-8")
    n = src.count(old)
    if n != 1: return f"ERROR: {n} matches — include more context in old"
    p.write_text(src.replace(old, new), encoding="utf-8")
    return f"edited {path} ({len(old)} → {len(new)} chars)"

@tool
def run_tests(path_glob: str = "tests/") -> str:
    """Run pytest on the given path; returns the tail of the output."""
    r = subprocess.run(["py", "-m", "pytest", "-q", str(ROOT / path_glob)],
                       capture_output=True, text=True, timeout=120)
    return (r.stdout + r.stderr)[-3000:]
```

The agent loop (W13-04's code-gen graph, now with repo tools): `plan → localize (grep/repo_map) → read_file → apply_edit → run_tests → (fail → debug → edit)`. Your W13-04 graph is the scaffolding; these are the domain tools.

## 4. Repo-QA: the low-risk first agent

Before letting agents *edit*, ship the QA variant — same tools minus `apply_edit`:

```python
qa_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[repo_map, grep_code, read_file],
    system_prompt=("You answer questions about this codebase. Orient with repo_map, "
                   "localize with grep_code, read precisely with read_file. "
                   "Cite file:line for every claim. Say 'not found in repo' if so."),
)
qa_agent.invoke({"messages": [{"role": "user",
    "content": "Where is the eval harness defined and what schema does it expect?"}]})
```

Zero-risk (read-only), immediately useful, and it *validates your tool interfaces* before edits are on the table — the W10-04 least-power ladder, applied.

## 5. Edit-gating (the production rule)

Edits go through W10-04's gates: proposed patch shown (diff), human approves (or CI-bot thresholds), the edit tool applies atomically, `run_tests` must pass before the patch is considered done. The W13-04 self-repair loop *is* the validation loop — the SWE-agent pattern composes with everything you've built.

## Exercises

1. Build the QA agent; ask 5 questions about your capstone repo; verify every claim's `file:line` citation by opening the files. Hallucination rate?
2. Tool-interface A/B: `grep_code` returning raw 500-line output vs the 40-hit cap — run the same localization task both ways; compare steps and correct localization rate (the SWE-agent lesson, measured).
3. Edit drill: give the edit-gated agent a real small bug (introduce one in your code); verify propose → approve → apply → test-pass cycle.
4. Localization probe: ask "where is prompt versioning handled?" — compare grep-first vs read-everything strategies for steps and accuracy.
5. Constrain the agent to *one subdirectory* (scoped ROOT); what breaks? (Least-privilege scoping, W10-04, filesystem edition.)

## Pitfalls

- **Path escapes** — every file tool needs the workspace-root containment check (the `apply_edit` guard above)
- **Unbounded reads** — `read_file` without windows = context bomb; line-window + truncation always
- **Edits without tests** — an unvalidated patch is a bug with extra steps; the W13-04 loop is the validation contract
- **Grep on binary/generated files** — exclude `.venv`, `node_modules`, lock files, media (the tool above filters; keep the filter)
- **Agent-owned secrets in repos** — the repo-QA agent can read `.env` if not excluded; add secret-file deny lists to *every* file tool

## Resources

- Yang et al., *SWE-agent: Agent-Computer Interfaces Enable Software Engineering LLMs* — the interface-design paper (§3 is this file's core)
- [SWE-bench](https://www.swebench.com/) — the benchmark and its task shapes
- Aider / OpenHands / Cursor docs — production code-agent designs (repo-map patterns)
- W13-04 (self-repair graph) + W10-02/05 (tool design) — composed here
