# Exercises — CLIP & BLIP Architectures

Expanded set with worked approaches. Reuse the mini-benchmark pairs and the
Week-07 eval harness throughout.

## 1. CLIP loss from scratch, verified (from 01-clip-loss)

**Task:** implement `clip_loss` twice — matrix loops and vectorized `F.cross_entropy`
— and prove they agree to 1e-6 on random embeddings; then hand-compute the
N=3 case from file 01's §1 and match.

**Worked approach:** the loop version makes the two softmaxes explicit;
the vectorized one is what you keep. Assert agreement:

```python
assert torch.allclose(clip_loss_loop(i, t), clip_loss(i, t), atol=1e-6)
```

**Pass criterion:** three-way agreement (loop, vectorized, hand) on the same
matrix; any mismatch is a normalization or target-ordering bug.

## 2. Zero-shot temperature sweep (from 02-zero-shot-classification)

**Task:** on 20 labeled images, run zero-shot with logit scaling {1, 10, 100};
report accuracy (unchanged — argmax is scale-invariant for a fixed image!)
and probability spread. Then add one confusable class and show where the
scale matters.

**Worked approach:** argmax is invariant, so accuracy columns will be
identical — the *distributions* differ (entropy drops with scale). The
teaching point: temperature changes confidence, not ranking; report both.

**Pass criterion:** entropy table across the three scales + one sentence on
when confidence (vs ranking) matters in a product.

## 3. Retrieve-then-rerank with ITM (from 03-blip-objectives)

**Task:** for 10 queries: retrieve top-10 with CLIP cosine, rerank with a
pair-scoring head (BLIP ITM or your wired scorer); report R@1 both ways.

**Worked approach:** hold the retrieval stage fixed; the only variable is
the reranker. Log per-query ranks before/after — the aggregate hides where
reranking *hurts* (hard negatives that are actually positives; a known ITM
failure when captions are formulaic).

**Pass criterion:** two R@1 numbers + the per-query table; annotate at
least one query where reranking changed the winner.

## 4. Decision-guide rehearsal (from 04-decision-guide)

**Task:** pick five queries from your capstone's demo list; for each, apply
§4's three questions and write the routed tool + expected latency; then
estimate the whole demo's compute budget per query.

**Worked approach:** the routing table *is* the deliverable — one row per
query with (tool, why, ms). The budget line is the sum; if a VLM appears
more than once, your demo plan needs GPU or fewer VLM calls.

**Pass criterion:** five routed queries + a total-budget line; the table is
committed to `doc/capstone/query-routing.md`.

## 5. Capstone: the model card (from all files)

**Task:** write a one-page model card for your capstone's chosen stack
(CLIP variant, reranker, captioner): embedding dims, preproc settings,
known failure modes (from your own exercises), and the upgrade triggers.

**Worked approach:** pull every number from your own runs (dims from the
Protocol tests, failures from the off-diagonal cells and rerank tables).
The card's "not good at" section is the most valuable — it is what you will
re-read at 2 a.m. before the demo.

**Pass criterion:** the card cites run artifacts (reports/*.md) for every
claim; zero vibes-based sentences.

## Pitfalls recap

- Rerank evals that retrain the retriever mid-experiment — one variable per experiment, or the delta is unattributable.
- Zero-shot class lists that grow mid-eval — the class list is part of the model; freeze it before the sweep.
- Model cards written from paper tables instead of your runs — the capstone's whole point is *your* corpus's numbers.
