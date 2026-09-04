# 02.2 — Multi-Turn & Prompt Assembly

> Subfolder index: [README.md](README.md) · Parent: [../02-system-prompts-testing-injection.md](../02-system-prompts-testing-injection.md)

---

## What you'll learn

- History as an engineered structure: turns, summaries, re-injections
- Assembly with render-time validation
- The token-budget allocation across prompt sections

## 1. History engineering (the three operations)

| Operation | Mechanism | Use |
|---|---|---|
| **Trim** | drop oldest turns under budget | simple sessions |
| **Summarize** | compress old turns into a recap | long sessions needing continuity |
| **Re-inject** | pin critical facts into every turn | facts that must never age out |

```python
def assemble_turn(history, question, facts, budget=6000):
    parts = [SYSTEM]
    if facts: parts.append(f"Known facts: {'; '.join(facts)}")
    turns = trim_for_budget(history, budget - count(SYSTEM) - count(question) - 200)
    parts += turns
    parts.append(f"User: {question}")
    return parts
```

The budget is allocated *top-down*: system (fixed) → facts (pinned) → question (reserved) → history (whatever remains). The allocation order is the design — history gets the leftover, never the priority.

## 2. Summarization quality (what survives compression)

| Content | Survives summarization? |
|---|---|
| decisions and commitments | mostly — verify names/dates |
| numbers and IDs | **often lost or mangled** — re-inject verbatim |
| tone/context | partially |
| step-by-step reasoning | no — keep recent turns raw |

Rule: anything the *next* answer depends on numerically gets re-injected verbatim; the summary carries narrative only. The E9-02 compression table (W18-03's techniques) applies at turn scale.

## 3. Assembly with render-time validation

```python
def validate_assembled(messages, max_tokens=8000):
    joined = "\n".join(str(m.get("content", "")) for m in messages)
    problems = []
    if "None" in joined: problems.append("None rendered")
    if count_tokens(joined) > max_tokens: problems.append("over budget")
    if messages[0]["role"] != "system": problems.append("no system message")
    if any("{" in str(m.get("content", "")) for m in messages[1:]):
        problems.append("unrendered placeholder")
    return problems
```

The four checks run on **every assembled request** — in dev they assert, in prod they log and degrade (W15-01's contracts). The checks catch: template regressions, None leakage, budget overruns, missing constitutions.

## 4. The multi-turn drift problem

Long sessions erode the constitution's effect — the model's behavior drifts toward the conversation's local pattern. Countermeasures:

| Measure | Mechanism |
|---|---|
| periodic re-anchoring | re-state the constitution compactly every N turns |
| per-turn goal restatement | the user-turn header carries the current task |
| drift detection | behavioral checks on a sample of turns (W3-02 §5) |
| session rotation | long sessions restart with a summary + fresh constitution |

## Exercises

1. Drift measurement: 30-turn conversation; test constitution adherence at turns 5/15/30 — plot the adherence decay; find your re-anchor interval.
2. Summarization information audit: summarize 16 turns; list everything the summary lost; classify lost items as acceptable/unacceptable.
3. Budget allocator: implement the top-down allocation (§1) with a per-section report; test with an oversized few-shot block.
4. Re-injection policy: define which facts never age out for your assistant; test that a 40-turn session still honors them.
5. Assembly fuzz: random-valid inputs through `validate_assembled` — find the input that produces the weird failure.

## Pitfalls

- **Summary hallucination** — the recap invents decisions; verify summaries against the turns they compress (W16-02's validation)
- **Facts in summaries instead of re-injection** — numbers degrade in compression; verbatim re-inject anything numeric
- **Trim boundary conditions** — popping the wrong index deletes the system message or the current question
- **Budget checks after the call** — check before sending; the API bills the overrun
- **Turn ordering assumptions** — assistant turns must alternate; validate the sequence shape, not just content

## Resources

- W3-02 parent, W10-05 (the fitter), E9-01/02 (memory tiers and compression) — composed here
- W15-05 (the ledger these budgets feed)
