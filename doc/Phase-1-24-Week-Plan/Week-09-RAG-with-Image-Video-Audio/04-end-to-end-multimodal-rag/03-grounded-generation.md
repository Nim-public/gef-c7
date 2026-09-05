# VLM Generation — Image-Grounded Cited Answers

**What you'll learn:** the answer stage under quota: build the context
window (images + snippets within budget), generate, then *enforce* the
citation contract before anything reaches the user.

## 1. Context assembly with a token budget

```python
MAX_IMAGE_TOKENS = 1152        # 2 × 576
MAX_TEXT_TOKENS = 2400
BUDGET = {"images": 2, "snippets": 6, "answer": 400}

def build_context(hits: list[dict], question: str) -> list[dict]:
    imgs = [h for h in hits if h["modality"] in ("image", "video")][:BUDGET["images"]]
    snips = [h for h in hits if h["modality"] == "text"][:BUDGET["snippets"]]
    return imgs + snips
```

Budget discipline from the patterns file, in code: images are the scarce
resource; snippets fill; the answer reserve is untouchable.

## 2. The prompt with citation instructions

```python
SYSTEM = ("Answer only from the provided context. Cite units as [unit_id]. "
          "If the context lacks the answer, say so.")

def make_prompt(ctx: list[dict], question: str) -> str:
    lines = [f"[{h['unit_id']}] {h['text'][:400]}" for h in ctx if h["modality"] == "text"]
    return f"{SYSTEM}\n\nContext:\n" + "\n".join(lines) + f"\n\nQuestion: {question}"
```

Images go to the VLM as *images* (projection pattern, W8); text goes in
the prompt; every unit is citable by id — the ids are the contract.

## 3. Citation enforcement (the gate)

```python
def citation_audit(answer: str, cited_ids: set[str],
                   retrieved_ids: set[str]) -> dict:
    issues = []
    if not cited_ids:
        issues.append("no citations")
    phantom = cited_ids - retrieved_ids
    if phantom:
        issues.append(f"phantom citations: {phantom}")
    return {"ok": not issues, "issues": issues}
```

Fail behavior: `ok=False` answers are regenerated once with stricter
instructions, then served flagged `[unverified]` — never silently. This is
the patterns file's degradation ladder, applied to answers.

## 4. The full answer path, under quota

```python
def answer(query: str) -> dict:
    hits = retrieve(query, k=12)
    if route_query(query) != "P3" or p3_quota_exceeded():
        return {"answer": summarize_snippets(hits), "mode": "P1", "citations": hits[:5]}
    ctx = build_context(hits, query)
    ans = vlm_generate(make_prompt(ctx, query), images=[h["path"] for h in ctx if h["modality"] != "text"])
    audit = citation_audit(ans, extract_ids(ans), {h["unit_id"] for h in hits})
    return {"answer": ans, "mode": "P3", "citations": hits[:5], "audit": audit}
```

Two modes in one function: P1 summary by default, P3 on route + quota —
the router's decisions are visible in the response, which is what makes
the eval possible (per-mode faithfulness, next file).

## 5. The answer contract — what `answer()` promises

Freezing the response schema now keeps Week 10's agent stable:

```python
# answer() promises, per response:
#   answer:    str            — the text (never empty; "not found" is valid)
#   mode:      "P1" | "P3"    — which generation path ran
#   citations: list[dict]     — unit_id + score + path, ⊆ retrieved set
#   audit:     dict | None    — ok/issues (P3 only)
#   degraded:  bool           — True iff a fallback fired (quota, audit fail)
```

Five fields, one page of consumer documentation, zero surprises. The
`degraded` flag is the one agents check first — it changes how much they
trust the answer and whether they re-query.

## Exercises

1. Implement `build_context` and verify token counts against the budget
   with your tokenizer — assert, don't eyeball.
2. Break the audit: inject a phantom citation; confirm the response is
   flagged `[unverified]` and the issue is logged.
3. Mode-mix drill: 5 P3 queries and 5 P1 queries through `answer`; check
   the response `mode` field matches the router decision every time, and
   that every response validates against the frozen schema.

## Pitfalls

- Trusting the VLM's citation format — parse defensively (regex over ids),
  expect malformed output on long answers.
- Context assembly without *counting* — 576-token images slip in until the
  prompt overflows; assert the budget.
- Regeneration loops on audit failure — one retry, then flag; infinite
  loops burn quota silently.

## Resources

- Patterns file 04 (token economics, quotas); Week-05 faithfulness harness.
- Your hybrid retriever — the hit list this stage consumes.
