# Realtime vs Cascade — Decision and Costs

**What you'll learn:** the architectural fork: a realtime speech-to-
speech model vs your cascade stack. The decision is latency + cost +
control, and your corpus-bound capstone usually lands on cascade — with
numbers to say why.

## 1. The two architectures

| Property | Cascade (yours) | Realtime (speech-to-speech) |
|---|---|---|
| Stages | 3 (STT, agent, TTS) | 1 (speech in → speech out) |
| Perceived latency | 2–6 s | 0.5–1.5 s |
| Agent logic | *your* W10 agent, tools, budget | the realtime model's behavior |
| Grounding (RAG) | native (tools) | limited/function-call bridges |
| Cost driver | per-stage tokens + TTS chars | per-minute audio tokens |
| Observability | full (spans, traces, text) | audio in/out, opaque middle |

Realtime models are genuinely magical for *conversation*; cascade is
genuinely superior for *grounded answers over your corpus*. The decision
is which product you are building.

## 2. The cost comparison, computed

| Factor | Cascade | Realtime |
|---|---|---|
| STT | ~$0.006/min (or local, free) | — |
| agent (text) | your ledger (W9-04) | — |
| TTS | ~$15/1M chars | — |
| realtime session | — | ~$0.06–0.32/min (model-dependent) |
| per 10-min grounded session | ~$0.06 + agent cost | ~$0.60–3.20, grounding extra |

```python
def session_cost(minutes: float, mode: str, agent_cost_per_min: float) -> float:
    if mode == "cascade":
        return minutes * (0.006 + agent_cost_per_min + 0.02)   # stt+agent+tts
    return minutes * 0.20                                       # realtime, ballpark
```

The grounding overhead is the hidden line: realtime models ground via
function calls *back into your stack* — meaning you build the tool
bridge anyway, inside a cost model you control less. For a corpus-RAG
capstone, that is cascade's whole argument.

## 3. The decision procedure

1. **Does the product need sub-second turn-taking?** No → cascade.
2. **Is grounding over your corpus the core task?** Yes → cascade (tools
   are native).
3. **Is the conversation open-domain and emotional?** Yes → realtime
   earns its cost.
4. **Is the budget per-session or per-answer?** Per-answer → cascade.

Your capstone: corpus-grounded QA → **cascade**, with push-to-talk as
the demo and full-duplex as future work. The decision memo records it
with the §2 numbers, revisit-triggered (as always) by a product change.

## 4. Hybrid: cascade now, realtime later (the seam)

The seam between them is the *agent* — realtime models that call your
tools replace the STT+agent front half, keeping your tool surface:

```text
cascade:      mic → VAD → STT → [your agent] → TTS → speaker
realtime:     mic → [realtime model ⇄ function calls to your tools] → speaker
                       (your tools, hosted bridge)
```

The MCP tool surface (W10 file 03) is exactly what survives the swap —
which is the quiet argument for having built it.

## Exercises

1. Fill the §2 cost table with *your* ledger's agent cost per minute; run
   the decision procedure; write the verdict into the boundary memo.
2. Latency audit: measure your cascade's total on 10 queries; plot
   against the realtime ballpark (0.5–1.5 s) — the gap is your roadmap
   (streaming STT, sentence-TTS) or your reason to stop.
3. Seam drill: sketch the realtime variant of your architecture — which
   components survive unchanged (tools, sessions, evals) and which
   vanish (fitter, guardrails-as-code)? The inventory is the migration
   cost, written down.

## Pitfalls

- Comparing list-price realtime against *your measured* cascade — use
  your ledger on both sides or the comparison is fiction.
- Choosing realtime "because it sounds better in the demo" — grounded
  answers are the capstone's product; conversation quality is the
  garnish here.
- Forgetting that realtime grounding still costs you the tool bridge —
  the §2 hidden line is the decision-maker.

## Resources

- OpenAI Realtime API pricing/concepts; your W9-04 cost ledger.
- [`../01-cascade-stack.md`](../01-cascade-stack.md) and
  [`../02-turn-taking.md`](../02-turn-taking.md) — the stack being
  compared.