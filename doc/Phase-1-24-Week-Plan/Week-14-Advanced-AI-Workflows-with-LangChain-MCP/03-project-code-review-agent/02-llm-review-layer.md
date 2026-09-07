# The LLM Review Layer — Structured Finding Models

**What you'll learn:** the LLM review as structured `Finding` models:
what the model judges, the schema that binds it, and the sampled QA
that keeps the judgment honest.

## 1. The Finding model

```python
from pydantic import BaseModel, Field

class Finding(BaseModel):
    severity: str = Field(description="critical|major|minor|nit")
    category: str = Field(description="correctness|security|style|design|tests")
    line_hint: int = Field(description="1-based line in the file")
    claim: str = Field(description="the issue, one sentence")
    suggestion: str = Field(description="the fix, one sentence")
    confidence: float = Field(ge=0, le=1)

class Review(BaseModel):
    findings: list[Finding]
    summary: str
```

| Field | Consumer |
|---|---|
| `severity` | the deterministic sort (file 03) |
| `category` | report grouping |
| `line_hint` | diff cross-reference (file 04) |
| `claim` + `suggestion` | the review's substance |
| `confidence` | the sampled-QA gate |

The model is the W11 `Answer` pattern for code: every judgment carries
its evidence (line) and its fix.

## 2. The review prompt (deterministic findings in context)

```python
REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a code reviewer. You will see: (1) deterministic scanner "
     "findings (facts), (2) the full file. Judge what the scanners "
     "cannot: naming, design, missing tests, logic risks. Only report "
     "issues you are confident exist. Never restate scanner findings."),
    ("human", "Scanner findings:\n{scan_findings}\n\nFile:\n{source}"),
])
review_chain = REVIEW_PROMPT | model.with_structured_output(Review)
```

The instruction does two things the W10 constitution taught: *do not
restate* the deterministic layer (no duplicate findings), and *judge
what it cannot* (the LLM's actual value). The structured output makes
every judgment auditable.

## 3. The sampled QA (judgment needs verification too)

```python
def sample_for_review(findings: list[Finding], rate: float = 0.3) -> list[Finding]:
    rng = random.Random(hash(tuple(f.line_hint for f in findings)))
    return rng.sample(findings, max(1, int(len(findings) * rate)))
```

| QA check | Method |
|---|---|
| line_hint accuracy | the line exists and mentions the claim's subject |
| severity consistency | the same issue class → same severity across runs |
| suggestion plausibility | a human reads it (30% sample) |

The sampled hand-check is the W10 judge protocol: label 10 findings,
measure agreement, fix the prompt when agreement drops. Code review
findings that point at wrong lines are worse than no findings.

## 4. The deduplication rule (scanners + LLM)

```python
def dedupe(deterministic: list[dict], llm: list[Finding]) -> list[Finding]:
    keep = []
    scan_lines = {f["line"] for f in deterministic}
    for f in llm:
        if f.line_hint in scan_lines and f.category in ("style",):
            continue                     # scanner owns style at that line
        keep.append(f)
    return keep
```

The dedup rule: deterministic findings own their rules *at their lines*;
the LLM layer complements, never duplicates. The report (file 03) marks
each finding's source — reviewers trust it more when provenance is
explicit.

## Exercises

1. Build the review layer over the AST+ruff findings; run it on a
   deliberately bad file; every Finding must have a plausible line_hint.
2. Dedup drill: craft an LLM finding that duplicates a scanner finding;
   the dedup must drop it; the merged report is the proof.
3. Sampled-QA drill: hand-check 30% of findings on 3 files; the
   agreement rate goes in the pin note (the W9 judge protocol).

## 5. The review-prompt calibration (the Finding model's rubric)

The severity rubric lives in the prompt verbatim (W11 file 03-06's
table) — and the sampled QA grades *consistency* against it:

| Rubric element | Graded by |
|---|---|
| severity classes | two-run self-consistency + hand labels |
| category classes | dedup + grouping sanity |
| line_hint accuracy | the diff audit (file 04) |

The calibration loop is the W9 judge protocol: hand-label, self-
consistency check, reword the rubric where agreement drops. The Finding
model is the rubric's data form; the prompt is its prose form; both
carry version stamps (`rvN`), because a rubric edit is a model-behavior
change.

## Exercises

1. Build the `Finding`/`Review` models; run the LLM layer with the
   scanner findings in context; run the dedup; hand-check 30% of
   findings (the sampled QA).
2. Dedup drill: an LLM finding that duplicates a scanner finding; the
   dedup must drop it; the merged report is the proof.
3. Sampled-QA drill: hand-check 30% of findings on 3 files; the
   agreement rate goes in the pin note (the W9 judge protocol).

## Pitfalls

- Findings without line hints — unanchored judgment is noise; the schema
  requires the hint.
- The LLM re-reporting lint findings — the dedup + prompt rules prevent
  it; the merged report verifies.
- Confidence scores treated as calibrated — same rule as W13: measure
  the accuracy per bucket before gating on the number.