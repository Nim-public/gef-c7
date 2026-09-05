# Pattern 3 — VLM Generation: Economics and Grounding

**What you'll learn:** the expensive pattern: a vision-language model reads
retrieved *pixels* and writes grounded answers. What it buys (real visual
grounding, citations by image), what it costs (tokens, latency, failure
surface), and the budget math that decides if you can afford it.

## 1. The pattern's shape

```text
query → retrieve images (P1/P2 hybrid) → top-N images
      → VLM(prompt = question + N images + retrieved text)
      → answer with per-image citations
```

Two entry points matter: **generation grounding** (answer *about* the
image's pixels — chart shapes, layouts, text in screenshots) and **answer
citations** (every claim points to a retrieved unit).

## 2. The token economics, computed

| Item | Tokens (LLaVA-1.5 class) | At 4k ctx |
|---|---|---|
| 1 image | 576 | ~7 images max |
| Your text context (snippets) | ~300–800 | — |
| Question + instructions | ~100 | — |
| Answer | ~150–400 | — |

Budget rule: **2 images + 6 snippets + 400-answer tokens** fits an 8k
context with margin; 4 images fit only with aggressive snippet truncation.
The Week-08 projection-pattern token math, applied to a real prompt.

## 3. Latency and cost, measured

| Setup | Latency/answer | Cost/1k answers |
|---|---|---|
| 7B VLM, local GPU | 2–6 s | electricity |
| 7B VLM, CPU | 60–300 s | demo-infeasible |
| Hosted VLM API | 1–3 s | $ per 1k (pricing table) |

The capstone implication (CPU reality): P3 is a *demo garnish* — one
prepared question answered live, with the answer pre-verified — not the
default path. Your P1+P2 hybrid answers 95% of queries; P3 handles the
"what exactly does the chart show" class.

## 4. Grounding quality: the eval that matters

P3's claims need *verification*, not vibes:

| Check | Method |
|---|---|
| Citation validity | cited unit exists and is top-5 retrieved |
| Visual claim | VLM-verify or human spot-check (10%) |
| Faithfulness | answer sentences trace to context (W5 harness) |

```python
def citation_audit(answer_units: list[str], retrieved: list[str]) -> bool:
    return all(u in retrieved for u in answer_units)
```

Cheap, automatable, and catches the most common P3 failure: citing
plausible-but-unretrieved units.

## Exercises

1. Build the token-budget table for *your* context: images + snippets +
   answer; write the max-images number into the tool contract.
2. Run one P3 answer end-to-end on a chart query; audit citations and
   hand-verify the visual claim; log both results.
3. Cost model: at your demo's expected query rate, compute P3's daily cost
   local vs hosted; the memo records the chosen P3 quota (e.g., "≤10%
   of queries").

## Pitfalls

- P3 as default path — token cost and latency compound; quota it.
- Un-audited citations — the audit is one function; run it always.
- Describing images in the prompt *and* attaching them — double token cost;
  attach pixels, keep text instructions tight.

## Resources

- Week-08 fusion file 04 (LLaVA projection, token math); Week-05 faithfulness harness.
- Your hybrid retriever — P3's upstream.
