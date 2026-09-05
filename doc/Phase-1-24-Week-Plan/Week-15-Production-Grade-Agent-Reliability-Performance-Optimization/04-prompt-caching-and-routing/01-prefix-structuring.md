# Prefix Structuring — The Stable/Variable Order Rule

**What you'll learn:** prompt caching discounts the *stable prefix* of
your prompt — so the stable content must come first, byte-identical,
and the variable content last. The reorder rule and the audit that
enforces it.

## 1. The rule

```text
STABLE  (cached):  system constitution, tool schemas, few-shot examples,
                   knowledge preamble — byte-identical across calls
VARIABLE (uncached): retrieved context, user query, history tail
```

```python
# WRONG order — variable content interleaved into the prefix:
messages = [
    ("system", f"You are... Context: {context}"),   # ← context changes per call
    ("user", query),
]

# RIGHT order — stable first, variable last:
messages = [
    ("system", CONSTITUTION + TOOLS_DOC + FEWSHOT),  # byte-identical → cached
    ("user", f"Context:\n{context}\n\nQuery: {query}"),  # variable, at the tail
]
```

| Rule | Why |
|---|---|
| stable content first | the cache matches from byte 0 |
| byte-identical | one changed character invalidates from there |
| variable last | the prefix stays cacheable |
| timestamps out of the prefix | a changing date kills the whole prefix |

The reorder is often a 2-line change worth 50–90% off the prompt bill:
your constitution + tool schemas + few-shot examples are ~2k tokens of
*identical* prefix on every call — paid at full price when they sit
after variable content.

## 2. The audit (the prefix's byte-identity check)

```python
def prefix_audit(prompts: list[str], stable_len: int) -> float:
    """Share of calls whose first `stable_len` chars are identical."""
    if not prompts:
        return 0.0
    prefix = prompts[0][:stable_len]
    same = sum(1 for p in prompts if p[:stable_len] == prefix)
    return same / len(prompts)
```

| Audit result | Meaning |
|---|---|
| 1.00 | the prefix is cacheable |
| <1.00 | something variable leaked into the prefix (a timestamp, a count) |

The audit runs on logged prompts after every deploy — the drift that
kills caching (an added timestamp, a reordered example) shows up as a
dropping share before the bill does.

## 3. The reorder checklist

```text
[ ] constitution first (byte-identical)
[ ] tool schemas next (they change only on surface bumps)
[ ] few-shot examples next (versioned with the prompt)
[ ] retrieved context LAST
[ ] user query LAST
[ ] no timestamps/counters in the prefix
```

The checklist is the prompt-architecture review (W10 file 05-07) with
the caching column added — every deployed prompt audited for its
stable/variable split.

## Exercises

1. Reorder one of your prompts to the stable/variable rule; measure the
   byte-identical prefix length before/after.
2. Audit drill: log 20 prompts; run `prefix_audit` on the stable length;
   find and fix the leaking variable.
3. Timestamp drill: add a timestamp to the prefix; watch the audit drop
   to 0; move it to the tail; watch it recover — the rule, proven by
   its violation.