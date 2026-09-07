# Benchmark Tour — COCO, VQA, AudioCaps, MSR-VTT Mapped to Your Eval

**What you'll learn:** which official benchmark each task family uses, what
metric is *the* number on its leaderboard, and how to borrow each protocol
for your capstone corpus without downloading 18 GB.

## 1. The mapping table

| Benchmark | Task | Official metric | Split protocol | Borrow for |
|---|---|---|---|---|
| COCO Captions | image captioning | BLEU-4 / CIDEr / SPICE | Karpathy 5k test pool | caption eval shape, 5 refs |
| Flickr30k | image↔text retrieval | R@1/5/10 both directions | 1k test pool | retrieval protocol |
| VQA v2 | visual question answering | accuracy over 10 answers | val/test-standard | answer-style eval |
| AudioCaps | audio captioning | BLEU-4 / SPICE | fixed train/val/test | audio text sidecar eval |
| Clotho | audio captioning | F1 / BLEU variants | 5 captions/clip | multi-ref audio eval |
| MSR-VTT | video↔text retrieval | R@1/5/10 (t2v, v2t) | 1k test pool | video retrieval protocol |
| MSVD | video captioning | BLEU-4/ROUGE | standard split | video caption baselines |

The pattern to internalize: **captioning → n-gram + semantic metrics;
retrieval → R@K both directions; QA → answer accuracy.** Your capstone is a
retrieval system with a generation layer on top, so you owe the retrieval
protocol (row 2/6) and — once Week 12+ adds generated captions — the caption
protocol (row 1).

## 2. Borrowing the COCO protocol for your corpus

The parts of the COCO protocol worth copying (and their cheap versions):

| COCO protocol | Your version |
|---|---|
| 5 human captions per image | 1 human + 2 LLM-paraphrase captions (record which) |
| Karpathy 5k test pool | 200–500 held-out pairs, pool size recorded |
| CIDEr (tf-idf weighted n-grams) | BLEU-4 + CLIPScore (CIDEr needs bigger ref sets) |
| Both t2i and i2t | both, always (file 03) |

```python
def capstone_eval_header(n_pool: int, seed: int, n_refs: int) -> dict:
    return {"pool": n_pool, "seed": seed, "refs_per_unit": n_refs,
            "metrics": ["bleu4", "clipscore", "r@1", "r@5", "r@10", "medr"],
            "directions": ["t2i", "i2t"]}
```

The header is part of the report; numbers without it are not comparable to
anything, including your own next run.

## 3. What each benchmark *cannot* tell you about a RAG system

Every benchmark above evaluates a *pair* (image, caption). Your system
answers questions over a corpus — a different shape:

| RAG property | Benchmarks measure it? |
|---|---|
| Corpus-scale retrieval (10k+ units) | partially (COCO 5k pool) |
| Multi-hop (text→image→text) | no |
| Grounded generation (quote the source) | no |
| Temporal localization (video) | no (MSR-VTT is clip-level) |

So the capstone eval stack is: **borrowed benchmarks for the encoder layer**
(your CLIP embeddings vs COCO's leaderboard numbers sanity-check your
pipeline) **plus a custom RAG eval** (Weeks 11–12: answer faithfulness,
citation correctness). Do not let a good R@10 create false confidence in
end-to-end answers — those need their own harness.

## 4. Reproducing one official number as a pipeline test

The strongest correctness check available: reproduce a *known* number. Take
the official CLIP ViT-B/32 zero-shot image↔text retrieval R@1 on Flickr30k
(~88 i2t / ~68 t2i at 1k pool, per the paper's protocol):

```python
def pipeline_sanity_against_known(n: int = 1000):
    """Your stack, small pool: within ±0.03 of the paper's protocol means
    your encode/pool/eval path is correct end-to-end."""
    ranks = fixed_pool_eval(Q_txt, C_img, gt, pool=n, seed=42)
    r1 = recall_at_k(ranks, 1)
    assert abs(r1 - EXPECTED_R1) < 0.03, f"{r1:.3f} vs {EXPECTED_R1}"
```

If the small-scale reproduction is off, the bug is in *your* pipeline
(pool construction, normalization, projection choice) — found in minutes,
not at demo time.

## 5. The borrow-don't-download workflow

1. Pick the benchmark whose *protocol* you need (retrieval → Flickr30k/MSR-VTT shape).
2. Load 200–500 pairs via streaming (datasets subfolder, file 01) into your manifest schema.
3. Run the official metric implementations (files 01–03) on the subset.
4. Report with the header (pool, seed, refs) — subset results are for
   *regression tracking*, never for leaderboard claims.

This keeps the official protocol's discipline (fixed pools, both directions,
multi-reference) at 1% of the storage.

## Exercises

1. Fill the mapping table's "Borrow for" column for your capstone's three
   modalities; one sentence each naming the protocol piece you copy.
2. Reproduce the §4 sanity check at pool=200 with a lower assert tolerance —
   document the smallest pool where the ±0.03 bound still holds for your stack.
3. Write the "what this eval does NOT measure" paragraph for your eval report
   using §3's table (three bullet points minimum).

## Pitfalls

- Comparing subset R@K to paper R@K — different pools; only *protocol* transfers, not numbers.
- Borrowing VQA accuracy for caption eval — different task shape entirely.
- Treating MSR-VTT clip-level R@K as "video understanding" — temporal localization is a different, unmeasured skill.

## Resources

- Karpathy & Fei-Fei 2015 (COCO/Flickr splits); VQA v2 evaluation docs.
- AudioCaps/Clotho papers (metric conventions); MSR-VTT retrieval protocol.
