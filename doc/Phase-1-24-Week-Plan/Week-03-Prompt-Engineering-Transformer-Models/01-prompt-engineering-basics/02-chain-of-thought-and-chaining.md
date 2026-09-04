# 01.2 — Chain-of-Thought & Prompt Chaining

> Subfolder index: [README.md](README.md) · Parent: [../01-prompt-engineering-basics.md](../01-prompt-engineering-basics.md)

---

## What you'll learn

- CoT: when reasoning tokens pay, and the cost math
- Chaining: the pipeline pattern with validated seams
- The refine variant: iterative improvement loops

## 1. CoT — the economics

```python
COT_PROMPT = """Classify the ticket. Think step by step:
1. What does the customer actually want?
2. Which system/component is involved?
3. Which category matches? Output the category on the last line as CATEGORY: <name>

Ticket: "{ticket}"
"""
```

The trade: CoT adds reasoning tokens (billed like output, W1-07) in exchange for accuracy on multi-step decisions. The measurement protocol: zero-shot vs CoT on the same 20 cases — accuracy, tokens, latency. The W3-01 §7 exercise produces the table; the decision rule is:

```
use CoT iff  Δaccuracy × value_per_correct  >  Δtokens × token_price
```

For a triage system at 1M tickets/day, +5% accuracy on a 3-class task rarely justifies +3× tokens — which is why production triage uses few-shot, and CoT is reserved for the ambiguous tail (the W15-04 escalation path).

## 2. Structured CoT: reasoning + answer as JSON

```python
STRUCTURED_COT = """Analyze the ticket, then output strict JSON:
{"reasoning": "1-3 sentences", "category": "BILLING|TECHNICAL|ACCOUNT", "confidence": "low|medium|high"}

Ticket: "{ticket}"
JSON:"""
```

Structured CoT keeps the reasoning benefit while making the output parseable — the reasoning field is auditable (you can read *why* it classified that way) without parsing free text. The W13-03 router node uses exactly this shape.

## 3. Prompt chaining with validated seams

```python
def chain(ticket: str) -> dict:
    summary  = ask(summarize_prompt(ticket))
    if len(summary) > 500: summary = ask(f"Compress to 2 sentences:\n{summary}")
    category = classify(summary)
    if category not in {"BILLING", "TECHNICAL", "ACCOUNT"}:
        category = "ACCOUNT"                              # seam fallback (W3-01 §4)
    reply = draft_reply(summary, category)
    return {"summary": summary, "category": category, "reply": reply}
```

The seam checks are the chain's value: each link validates its input before the next link runs. Failure at a seam is *localized* (retry that link) instead of poisoning the whole pipeline (W3-01's argument, now with the code).

## 4. The refine variant (iterative loops)

```python
def refine(draft: str, rubric: str, rounds: int = 2) -> str:
    for _ in range(rounds):
        critique = ask(f"Rubric:\n{rubric}\n\nDraft:\n{draft}\n\nList violations only.")
        if not critique.strip(): break                    # converged
        draft = ask(f"Fix these violations:\n{critique}\n\nDraft:\n{draft}")
    return draft
```

The critique-fix loop is the evaluator-optimizer pattern (Anthropic's taxonomy) — it works when the rubric is objective enough for the model to self-assess. Bound the rounds; verify convergence (the loop can oscillate between two "fixes").

## Exercises

1. The CoT economics table: zero-shot vs CoT vs structured-CoT on 20 cases — accuracy, tokens, latency; compute the §1 inequality with your numbers.
2. Seam-failure injection: make `classify` return garbage 30% of the time; measure how far garbage propagates without vs with the seam fallback.
3. Refine-loop convergence: run the refine loop on 10 drafts; count rounds to convergence and detect oscillation (draft returns to a previous state).
4. The chronology-preserving variant: implement refine for a chronological document (each fix must not contradict earlier sections) — where does naive refinement break chronology?
5. Cost-optimal chain design: given a quality bar, minimize total tokens across the chain — try per-link model routing (W15-04: cheap model for summarize, strong for draft).

## Pitfalls

- **CoT on extraction tasks** — reasoning tokens on "extract the email" are pure overhead
- **Chains without seam validation** — one malformed link poisons everything downstream (W3-01's rule)
- **Refine oscillation** — fix A breaks B, fixing B breaks A; detect state repetition and stop
- **Reasoning fields leaking into user-facing output** — strip `reasoning` before display, keep for audit
- **Unbounded refine rounds** — every loop needs a bound (W10-01's max-steps rule, refinement edition)

## Resources

- Wei et al., *Chain-of-Thought Prompting* — the original (W3-01's source)
- Anthropic, *Building effective agents* — the chaining/evaluator-optimizer patterns
- W10-01/05 (the loop and context rules) — composed here
