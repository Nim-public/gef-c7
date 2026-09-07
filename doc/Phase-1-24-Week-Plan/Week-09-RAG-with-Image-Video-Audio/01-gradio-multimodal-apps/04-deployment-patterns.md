# Deployment Patterns — Local, Spaces, API

**What you'll learn:** the three deployment shapes for a multimodal Gradio
app, their cost/latency profiles, and the checklist that makes a demo day
boring (the goal).

## 1. The three patterns

| Pattern | Best for | Cost | Latency | Gotcha |
|---|---|---|---|---|
| Local (`launch()`) | dev, your demo | free | best | unreachable from outside |
| HF Spaces | shareable public demo | free CPU / paid GPU | queue-dependent | cold starts, 50 GB limit |
| `launch(api=True)` / client | programmatic use | your host | +HTTP overhead | auth is on you |

```python
demo.queue(max_size=8).launch()                    # local
# Spaces: push app.py + requirements.txt to a Space repo; SDK=gradio
demo.queue(max_size=8).launch(api_name="generate") # API exposure per endpoint
```

## 2. Spaces specifics that bite

| Issue | Symptom | Fix |
|---|---|---|
| Cold start | first request ~2–5 min (model download) | pin model cache or accept + display |
| Sleep on free tier | Space sleeps after 48 h idle | paid dup or wake link |
| Secrets | keys in repo | Space **Settings → Secrets**, read via `os.environ` |
| Big models | >50 GB repo limit | download at runtime from Hub |

```python
# requirements.txt pins — Spaces builds from scratch every push
# gradio==4.* ; diffusers==0.* ; torch==2.* ; transformers==4.*
```

Pin exact versions: Spaces rebuilds the environment on every push, and a
floating dependency is a demo-day outage.

## 3. The API pattern: your app as a tool

Week 10 (agents) will call your RAG *as a tool* — the contract starts here:

```python
def retrieve(query: str, k: int = 5) -> list[dict]:
    """JSON-in, JSON-out; no UI types in the signature."""
    return [{"unit_id": i, "score": s, "caption": c} for i, s, c in hits]

demo.queue().launch(api_name="retrieve")
```

Rules: handlers separate from UI (pure functions), JSON-serializable
returns, named endpoints. The UI is a shell over the same functions your
agent will call — one codebase, two consumers.

## 4. The demo-day checklist

```text
[ ] cold start rehearsed (or model pre-cached)
[ ] seed 42 fallback image pre-generated
[ ] queue limits set (max_size, timeouts)
[ ] secrets via env vars — `git status` clean
[ ] fallback path when a modality is down (W8 fusion: degrade, don't crash)
[ ] run tuple displayed with every generated artifact
```

## 5. Monitoring the deployed app — the minimum viable set

| Signal | Where | Alert threshold |
|---|---|---|
| p95 latency | your ledger, logged per request | > 2× baseline |
| error rate | handler try/except counter | > 1% |
| queue depth | `queue.max_size` headroom | sustained > 50% |
| disk (cache/models) | Space metrics | > 80% |

```python
import logging, time

log = logging.getLogger("app")

def timed_handler(fn):
    def wrap(*args, **kw):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kw)
        finally:
            log.info("latency_ms=%.0f fn=%s", (time.perf_counter() - t0) * 1000, fn.__name__)
    return wrap
```

A structured log line per request is the whole monitoring stack for a
capstone demo — grep-able, exportable, and enough to answer "was it slow
for everyone or just you" after the fact.

## Exercises

1. Deploy the cataloger to a free CPU Space; measure cold-start and
   steady-state search latency; record both in `reports/deployment.md`.
2. Add API auth: a token header check in the handler; verify `curl` with
   and without the token.
3. Kill a component (point BLIP at a bad path) and verify the app degrades
   to CLIP-only search with a visible banner — the fusion file's graceful
   degradation, in production shape.

## Pitfalls

- Testing only on your machine where models are cached — Spaces cold start
  is the real first impression; rehearse it.
- `os.environ` reads at module import *before* Secrets load — read lazily
  inside handlers.
- Demo numbers quoted from your laptop on a CPU Space — 5–20× slower; re-measure after deploy.

## Resources

- Gradio deploying guide (Spaces, API pages); HF Spaces docs (secrets, hardware).
- Your fusion degradation matrix (W8) — the fallback column here.
