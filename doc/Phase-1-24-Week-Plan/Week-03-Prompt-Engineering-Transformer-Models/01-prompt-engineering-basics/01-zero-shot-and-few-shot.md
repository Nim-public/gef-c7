# 01.1 — Zero-Shot & Few-Shot: Deep Dive

> Subfolder index: [README.md](README.md) · Parent: [../01-prompt-engineering-basics.md](../01-prompt-engineering-basics.md)

---

## What you'll learn

- The instruction contract: format, role, boundaries, failure behavior
- Few-shot example design: selection, ordering, diversity, and the token budget
- The measured A/B methodology for prompt changes

## 1. The instruction contract

A zero-shot prompt is a specification. The four clauses:

| Clause | Weak | Strong |
|---|---|---|
| Role | "be helpful" | "You are a support triager for AcmeCloud" |
| Format | "categorize it" | `{"category": "...", "confidence": "low\|medium\|high"}` |
| Boundaries | — | "If none fit, category=OTHER" |
| Evidence | — | "Base the label only on the ticket text" |

The strong version is testable: every clause maps to a pytest case (W3-02 §5). The weak version isn't — "helpful" has no pass condition.

## 2. Few-shot example design

```python
FEW_SHOT = """Classify each ticket into BILLING, TECHNICAL, or ACCOUNT.

Ticket: "My card was charged after I cancelled."        -> BILLING
Ticket: "App crashes when I upload a photo."            -> TECHNICAL
Ticket: "I want to change my email address."            -> ACCOUNT
Ticket: "Reset link expired in 5 minutes."              -> ACCOUNT
Ticket: "Refund shows pending for 10 days."             -> BILLING

Ticket: "{ticket}"                                      ->"""
```

Design rules with reasons:

| Rule | Reason |
|---|---|
| 2–5 examples | more = token cost + diminishing returns |
| cover the hard classes (negation, mixed) | the model imitates the examples' *decision boundaries* |
| one example per trap | teaches the boundary, not the obvious case |
| consistent formatting | format variance teaches format variance |
| hardest example nearest the prompt | recency helps (W3-01) |

The example selection is an optimization: swap examples, measure on the eval (W1-05's harness), keep the winner. Few-shot selection is a feature-selection problem.

## 3. The A/B methodology (measure, don't vibe)

```python
import json

PROMPTS = {"v1_zero": zero_shot_prompt, "v2_few": few_shot_prompt, "v3_cot": cot_prompt}
CASES = json.load(open("eval/tickets20.jsonl"))

for name, fn in PROMPTS.items():
    ok = sum(1 for c in CASES if fn(c["text"]) == c["expected"])
    tokens = sum(count_tokens(fn(c["text"])) for c in CASES)
    print(f"{name}: {ok}/{len(CASES)}  ~{tokens} tokens")
```

Every prompt change runs the same harness — accuracy AND token cost. The winning prompt is the one that clears the quality bar at acceptable cost, and the *table* is the evidence (the W3-01 §7 exercise, formalized).

## 4. Boundary design: the escape hatch

Every classifier prompt needs the "none of the above" path:

```python
"Categories: BILLING | TECHNICAL | ACCOUNT\n"
"If the ticket matches none, output {\"category\": \"OTHER\"}.\n"
"Never guess between similar categories — choose OTHER with confidence=low."
```

The escape hatch converts confident wrong answers into flaggable ones — the W5-04 escalation hook at prompt level. Test it: 4 off-domain questions must produce OTHER, not a forced fit.

## Exercises

1. Contract conversion: take 3 weak prompts from your own notes; rewrite each with the four clauses; run the W1-05 harness before/after.
2. Example-swap study: 5 different few-shot sets on the same 20 cases — accuracy table; identify which example carried the most signal.
3. Boundary drill: craft 6 tickets that straddle two categories; design the tie-break rules; verify the model follows them.
4. Token-budget prompt: compress your best prompt to half the tokens without losing accuracy — report the compression and what you cut.
5. The escape-hatch test: 6 off-domain questions; measure OTHER-rate vs hallucinated-category rate.

## Pitfalls

- **Format instructions in prose** — "output JSON" buried in a paragraph gets ignored; put the schema adjacent to the instruction
- **Examples that all share a quirk** — the model learns the quirk (e.g., all examples end with periods → it adds periods to labels)
- **Tie-break rules missing** — ambiguous tickets get confident wrong labels; the OTHER path fixes it
- **Comparing prompts on different eval subsets** — the W1-05 harness discipline, or the A/B is invalid
- **Prompt versions unpinned** — v3 beats v2 means nothing if v3 isn't in git (W3-02)

## Resources

- W3-01 parent, W10-05 (the agentic constitution), W16-01 (versioning) — composed here
- OpenAI [prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) — the six strategies
