# Metrics Demo — BLEU + CLIPScore on Real Pairs

**What you'll learn:** Part C as a build guide: a demo that runs both
metrics from the evaluation subfolder on your held-out pairs, renders the
results *next to the media*, and teaches you to distrust single numbers.

## 1. The demo's actual job

The metrics mini-run is not about the numbers — it is about *pairing each
number with the artifact it judged*, so that "BLEU 0.31, CLIPScore 2.4"
becomes a picture you remember instead of a statistic you repeat. Gradio
makes the pairing trivial; the metric code comes from
[`../05-evaluation-metrics-benchmarks/`](../05-evaluation-metrics-benchmarks/).

```python
# scripts/metrics_demo.py
import pandas as pd, gradio as gr
from eval_metrics import sentence_bleu, clipscore   # your implementations

def score_pair(image_path: str, caption: str, refs: list[str]) -> dict:
    return {
        "bleu4": round(sentence_bleu(caption.split(), [r.split() for r in refs]), 4),
        "clipscore": round(clipscore(image_path, caption), 3),
    }
```

## 2. The batch run and its display

```python
def run_all(pairs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for r in pairs.itertuples():
        s = score_pair(r.image_path, r.caption, r.refs)
        rows.append({"unit_id": r.unit_id, **s})
    out = pd.DataFrame(rows)
    out.to_parquet("reports/metrics-mini-run.parquet")
    return out

def render(row) -> tuple:
    return (row.image_path, row.caption, row.bleu4, row.clipscore)

with gr.Blocks() as app:
    gallery = gr.Gallery(label="worst 6 by CLIPScore")   # the interesting tail
    table = gr.DataFrame(label="all scores")
    btn = gr.Button("Score held-out pairs")
    btn.click(lambda: [run_all(PAIRS)], None, [table])
```

The **worst-6 gallery** is the feature that matters: sorting by *lowest*
CLIPScore shows you the pairs where the caption and the image disagree —
usually revealing either a bad caption or a wrong pairing. High scores teach
nothing; the tail teaches everything.

## 3. Reading the two metrics against each other

| BLEU | CLIPScore | Diagnosis |
|---|---|---|
| high | high | healthy pair — the boring majority |
| high | low | copied reference n-grams, wrong image (pairing bug or hallucination) |
| low | high | paraphrase/lexical mismatch — semantically fine |
| low | low | genuinely bad caption — the interesting failures |

Any pair in the off-diagonal cells gets a manual look. Ten minutes here is
the cheapest model-behavior lesson in the entire program.

## 4. Acceptance criteria (Part C done when…)

1. `py scripts/metrics_demo.py` runs on all held-out pairs in < 2 min (CPU ok).
2. The parquet has one row per pair with both metrics; no NaNs (a NaN means
   an unhandled empty-caption case — fix the metric, not the data).
3. The Gradio app shows the worst-6 gallery and the full table.
4. You have *written down* three diagnoses from the off-diagonal cells in
   `reports/metrics-notes.md` — the rubric grades the notes, not the parquet.

## Exercises

1. Add the shuffled-caption negative control (CLIPScore bands exercise) as
   a self-test that runs at app startup and refuses to launch on failure.
2. Compute both metrics for the *same* caption against 5 references vs 1
   reference; add a "refs" column so future-you never compares across ref counts.
3. Wire the demo to your explorer: clicking a unit in the explorer shows its
   score row and its position in the worst-6 ranking (cross-app link by
   `unit_id`).

## Pitfalls

- Tokenizing once for BLEU and differently for CLIPScore's text — irrelevant for CLIP, fatal for BLEU; one tokenizer everywhere.
- Reporting corpus means only — the tail (worst 6) is where pairings break; the mean hides them by construction.
- Demo app that re-encodes every image per score call — encode once at startup or cache by `(image_hash, model)`; the parity-tested pipeline already gives you cache keys.

## Resources

- Your metric implementations: [`../05-evaluation-metrics-benchmarks/01-bleu-by-hand.md`](../05-evaluation-metrics-benchmarks/01-bleu-by-hand.md),
  [`../05-evaluation-metrics-benchmarks/02-clipscore.md`](../05-evaluation-metrics-benchmarks/02-clipscore.md).
- Gradio `gr.Gallery` docs for the tail view.
