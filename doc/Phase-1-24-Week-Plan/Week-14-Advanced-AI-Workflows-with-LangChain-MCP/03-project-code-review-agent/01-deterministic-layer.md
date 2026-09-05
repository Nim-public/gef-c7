# The Deterministic Layer — AST and Ruff Findings

**What you'll learn:** the scan layer that cannot hallucinate: AST
walks for structural facts, ruff for style/lint facts — the findings
that anchor the LLM layer's judgment to verifiable evidence.

## 1. The AST walk

```python
import ast

def ast_findings(source: str) -> list[dict]:
    tree = ast.parse(source)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            if not ast.get_docstring(node):
                findings.append({"rule": "missing-docstring",
                                 "line": node.lineno,
                                 "detail": f"function '{node.name}' has no docstring"})
        if isinstance(node, ast.Compare) and any(
                isinstance(op, ast.Eq) for op in node.ops):
            pass  # example placeholder rule; real rules below
    return findings
```

| AST check | What it proves |
|---|---|
| missing docstrings | API hygiene |
| bare `except:` | swallowed errors (the W10 anti-pattern) |
| `eval`/`exec` calls | the sandbox rule, statically |
| functions > 50 lines | complexity |

The AST layer's power is *falsifiability*: a bare-except finding cites
a line number; anyone can verify it in seconds. These findings are the
review's facts — the LLM layer argues around them, never replaces them.

## 2. Ruff as the second scanner

```python
import subprocess

def ruff_findings(path: str) -> list[dict]:
    proc = subprocess.run(["ruff", "check", path, "--output-format", "json"],
                          capture_output=True, text=True)
    return json.loads(proc.stdout or "[]")
```

Ruff covers what a hand-rolled AST walk should not reinvent: style,
imports, known bug patterns. Its findings carry rule codes (`E501`,
`F401`) — deterministic, versioned with the ruff version in the pin
note.

## 3. The layered architecture

```text
source code
  ├─▶ AST walk      → structural facts   (deterministic)
  ├─▶ ruff          → lint findings      (deterministic)
  └─▶ LLM review    → judgment findings  (typed, sampled for QA)
        ↓
   merged report (file 03)
```

| Layer | Output | Trust |
|---|---|---|
| deterministic | findings with line numbers | facts |
| LLM | `Finding` models | judgment — verified by sampling |

The architecture is the numeric-grounding pattern (W12 file 04)
inverted: facts from tools, judgment from the model, the report binding
both. The LLM layer *sees* the deterministic findings — its job is the
judgment calls they cannot make (naming, design, missing tests).

## Exercises

1. Build the AST walk; run it on a deliberately bad file (bare excepts,
   no docstrings); every finding must cite a line.
2. Ruff drill: pin the ruff version; verify findings' rule codes are
   stable across two runs.
3. Layer drill: feed the deterministic findings into the LLM prompt;
   the review must *reference* them, not re-discover them.

## Pitfalls

- LLM-only reviews — they hallucinate line numbers and miss mechanical
  issues; the deterministic layer exists because of that.
- AST walks without error handling — unparseable files crash the scan;
  quarantine them like corrupt CSVs (W7).
- Ruff findings reformatted into prose — keep the rule codes; they are
  the audit handle.