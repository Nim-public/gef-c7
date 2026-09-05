# Seed Expansion — Paraphrase and Variation Generation

**What you'll learn:** multiply hand-written seeds into diverse training
and eval cases: paraphrase generation with variation controls, the
diversity budget per seed, and the dedup that keeps expansion from
collapsing into echoes.

## 1. The expansion prompt

```python
EXPANSION_PROMPT = """Rewrite the question below in {n} different ways.
Vary: phrasing, politeness, length, typos (1 max), and specificity.
Keep: the exact information need.
Do NOT: change what is being asked.

Original: {seed}"""
```

| Variation axis | Example |
|---|---|
| phrasing | "How do I…" → "What's the way to…" |
| politeness | "Give me…" → "Could you please…" |
| length | terse ↔ verbose |
| typos | one realistic slip |
| specificity | "the margin" ↔ "the gross margin in Q3" |

The variation axes are the expansion's contract — the prompt names
them, and the validation (file 04) checks the *spread* across axes, not
just the count.

## 2. The diversity budget per seed

| Budget | Rule |
|---|---|
| 5–10 variants per seed | beyond that, echoes appear |
| ≥3 axes varied per variant | single-axis variants are near-duplicates |
| 1 seed → ≤1 eval case | the rest go to training/robustness data |

```python
def expand_seed(seed: str, n: int = 8) -> list[str]:
    variants = llm_json(EXPANSION_PROMPT.format(n=n, seed=seed))
    deduped = dedupe_by_similarity(variants, thresh=0.85)
    return deduped[:n]
```

The dedup threshold (cosine or edit distance) is the expansion's
quality gate — variants above 0.85 similarity are echoes. The diversity
check (file 04) measures the spread; the dedup keeps it honest.

## 3. The seed selection (what deserves expansion)

| Seed quality | Expand? |
|---|---|
| a real user query from the logs | yes — highest value |
| a failure-class case (the mined clusters) | yes — robustness data |
| an invented query that "seems likely" | only if the persona grid needs it (file 02) |

The seed's provenance matters: logs and failure clusters are real
demand; invented seeds are hypotheses. The expansion multiplies what
exists — it does not manufacture demand.

## Exercises

1. Expand 10 seeds (5 log-derived, 5 failure-cluster) with the
   variation axes; measure the axis spread per variant.
2. Dedup drill: raise the similarity threshold to 0.95; count the
   echoes that pass; set the threshold where echoes die and variety
   survives.
3. Provenance drill: tag every variant with its seed's source; the
   eval set only admits log/failure-derived expansions.