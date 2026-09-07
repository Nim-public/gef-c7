# LCEL Composition — Pipelines, Streaming, Fallbacks, Retries

**What you'll learn:** the pipe syntax as your pipeline's runtime:
composed chains, streaming semantics, and the two resilience primitives
(`with_fallbacks`, `with_retry`) — with the W10 degradation ladder as
their policy.

## 1. The chain

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

chain = (
    {"context": RunnableLambda(fetch_context), "query": RunnablePassthrough()}
    | GROUNDING_PROMPT
    | model
    | RunnableLambda(parse_answer)
)

result = chain.invoke({"query": "Why did margin drop?", "k": 5})
```

The pipe composes runnables left to right; each stage's output feeds the
next. The W9 fixed pipeline, expressed declaratively — same stages, same
guards (the guards live inside `fetch_context` and `parse_answer`, which
are your tested functions).

## 2. Streaming semantics

```python
for chunk in chain.stream({"query": q, "k": 5}):
    print(chunk.content, end="", flush=True)   # token-level if the last
                                               # stage streams

async for event in model.astream_events(prompt_value, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

| Streaming mode | Granularity | Use |
|---|---|---|
| `chain.stream` | per-component output | progress UIs |
| `astream_events` | tokens, starts, ends | token-level UIs (W11 voice file) |

The W11 voice cascade's sentence-streaming (first-TTS-byte trick) maps
to `astream_events`: start TTS on the first sentence boundary token.

## 3. Fallbacks and retries — resilience with policy

```python
primary = model.with_structured_output(Answer)
fallback = fallback_model.with_structured_output(Answer)

robust = primary.with_fallbacks([fallback]).with_retry(
    stop_after_attempt=3, retry_if_exception_type=(RateLimitError,))
```

| Primitive | Semantics | W10 policy source |
|---|---|---|
| `with_retry` | same call, bounded attempts | the retry policy (timeout drills) |
| `with_fallbacks` | different call on failure | the degradation ladder (W8) |

The W10 degradation ladder, mechanized: retries for transient errors
(rate limits, timeouts), fallbacks for provider failures (different
model, different source). The policy decides *which* failures retry vs
fall back — transient gets retry, structural gets fallback.

## 4. LCEL vs graph (when each)

| Shape | LCEL chain | LangGraph |
|---|---|---|
| linear pipeline | `a | b | c` | overkill |
| conditionals | Runnable branching (clunky) | conditional edges (native) |
| cycles | no | native (file 03 of W13) |
| state accumulation | manual | reducers (native) |

The rule from your boundary memo: LCEL for linear chains (preprocessing
→ prompt → model → parse), LangGraph when anything branches or loops.
The two compose — your W13 graphs already contain LCEL-style nodes.

## 5. The LCEL debugging surface (what the pipe exposes)

| Need | LCEL mechanism |
|---|---|
| inspect a stage's input/output | wrap the stage in a logging `RunnableLambda` |
| time a stage | same wrapper, `perf_counter` around the call |
| trace the whole chain | LangSmith callback, or your trajectory merge |

```python
def logged(name: str, fn):
    def inner(x):
        t0 = time.perf_counter()
        out = fn(x)
        log.info("%s in=%.0fms", name, (time.perf_counter() - t0) * 1000)
        return out
    return RunnableLambda(inner)
```

LCEL's abstraction hides the stages unless you instrument them — the
logged wrapper is the minimal observability that keeps the W10 ledger
alive inside a declarative pipeline. The ledger's stages map 1:1 to the
wrapped runnables.

## Exercises

1. Express the W9 hot path as one LCEL chain; run the eval set; verify
   parity with the graph version (same outcomes, same guards).
2. Streaming drill: token-stream an answer; start "TTS" (printing) on
   the first sentence boundary; measure the perceived-latency delta
   (the W11 voice trick, in LCEL).
3. Resilience drill: kill the primary model (bad key); verify the
   fallback serves; count the retry attempts; both events in the
   trajectory rows.
4. Ledger drill: wrap each stage in `logged`; compare the per-stage
   table with the W9-04 ledger — the composition is the same cost model.

## Pitfalls

- Chains with hidden state (closures over mutable globals) — runnables
  should be pure; state belongs in LangGraph or explicit memory.
- `with_retry` on non-idempotent calls — retrying a write is a duplicate;
  retry only idempotent calls (reads, searches).
- Fallbacks that mask systematic failures — a fallback firing 100% of
  the time is a primary-config bug; the harness counts fallback usage.