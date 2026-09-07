# 01.3 — Meta Prompting, Multimodal & Variables

> Subfolder index: [README.md](README.md) · Parent: [../01-prompt-engineering-basics.md](../01-prompt-engineering-basics.md)

---

## What you'll learn

- Meta prompting: prompts that write and critique prompts — with the drift guard
- Multimodal prompting: image+text contracts and the extraction pattern
- Variable/templating hygiene at production level (W1-02's rules, agent edition)

## 1. Meta prompting — the draft-critique-rewrite loop

```python
def improve_prompt(prompt: str, failures: list[str], requirements: str) -> str:
    critique = ask(f"""You are a prompt engineer. List 5 ways this prompt could be
misunderstood or fail. Be specific and adversarial.

Requirements: {requirements}
Current prompt: {prompt}
Recent failures: {json.dumps(failures)}""")
    rewrite = ask(f"""Rewrite the prompt addressing these critiques. Return only the
new prompt.\n\nPrompt: {prompt}\nCritiques: {critique}""")
    return rewrite
```

The critique pass is the valuable half: "list 5 ways this could be misunderstood" surfaces real ambiguity. The guard: **generated prompts go through the same eval battery** (W3-02 §5) — a rewrite that regresses accuracy is rejected, no matter how plausible it reads. The loop is: generate → eval → accept/reject → repeat, bounded (W10-01's max-steps rule).

## 2. Meta prompting applied: test generation

The highest-value meta use: generating *test cases* for your own prompt:

```python
CASE_GEN = """Generate 10 diverse tickets that stress this classification prompt:
2 easy, 2 with mixed intent, 2 with typos, 2 non-English, 2 adversarial.
Return JSON: [{{"text": "...", "expected_category": "..."}}]

Prompt under test: {prompt}"""
```

The generated cases are hypotheses — hand-verify labels before adding to the eval set (W16-02's validation discipline). This is how the 20-case mini-eval grows to 50 without manual writing.

## 3. Multimodal prompting — the extraction contract

```python
import base64

def extract_from_screenshot(png_bytes: bytes) -> str:
    b64 = base64.b64encode(png_bytes).decode()
    return ask_multimodal(
        "This is a screenshot of an error dialog. Extract: app name, error code, "
        "suggested fix. If the image contains no error dialog, reply exactly NO_DIALOG.",
        image_b64=b64)
```

Multimodal prompt rules (W2-04's notes, expanded):

| Rule | Reason |
|---|---|
| state the fallback ("reply NO_DIALOG") | prevents hallucinated extractions from unrelated images |
| ask for verbatim text where it matters | VLMs paraphrase OCR; verbatim is checkable |
| request structure | same JSON contracts as text (W3-01) |
| note image preprocessing | resize/quality affects reading (W7-02) |

## 4. Variables — the production templating layer

```python
from string import Template

class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
        self.variables = set(re.findall(r"\$(\w+)", template))

    def render(self, **vars) -> str:
        missing = self.variables - vars.keys()
        if missing: raise KeyError(f"missing: {missing}")
        out = Template(self.template).substitute(**vars)
        assert "$" not in out.replace("$$", ""), "unrendered placeholder"
        return out

tpl = PromptTemplate("Classify: $ticket\nCategories: $cats\nPriority hint: $hint")
```

`string.Template` ($-syntax) avoids the brace-escaping collision with JSON examples (W1-02's f-string trap) — a real ergonomic win for prompt-heavy code. Combined with render-time asserts (no `$` left, budget checked), templates become safe building blocks.

## Exercises

1. The meta loop: improve your W3-02 triage prompt through 3 generate-eval rounds; plot accuracy per round; detect and stop on regression.
2. Test-generation eval growth: generate 20 stress cases (file W2-06's kinds); hand-verify; add the verified ones to the eval set — measure the pass-rate change on the *original* model.
3. Multimodal extraction with verification: 5 screenshots → structured JSON → verify extracted text appears in a companion OCR pass (W2-02's NER/OCR cross-check).
4. Template migration: move 3 f-string prompts to `PromptTemplate` with render asserts; demonstrate a caught missing-variable bug.
5. The adversarial meta drill: ask the model to generate prompts that would *break* your agent — then run them (the W23-03 red-team loop, prompt-generation edition).

## Pitfalls

- **Meta-generated prompts accepted without evals** — plausible rewrites regress accuracy; the battery decides (W3-02's rule)
- **Image prompts without fallbacks** — VLMs describe unrelated images confidently; the NO_DIALOG pattern is mandatory
- **Variables interpolated into instructions** — `$user_input` inside the *system* section is an injection hole (W3-02: user data belongs in the user turn)
- **Template proliferation without versioning** — 12 templates × 3 versions unmanaged; the registry pattern (W3-02 §4) applies
- **Multimodal calls on tiny images** — downscaling below legibility produces confident wrong extractions; check dimensions before sending

## Resources

- W3-01 parent (the techniques), W3-02 (the testing/injection layers) — composed here
- OpenAI [vision guide](https://platform.openai.com/docs/guides/vision) — the multimodal message format
- Anthropic [prompt engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) — the XML-structuring and meta patterns
