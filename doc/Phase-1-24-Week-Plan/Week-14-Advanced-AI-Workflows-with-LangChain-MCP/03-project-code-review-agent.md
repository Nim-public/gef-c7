# 03 — Project: Code Review Agent with LangChain

> Week 14 index: [README.md](README.md)

**Session 1 project:** *Code Review Agent with LangChain — 1. Bug Detection: auto-scan code for bugs, vulnerabilities, and code smells. 2. Performance Boost: identify bottlenecks and suggest optimization improvements. 3. Smart Refactoring: context-aware suggestions following coding standards. 4. Automated Reports: generate prioritized fix lists.*

---

## What you'll learn

- A multi-pass review pipeline: static checks first, LLM review second, report last
- Structured findings (Pydantic) so reports are machine-actionable
- Diff-aware review (review the *change*, not the universe)
- Prioritization as a deterministic sort over classified findings — not an LLM opinion

## 1. Design: deterministic first, LLM second

| Pillar | Owner | Why |
|---|---|---|
| Bug/vuln scanning | **tools**: AST checks, `ruff`/`bandit` | deterministic, zero hallucination |
| Performance/refactoring suggestions | **LLM** over the code + scan results | judgment task |
| Prioritized report | **code** (sort by severity) + LLM prose | ordering must be reproducible |

The anti-pattern this avoids: "the LLM found 6 issues" where a linter finds the same 6 deterministically — and one invented. Static analysis is the grounding for code review, as retrieval is for RAG (W4).

## 2. The scan tool (deterministic layer)

```python
from langchain_core.tools import tool
import subprocess, tempfile, json, ast

@tool
def static_scan(code: str) -> str:
    """Run ruff + bandit-style AST checks on the given code. Returns findings as JSON."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code); path = f.name
    findings = []
    try:
        r = subprocess.run(["ruff", "check", "--output-format", "json", path],
                           capture_output=True, text=True, timeout=30)
        findings += json.loads(r.stdout or "[]")
    except Exception as e:
        findings.append({"rule": "scan-error", "message": str(e)})
    # AST example: flag bare except + exec/eval
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({"rule": "bare-except", "message": f"line {node.lineno}"})
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("exec", "eval"):
            findings.append({"rule": "dangerous-call", "message": f"line {node.lineno}"})
    return json.dumps(findings[:50], indent=1)
```

## 3. Structured findings (the LLM layer)

```python
from pydantic import BaseModel, Field
from typing import Literal

class Finding(BaseModel):
    title: str
    severity: Literal["critical", "major", "minor", "nit"]
    category: Literal["bug", "security", "performance", "style", "refactor"]
    line_hint: int | None = None
    explanation: str
    suggested_fix: str | None = None

class Review(BaseModel):
    findings: list[Finding]
    summary: str

review_chain = (review_prompt | llm.with_structured_output(Review))
```

The review prompt (W3-02 discipline): include the code in a delimited block, the static findings as *facts*, and rules — "report only findings you can point to a line for; do not invent issues; severity by impact not by confidence."

## 4. Prioritized report (deterministic sort)

```python
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "nit": 3}

def build_report(review: Review, scan: list) -> str:
    all_f = sorted(review.findings + [Finding(**f) for f in scan],
                   key=lambda f: SEVERITY_ORDER[f.severity])
    lines = [f"## Code Review — {len(all_f := all_f)} findings", ""]
    for i, f in enumerate(sorted(all_f, key=lambda f: SEVERITY_ORDER[f.severity]), 1):
        fix = f"\n  Fix: {f.suggested_fix}" if f.suggested_fix else ""
        lines.append(f"{i}. **[{f.severity.upper()}] {f.title}** ({f.category}){fix}\n  {f.explanation}")
    lines.append(f"\nPrioritize: {sum(1 for f in all_f if f.severity == 'critical')} critical, "
                 f"{sum(1 for f in all_f if f.severity == 'major')} major.")
    return "\n".join(lines)
```

Ordering is code (reproducible); the prose is the LLM's. This is the "automated reports" pillar done honestly.

## 5. The review agent (assembled)

```python
from langchain.agents import create_agent

reviewer = create_agent(
    model="openai:gpt-4o-mini",
    tools=[static_scan],
    system_prompt=("You are a code reviewer. ALWAYS run static_scan first. Combine its "
                   "findings with your own analysis. Use the structured review format. "
                   "Severity: critical=security/data-loss, major=bugs, minor=quality."),
    response_format=ToolStrategy(Review),
)
```

Pipeline vs agent: a *chained* version (scan → review → report) is deterministic and cheap; the *agent* version lets the model pull extra files/imports for context. Ship chained; agent when multi-file context is real (W3-05).

## 6. Extending: diff-aware PR review

```python
def review_pr(diff: str, full_files: dict[str, str]) -> Review:
    ctx = "\n".join(f"--- {p}\n{src}" for p, src in full_files.items())
    return review_chain.invoke({"diff": diff, "files": ctx[:12000]})
```

Rules: review the *diff* but ground findings in *whole files*; cap context (file 15's cost knobs); post findings as inline PR comments with `line_hint`.

## Exercises

1. Build the reviewer; run it over your own `scripts/ods_to_md.py` and `split_schedule.py`. Which findings do you agree with? Which are noise?
2. Severity calibration: plant 3 known issues (SQL injection string-build, bare except, N+1 loop) — does the review catch all 3 and rank them correctly?
3. False-positive budget: run on 5 clean files; count invented findings. Tune the prompt until ≤1 FP per file.
4. Diff review: create a git diff of a small change; review the diff with full-file context; verify no finding references unchanged lines.
5. Report ordering test: shuffle the LLM's findings order across 3 runs — does your deterministic sort produce identical report order? (It must.)

## Pitfalls

- **LLM inventing line numbers** — `line_hint` is a hint; anchor on code snippets instead of trusting ints
- **Severity inflation** — everything "critical" is noise; calibrate against the deterministic scan
- **Reviewing diffs without file context** — "this line is fine" conclusions that break callers elsewhere
- **No dedup** — static scan + LLM flag the same issue twice; merge by (rule, line) keys
- **Reports without prioritization logic in code** — LLM-chosen order varies run to run

## Resources

- LangChain [structured output](https://docs.langchain.com/oss/python/langchain/structured-output) — the Pydantic patterns here
- [ruff](https://docs.astral.sh/ruff/) + [bandit](https://bandit.readthedocs.io/) — the deterministic layer
- Python `ast` module — custom smell detection (the bare-except pattern)
- W10-04 (severity as metrics), W14-01 (composition) — composed here
