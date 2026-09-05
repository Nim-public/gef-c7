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

## 5. The seed-to-purpose mapping (what each expansion is for)

| Destination | Which variants | Format |
|---|---|---|
| eval set (held-out) | 1 per seed, untouched phrasing | the gold-labeled case |
| robustness data | paraphrases with typos/length shifts | training pairs |
| red-team probes | the adversarial axis variants | the battery |
| few-shot pool | the clearest variants | the prompt's examples |

The mapping is the expansion's allocation plan — one seed's variants
split across purposes, so the eval set stays honest (only the untouched
phrasing) while the training data gets the variety. The W10 memory-tier
rule applies: different destinations, different content.

## 6. The expansion ledger (the seeds' record)

| Seed | Source | Variants | Axes covered | Destinations |
|---|---|---|---|---|
| q-log-041 | live logs | 7 | phrasing, politeness, typos | eval 1, robustness 6 |
| q-fail-017 | failure cluster | 6 | phrasing, specificity | robustness 6 |
| q-invented-002 | persona grid | 5 | all | training only |

The ledger is the expansion's provenance — every seed's source, output,
and destination. It is the W14-04 self-improving loop's input (the
log-derived seeds) and the persona grid's output (the invented ones) —
the two data families meeting in one table.

## Exercises

1. Expand 10 seeds (5 log-derived, 5 failure-cluster) with the
   variation axes; measure the axis spread per variant.
2. Dedup drill: raise the similarity threshold to 0.95; count the
   echoes that pass; set the threshold where echoes die and variety
   survives.
3. Provenance drill: tag every variant with its seed's source; the
   eval set only admits log/failure-derived expansions.
4. Mapping drill: allocate one seed's variants across the four
   destinations; the eval variant is the untouched one — the rule,
   demonstrated.