# 02.2 — f-strings & Prompt Templating

> Subfolder index: [README.md](README.md) · Parent: [../02-string-manipulation-and-regex.md](../02-string-manipulation-and-regex.md)

---

## What you'll learn

- f-string mechanics: expressions, format specs, escaping braces
- Building parameterized prompt functions that are testable
- The template patterns used throughout this program (W3-01, W10-05)

## 1. f-string mechanics

```python
name, score = "triage", 0.8742

f"model={name!r} score={score:.1%}"        # "model='Score agent' score=87.4%"
f"{n:,} tokens"                            # '1,250,000 tokens'
f"{n:>8}" / f"{n:<8}" / f"{n:^8}"          # align left/right/center, width 8
f"{pi:.3f}"                                # '3.142'
f"{obj!r}" vs f"{obj}"                     # repr vs str
```

Formatting specs: `[[fill]align][width][,][.precision][type]`. The three you'll use constantly: `.Nf` (decimals), `,` (thousands), alignment with width (logs/tables).

## 2. Escaping: the JSON-in-template trap

```python
# WRONG — NameError: 'category' is not defined
tpl = 'Return {"category": "billing"}'

# RIGHT — double the literal braces
tpl = 'Return {{"category": "billing"}}'

# with .format() the same rule applies:
"{{literal}} {value}".format(value=42)     # '{"category": ...}' works via format_map
```

Every `{{` in a template becomes `{` after rendering — which is why W3-01's rule exists: **JSON examples inside f-string templates need doubled braces**, and forgetting them produces runtime errors on unrelated data.

## 3. Prompt functions (the pattern this program uses)

```python
def grounded_prompt(question: str, contexts: list[dict], k_note: str = "") -> str:
    blocks = "\n\n".join(
        f"<context id='{c['id']}' source='{c['source']}'>\n{c['text']}\n</context>"
        for c in contexts)
    return (
        "Answer using ONLY the context blocks.\n"
        "Cite as [doc:id]. If insufficient: say so.\n\n"
        f"{blocks}\n\nQuestion: {question}{k_note}")
```

Properties that make it testable: pure function, explicit parameters, delimiting built in (W3-02), no hidden state. The W3-01 pattern `triage_prompt(ticket, categories, few_shot)` generalizes exactly this.

### Multi-line and conditional content

```python
def build(messages: list[dict], include_history: bool = True) -> str:
    parts = [f"## Instructions\n{SYSTEM}"]
    if include_history:
        parts.append("## History\n" + "\n".join(f"- {m}" for m in history))
    parts.append(f"## Question\n{question}")
    return "\n\n".join(parts)
```

Conditional sections as list-assembly beat one giant nested f-string — readable and unit-testable per section.

## 4. Validation layer (render-time asserts)

```python
import string

class SafeTemplate(string.Template):       # $-based substitution, strict on missing
    pass

def render(template: str, **vars) -> str:
    out = SafeTemplate(template).substitute(**vars)   # raises KeyError on missing
    assert "None" not in out, "rendered None — check inputs"
    assert len(out) < 30000, "context budget exceeded"
    return out
```

Three render-time checks from W10-05: no unrendered placeholders, no `None`, token/length budget. `str.format_map` with a defaultdict gives lenient mode; `substitute` gives strict mode — choose deliberately per pipeline stage.

## 5. Template testing pattern

```python
def test_grounded_prompt_renders():
    p = grounded_prompt("q?", [{"id": "d1", "source": "s", "text": "t"}])
    assert "<context id='d1'" in p and "Question: q?" in p

def test_grounded_prompt_empty_context():
    p = grounded_prompt("q?", [])
    assert "I don't have" not in p      # escape lives downstream, not in the template
```

## Exercises

1. Build `triage_prompt` (W3-01 §7's signature) with a JSON example inside — demonstrate the brace-escaping bug and its fix.
2. Write 5 formatting tests for your f-strings: currency, percentages, alignment — pin exact outputs.
3. Build `render(template, **vars)` with strict missing-variable behavior + budget assert; test both failure paths.
4. Conditional prompt assembly: build a prompt whose few-shot section appears only when confidence history is low — unit-test both branches.
5. Localization prep: extract all user-visible strings from one function into a dict keyed by locale; render English and Hindi versions of the same prompt.

## Pitfalls

- **Single braces in literal JSON** — the classic runtime NameError; double them
- **Multiline f-strings before 3.12** — nested same-type quotes fail pre-3.12; use different quote styles or join
- **Silent None rendering** — `f"{None}"` → "None" in your prompt; assert at render time
- **Building prompts by concatenation across modules** — hidden state; centralize templates (W3-02 files)
- **format_map with user input** — arbitrary attribute access via format strings; use explicit vars only

## Resources

- [Formatted string literals](https://docs.python.org/3/reference/lexical_analysis.html#f-strings) — the spec
- [string.Template](https://docs.python.org/3/library/string.html#template-strings) — safe substitution
- W3-01/02 — the consumers; W10-05 (validation asserts) — the render-time discipline
