# User Contracts — Exception→Message Handler Maps

**What you'll learn:** the exception→message map: every internal failure
class produces a user-facing message that is honest, actionable, and
never leaks internals — the W10 user-contract layer, complete.

## 1. The handler map

```python
HANDLERS = {
    BudgetExhausted: lambda e: (
        "This task exceeded its resource budget. "
        "Try a narrower question, or split it into parts."),
    RateLimitError: lambda e: (
        "The service is busy right now. Please retry in a minute — "
        "your work is saved."),
    ToolError: lambda e: f"A data source failed: {e.hint} "
                          "Try rephrasing, or ask a different question.",
    ValidationError: lambda e: (
        "I couldn't produce a properly formatted answer. "
        "Please rephrase the question."),
    Exception: lambda e: (
        "Something went wrong on our side. The issue has been logged. "
        f"Reference: {e.run_id}"),
}
```

| Rule | Enforced by |
|---|---|
| honest | the message names the failure class |
| actionable | every message names a next step |
| no internals | no stack traces, no paths, no prompts |
| reference id | the last resort carries the run id |

The map is a committed artifact (W12 policies-as-data): the *message*
is the product; the exception is internal. The handler lookup happens
at the boundary — the user never sees a stack trace.

## 2. The two-audience rule (user vs reviewer)

```python
def failure_response(e: Exception, run_id: str) -> dict:
    user_msg = HANDLERS[type(e) if type(e) in HANDLERS else Exception](e)
    reviewer = {"class": type(e).__name__, "detail": str(e)[:300],
                "run_id": run_id, "trace_ref": f"traces/{run_id}.jsonl"}
    log_failure(reviewer)                     # the reviewer path
    return {"answer": user_msg, "run_id": run_id, "degraded": True}
```

| Audience | Gets |
|---|---|
| user | the handler message |
| reviewer/log | the exception class, detail, trace reference |

The W12 display-contract pattern (two renderings): the user view never
contains what the reviewer view needs, and vice versa. The reference id
is the bridge — a user pasting it lets support find the exact trace.

## 3. The contract battery (the map as tests)

```python
CONTRACT_CASES = [
    (BudgetExhausted("time"), "budget", ["narrower", "split"]),
    (RateLimitError("429"), "busy", ["retry"]),
    (ToolError("unit_id 'x' not found; call retrieve()"), "data source",
     ["rephras"]),
    (Exception("Unexpected"), "logged", ["Reference:"]),
]

@pytest.mark.parametrize("exc,must_have", CONTRACT_CASES)
def test_user_contract(exc, must_have):
    msg = HANDLERS[type(exc) if type(exc) in HANDLERS else Exception](exc)
    assert not any(bad in msg.lower() for bad in
                   ("traceback", "exception", ".py", "sk-"))
    for phrase in must_have:
        assert phrase in msg.lower()
```

The battery asserts: no internals leak, the message is actionable, and
the reference id appears on last-resort failures. The leak-check list
grows with every new internal surface.

## Exercises

1. Implement the handler map; wire it at the API boundary; run the
   contract battery.
2. Leak drill: raise an exception whose message contains a file path and
   an API key; the user message must contain neither — the firewall, at
   the boundary.
3. Reference drill: trigger the last-resort path; paste the reference id
   into the trace lookup; the exact run must be findable.