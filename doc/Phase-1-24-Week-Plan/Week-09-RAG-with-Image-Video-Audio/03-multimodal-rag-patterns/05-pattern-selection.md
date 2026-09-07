# Pattern Selection — The Routing Table

**What you'll learn:** patterns are per-*query*, not per-corpus: the router
classifies each query and dispatches to P1, P2, or P3 — this file builds
the routing table, the router's rules, and the eval that keeps it honest.

## 1. The routing table

| Query class | Detector (regex/embedding) | Route | Rationale |
|---|---|---|---|
| Exact terms, codes, names | `[\w-]*\d[\w-]*`, quotes | P1-OCR / FTS-lean | dense misses rare tokens |
| Scene/object lookup | generic phrasing, no domain terms | P2 (CLIP space) | captions flatten scenes |
| Chart/data questions | "chart", "graph", "margin", "table" | P1-merged + P3 quota | numbers live in OCR |
| Anything, low-latency | default | P1-merged | cheapest grounded path |
| "What exactly does X show" | "exactly", "show", zoom-ins | P3 | pixel grounding needed |

```python
import re

def route(query: str) -> str:
    if re.search(r"\b\w*\d\w*\b|\".+\"", query):        # codes or quoted
        return "P1-fts"
    if re.search(r"\b(chart|graph|table|margin|revenue)\b", query, re.I):
        return "P1-merged"
    if re.search(r"\b(exactly|zoom|show me)\b", query, re.I):
        return "P3"
    return "P2"
```

## 2. The router is a classifier — evaluate it like one

The routing table's rows come from *your* eval data: 20+ queries per class
with the measured best pattern (from files 02–04). The router's accuracy =
does it send each query to its measured-best route?

```python
def router_accuracy(queries: list[tuple[str, str]], gold: dict[str, str]) -> float:
    return float(np.mean([gold[q] == route(q) for q, _ in queries]))
```

Gold labels come from the pattern-comparison evals — the router is
*derived* from measurements, exactly like every decision memo in this
program.

## 3. Fallbacks and the degradation ladder

| Situation | Action |
|---|---|
| Router default fires on domain query | log it; weekly review tunes regexes |
| P3 quota exhausted | drop to P1-merged with a "degraded" flag |
| Modality store down | fusion ladder (W8): renormalize, degrade |
| Empty retrieval (all routes) | answer "not found" honestly, log query |

The ladder exists so the router never has to choose between crashing and
guessing — both are worse than a labeled degradation.

## 4. The capstone query plan

Your demo's query list (20–30 queries) should *cover* all routes: 5+ per
class, including one deliberate router-miss (domain query hitting default)
to show logging. The Week-10 agent inherits this table as its tool-routing
prior.

## 5. Router maintenance — the table rots, the loop keeps it honest

The routing table encodes *this corpus's* measured best patterns. Two
maintenance triggers:

| Trigger | Action |
|---|---|
| corpus class mix shifts >20% | re-run the pattern eval; re-derive gold |
| a route's R@10 drops below its class baseline | investigate before re-routing |
| new query class appears in logs ≥5× | add a row; measure before enabling |

```python
def route_with_log(query: str, log) -> str:
    r = route(query)
    log.info("route=%s q=%s", r, query[:80])     # every miss review starts here
    return r
```

The log line is the table's heartbeat: week-over-week miss reviews are how
regexes evolve into a tiny classifier, on evidence rather than vibes.

## Exercises

1. Build the gold map for your 25 queries from the pattern evals; compute
   router accuracy; iterate regexes until ≥0.85 *without* memorizing
   specific queries (test on held-out phrasings).
2. Quota drill: simulate 100 queries with a 10% P3 quota; verify the
   degradation path fires exactly on overflow and flags answers.
3. Miss-review: take 5 default-routed queries; was the regex fixable or is
   a small classifier (few-shot LLM route) the right upgrade? Write the
   recommendation.

## Pitfalls

- Regex routing trained on your own demo queries — held-out phrasings or it
  is memorization, not routing.
- Silent degradation — every fallback flags its answers; invisible
  degradation corrupts evals.
- One route for the whole corpus — the table exists because query classes
  have different best patterns; re-verify per corpus change.

## Resources

- Pattern files 02–04 (the measurements this table encodes).
- Your Week-10 agent design — the consumer of this routing prior.
