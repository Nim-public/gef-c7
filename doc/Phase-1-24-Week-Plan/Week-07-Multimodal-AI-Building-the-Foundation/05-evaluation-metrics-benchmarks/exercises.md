# Exercises — Evaluation Metrics & Benchmarks

Expanded set with worked approaches. Use the mini-benchmark parquet from the
datasets subfolder (200–500 held-out pairs) as the eval set throughout.

## 1. BLEU vs NLTK cross-check (from 01-bleu-by-hand)

**Task:** your `sentence_bleu` must agree with `nltk.translate.bleu_score`
(needle: `SmoothingFunction().method0`, identical tokenization) on 50 pairs
to within 1e-6, or you must document the exact convention difference.

**Worked approach:**

```python
from nltk.translate.bleu_score import sentence_bleu as nltk_bleu

for cand, refs in zip(cands, refs_list):
    mine = sentence_bleu(cand, refs)
    theirs = nltk_bleu(refs, cand)          # same tokenizer in both!
    assert abs(mine - theirs) < 1e-6, (mine, theirs)
```

Differences, when they appear, are always one of: tokenization (nltk's
default vs your `.split()`), multi-reference r_eff (closest vs shortest),
or smoothing. Name yours in a comment — the point is *knowing* the metric.

**Pass criterion:** 50/50 agreement, or a written paragraph naming the
divergence and why NLTK's convention is the one reported.

## 2. CLIPScore bands audit (from 02-clipscore)

**Task:** on 30 held-out pairs, compute CLIPScore for (a) ground-truth
captions, (b) shuffled captions (wrong image), (c) noun-echo captions built
from image top-predicted classes. Report the three means and verify they land
in the bands: (a) ≈2.2–2.4, (b) <1.5, (c) >2.5.

**Worked approach:** shuffling is the negative control — if shuffled
captions do not crater below 1.5, your embedding space or pairing is wrong
(usually `image_features` vs `image_embeds`, or unnormalized cosine).

**Pass criterion:** three disjoint bands on your 30 pairs; if (b) and (a)
overlap, stop and fix before any metric is reported anywhere.

## 3. Both-directions retrieval report (from 03-retrieval-metrics)

**Task:** produce the two-row R@K table (t2i, i2t) at pool=200, seed=42 on
your mini-benchmark, with the report header (pool/seed/corpus hash). Then
rerun at pool=50 and record the inflation.

**Worked approach:** normalize both matrices (the classic silent bug is
normalizing only one side); verify the §2 sanity set first (synthetic
perfect-match → R@1=1.0). The pool=50 rerun exists to *teach the trap*:
record both tables in `reports/retrieval-eval.md` with a one-line caveat
that only the fixed-pool protocol is comparable across runs.

## 4. Official-number reproduction (from 04-benchmark-tour)

**Task:** reproduce CLIP ViT-B/32's zero-shot t2i R@1 on a 1k Flickr30k-style
pool within ±0.03 of the published protocol value; write the reproduction
note (library versions, pool, seed) into `reports/repro-flickr30k.md`.

**Worked approach:** use precomputed CLIP embeddings if available for the
subset (encode with the *same* processor settings from your parity-tested
pipeline); the reproduction validates the *eval harness*, not the model. If
off by >0.03, suspect: pool construction (distractor sampling), norm order,
and the projections (§2 of file 02).

**Pass criterion:** the note contains the number, the pool/seed, and the
delta — reproducible by a teammate with one command.

## 5. Capstone: the eval harness skeleton (from all files)

**Task:** assemble `scripts/eval_retrieval.py`: load held-out pairs → encode
via the parity-tested pipeline → both-direction ranks → the four-metric
report → header with pool/seed/version → gate that fails CI if R@1 drops
>0.05 vs the committed baseline JSON.

**Worked approach:** the baseline JSON (`tests/fixtures/retrieval-baseline.json`)
stores the last accepted metrics; the harness compares and exits nonzero on
regression. Regression gates convert this week's metrics from homework into
a safety net for every later week's refactors.

**Pass criterion:** deliberately degrade the index (encode with unnormalized
vectors), watch the gate fail with a readable diff, restore, watch it pass.

## Pitfalls recap

- Comparing metric runs with different reference counts (5 refs vs 1) — BLEU-4 rises with reference count; hold refs constant per comparison.
- CLIPScore computed on `get_image_features` but paired with `text_embeds` — plausible garbage; the §2 assert catches it in seconds.
- Baseline JSON updated by hand after a regression — baselines change only via accepted runs, never to make CI green.
