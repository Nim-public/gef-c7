# Numeric Grounding — `numbers_supported` Checks

**What you'll learn:** the numeric-grounding check as data: every number
in the answer carries the check that produced it (`numbers_supported`),
and the harness audits the pairing.

## 1. The check contract

```python
class NumberCheck(BaseModel):
    value: float
    source: str = Field(description="pandas code or tool that produced it")
    verified: bool = Field(description="independent check agreed")

class AnalysisResult(BaseModel):
    answer: str
    numbers_supported: list[NumberCheck] = []
    charts: list[str] = []
    caveats: list[str] = []
```

| Field | Rule |
|---|---|
| `value` | must appear verbatim in `answer` |
| `source` | the exact code/tool output line |
| `verified` | True only if an independent check ran |

The W12 provenance trio (value, source, as-of) and the W13 verification
node merge here: `numbers_supported` is the answer's numeric audit
trail, *in* the typed output.

## 2. The audit: numbers ↔ checks pairing

```python
def audit_numeric_pairing(r: AnalysisResult) -> list[str]:
    issues = []
    numbers_in_answer = extract_numbers(r.answer)
    supported = [n.value for n in r.numbers_supported]
    for n in numbers_in_answer:
        if n not in supported:
            issues.append(f"unsupported number in answer: {n}")
    for n in r.numbers_supported:
        if not n.verified and "total" in r.answer.lower():
            issues.append(f"unverified total: {n.value}")
    return issues
```

| Failure | Caught by |
|---|---|
| number in answer, no check | the pairing audit |
| unsupported total | the totals rule |
| check whose value never appears | orphaned check (stale) |

The audit is the W12 `numeric_gate` (numbers require provenance),
generalized to *lists* of checks — the analytics answer's every figure
is paired to its derivation.

## 3. The verification flow (short loop)

```text
1. agent computes → draft answer + numbers_supported
2. harness audit   → pairing check (above)
3. mismatch        → caveat or recompute (the W12 mismatch drill)
```

The flow is the W13 verification node's three-way route, LCEL-shaped:
the pairing audit is a `RunnableLambda` at the chain's end, and its
failures feed the same degradation ladder.

## 4. The numeric eval (the capstone metric)

| Case | Numbers | Expected checks |
|---|---|---|
| "average margin" | 1 | source = the pandas line |
| "revenue by quarter" | 4 | one check per value |
| "top product" | 1 + order | verified=True |
| "how many rows" | 1 | trivially verified |

The W12 numeric eval set (file 02) with the check list — the strictest
scoring, now checking provenance as well as value.

## Exercises

1. Implement `NumberCheck` extraction in the analyze feature; run 5
   numeric queries; every number paired.
2. Audit drill: delete one check from a result; the pairing audit must
   flag it; wire the audit into the harness gate.
3. Verified-flag drill: an unverified total must carry a caveat (the W12
   rule); test both branches.

## 5. The grounding pin note

**Task:** extend `reports/sdk-versions.md` with the numeric-grounding
stack: `NumberCheck` schema version, the pairing-audit rule set, and the
audit-drill command.

**Worked approach:** the grounding stack is the CSV project's honesty
layer — the pin note records the pairing rules (every number sourced,
totals verified) and the drill that proves them.

**Pass criterion:** note committed; the audit-drill command green as
recorded.

## 6. The grounding demo (the reviewer's view)

The demo shows one numeric answer in both views: the user sees the
number and its caveat status; the reviewer sees `numbers_supported` —
each check's code and verified flag. The pairing audit runs live, and
the reviewer can delete a check in the UI to watch the audit flag it.

## Exercises (continued)

5. Two-view drill: render one numeric answer in user and reviewer views;
   the user view must not leak the raw code; the reviewer view must show
   every check.

## Pitfalls

- `numbers_supported` filled with the answer's own restatement — the
  source must be the *deriving* code, not prose.
- Verified=True from a non-independent check — the W12 independence rule
  survives; same-query verification is theater.
- Numbers formatted differently in answer vs checks — the audit extracts
  with one parser; keep formatting canonical.