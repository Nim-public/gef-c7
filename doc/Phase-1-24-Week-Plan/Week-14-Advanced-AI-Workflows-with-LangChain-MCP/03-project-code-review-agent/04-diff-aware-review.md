# Diff-Aware Review — Full-File Context, Line Hints

**What you'll learn:** reviewing *changes* rather than whole files: the
diff as the unit of attention, full-file context for the model, and
line hints that map findings onto changed lines.

## 1. The diff as the review unit

```python
import subprocess

def changed_lines(path: str) -> set[int]:
    diff = subprocess.run(["git", "diff", "HEAD", "--", path],
                          capture_output=True, text=True).stdout
    lines = set()
    new_line = 0
    for ln in diff.splitlines():
        if ln.startswith("@@"):
            new_line = int(ln.split("+")[1].split(",")[0].split()[0]) - 1
        elif ln.startswith("+") and not ln.startswith("+++"):
            new_line += 1
            lines.add(new_line)
    return lines
```

The diff-aware review reads the *changed* lines and reviews them with
the full file as context — the reviewer's actual job. Whole-file
reviews on unchanged code waste the LLM budget and bury signal.

## 2. The prompt with full-file context

```python
DIFF_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Review the CHANGED LINES in the context of the FULL FILE. "
     "Findings must reference lines in the diff. Ignore unchanged code "
     "unless the change interacts with it."),
    ("human", "Diff (changed lines marked):\n{diff}\n\n"
              "Full file:\n{source}\n\n"
              "Scanner findings:\n{scan_findings}"),
])
```

| Input | Role |
|---|---|
| the diff | what changed (the review's scope) |
| the full file | context (why the change is wrong/right) |
| scanner findings | the deterministic facts |

The prompt's one rule — findings must reference changed lines — is
enforced by the harness: a `line_hint` outside `changed_lines` is a
formatting violation the audit rejects.

## 3. The line-hint audit

```python
def audit_line_hints(findings: list[Finding], changed: set[int]) -> list[str]:
    return [f"finding at L{f.line_hint} is outside the diff"
            for f in findings if f.line_hint not in changed]
```

| Failure | Caught |
|---|---|
| findings on unchanged lines | the audit |
| line hints off-by-one | the audit (hint must be in the set) |
| findings about deleted code | the audit (deleted lines aren't in the new diff) |

The line-hint audit is the citation gate's diff edition: findings cite
lines like answers cite units — and the pairing is enforced.

## 4. The review in CI (the capstone tie-in)

```yaml
# .github/workflows/review.yml (excerpt)
- run: py scripts/review_agent.py --diff HEAD~1 --out reports/reviews/
```

| Trigger | Scope |
|---|---|
| every PR | the PR's diff |
| nightly | the day's commits |
| pre-demo | the full changed set |

The review agent's capstone role: it reviews *your* capstone PRs — the
program reviewing itself. The findings land in the same reports
directory family as every other artifact.

## Exercises

1. Build `changed_lines`; test it on a fixture diff (adds, modifies,
   context lines); the set must match a hand count.
2. Diff-aware drill: review a fixture diff; every finding's `line_hint`
   must be in `changed_lines` — the audit enforces scope.
3. Off-by-one drill: plant a finding one line above the change; the
   audit rejects it; fix the parser, not the audit.
4. CI drill: open a fixture PR; the review comment appears with
   severity-sorted findings scoped to the diff.
5. Pin-note drill: extend `reports/sdk-versions.md` with the review
   stack (ruff version, Finding schema, CI trigger, determinism
   command).

## 6. The review depth settings (the budget's dial)

| Setting | Whole-file review | Diff review | Effect |
|---|---|---|---|
| context tokens | full file × files | full file × changed | diff saves on big files |
| LLM scope | everything | changed lines + interactions | focused findings |
| noise floor | restates existing issues | only new/interacting | the scope rule |

The depth settings are the review's budget dial — the line-hint audit
is what keeps the diff review honest (findings scoped to changes). The
whole-file mode remains available for initial reviews; the diff mode is
the CI default.