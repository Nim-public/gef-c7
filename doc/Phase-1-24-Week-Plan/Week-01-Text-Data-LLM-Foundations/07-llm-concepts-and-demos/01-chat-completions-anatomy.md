# 07.1 — Chat Completions Anatomy

> Subfolder index: [README.md](README.md) · Parent: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md)

---

## What you'll learn

- The request and response objects, field by field
- Usage accounting: reconciling tokens against your own counts
- Error classes and their handling

## 1. The request, field by field

```python
from openai import OpenAI

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",                       # pinned, not "latest" (W2-01)
    messages=[...],                            # the state (W7-02)
    temperature=0,                             # distribution shaping (W7-03)
    max_completion_tokens=500,                 # output cap
    stop=["\n\n"],                             # stop sequences
    seed=42,                                   # best-effort reproducibility
)
```

| Field | Gotcha |
|---|---|
| `model` | provider can deprecate ids — pin and watch changelogs (E8-01) |
| `messages` | stateless — *you* resend history every call (file 07.2) |
| `max_completion_tokens` | caps **output only**; separate from context window |
| `stop` | list of strings; generation halts *before* emitting them |
| `seed` | best-effort determinism; identical seeds aren't guaranteed across infra changes |

## 2. The response, field by field

```python
choice = resp.choices[0]
print(choice.message.content)          # the answer text
print(choice.finish_reason)            # 'stop' | 'length' | 'tool_calls' | 'content_filter'
print(resp.usage.model_dump())         # prompt_tokens, completion_tokens, total
print(resp.id, resp.created)           # for trace joins (W10-04)
```

`finish_reason` is the field everyone ignores and everyone needs:

| Value | Meaning | Action |
|---|---|---|
| `stop` | model ended naturally | proceed |
| `length` | hit the token cap | answer truncated — extend cap or summarize |
| `content_filter` | provider safety layer fired | handle per policy (W15-02) |
| `tool_calls` | model wants a tool | execute (W10-01's loop) |

## 3. Usage accounting — reconcile with your own counts

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
own_count = len(enc.encode("your prompt here"))

print(own_count, resp.usage.prompt_tokens)     # close but not identical — templates/overhead
```

Provider counts include chat-template overhead (role markers, special tokens) that raw text counting misses — expect your count to be slightly *below* theirs. Reconcile once per model so your budget estimates (W15-05, E8-03) aren't built on fiction.

## 4. Error classes and handling

```python
from openai import RateLimitError, APIConnectionError, BadRequestError, InternalServerError

try:
    resp = client.chat.completions.create(...)
except RateLimitError:        # 429 — retryable with backoff (W15-01)
    ...
except APIConnectionError:    # network — retryable
    ...
except BadRequestError as e:  # 400 — NOT retryable; fix the request
    raise ValueError(f"bad request: {e}") from e
except InternalServerError:   # 5xx — retryable, but circuit-break after N
    ...
```

The retryable-vs-not split is exactly file W15-01's table — the exception types are the implementation.

## Exercises

1. Field census: make 5 calls with varied parameters; dump `resp.model_dump()` — map every field to its meaning; find the ones your code never reads.
2. `finish_reason` survey: craft calls that produce `stop`, `length`, and `content_filter` — build the handler map (W15-01 §3).
3. Reconciliation: count 10 prompts with tiktoken; compare to `usage.prompt_tokens` — compute the template overhead constant for your model.
4. Error drill: force each error class (bad model name, malformed messages, tiny rate limit) — verify your handler map produces the right user outcome.
5. Cost audit: reconcile your W1-05 §4's cost estimates against real `usage` — where does the estimate drift?

## Pitfalls

- **Reading `content` when `finish_reason == "content_filter"`** — may be None; handle before using
- **`max_completion_tokens` vs context window confusion** — the output cap is not the memory limit (W11-01)
- **Swallowing `BadRequestError` in retries** — retrying a 400 wastes money and hides the bug (W15-01)
- **No request ids logged** — without `resp.id` you cannot debug provider-side issues (W10-04)
- **Assuming `usage` is optional** — some proxies omit it; your cost ledger needs a fallback path (E8-03)

## Resources

- OpenAI [Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat) — the field-by-field source
- W1-07 parent, W15-01 (error handling), W10-04 (tracing) — composed here
