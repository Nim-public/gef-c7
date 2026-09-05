# Exercises — Modality Fusion

Expanded set with worked approaches. All experiments run on synthetic or
small real data; nothing needs a GPU.

## 1. The baseline that must be beaten (from 01-early-fusion)

**Task:** build the concat classifier on 200 synthetic pairs (text 64-d,
image 128-d, 4 classes, informative only in *one* modality for half the
pairs); report the 4-cell ablation table.

**Worked approach:** the informative-modality split is the interesting
design: for pairs where only text is informative, text-only accuracy ≈ full
accuracy, and image-only ≈ chance. If your full-model accuracy *drops*
below text-only, the fusion pathway is absorbing noise — the dead-fusion
signature from file 01's §2.

**Pass criterion:** table with full ≥ max(text-only, image-only) on
informative pairs; the dead-path drill (shuffled features) reproduces
full ≈ text-only.

## 2. Cross-attention mechanics proof (from 02-intermediate-fusion)

**Task:** with identity projections, construct Q (3 text tokens) and K/V
(4 patches) such that you can *predict* the attention map before running:
token 0 near patch 1, token 1 near patch 3, token 2 diffuse. Verify.

**Worked approach:** place Q rows near K rows in d-space (e.g., Q[0] = K[1]
+ noise); `A[0]` should peak at column 1. The diffuse token: equal distance
to all K — verify near-uniform row. This is the last time you can *see*
attention mechanics without trained weights; write the map down.

**Pass criterion:** predicted map matches computed map on argmax per row.

## 3. Calibration before fusion (from 03-late-fusion)

**Task:** three synthetic heads with true accuracies 0.8/0.7/0.6 but
reported confidences 0.95/0.7/0.4; fit per-head temperatures; then compare
late-fusion accuracy with raw vs calibrated scores.

**Worked approach:** fit T by minimizing NLL on held-out logits (1-D grid
search over [0.5, 3.0] is enough for a demo). The expected result: weighted
fusion with calibrated heads beats raw by 2–5 points — the number that
makes calibration non-optional.

**Pass criterion:** ECE < 0.03 per head after scaling; fusion delta
reported.

## 4. LLaVA sequence assembly (from 04-llava-projection)

**Task:** implement `llava_inject` with a proper tokenizer stub: text ids →
embedding rows; assert the output sequence length and that vision precedes
text; then compute the "context cost" of 3 images + 500 text tokens.

**Worked approach:** 3×576 + 500 = 2228 tokens. Add the *positional* caveat
to your notes: many LLMs use RoPE with sequence position — vision tokens
occupy positions 0–575, so text tokens attend *backwards* to the image; that
is the mechanism, not a detail.

**Pass criterion:** assertion suite green; the token-budget number appears
in your capstone planning notes.

## 5. Capstone: the fusion decision (from all files)

**Task:** extend the encoder decision memo with the fusion architecture:
early/late/cross/projection, with the missing-modality policy written as a
table row (what happens in the demo when ASR is absent? when OCR fails?).

**Worked approach:** the honest pick for a RAG capstone is late fusion
(rank fusion over modality indexes) with the LLM consuming a *combined
context* — §3's degradation matrix is the justification template. Name the
VLM route (LLaVA-style) as the Week-13+ upgrade path, not the week-8 build.

**Pass criterion:** the memo's fusion row cites exercises 1–4's numbers;
the degradation table names the failing component and the user-visible
behavior for each.

## Pitfalls recap

- Synthetic experiments where *both* modalities are informative — ablation deltas vanish and the exercise teaches nothing; make one modality uninformative by design.
- Attention-map reading on identity projections extrapolated to trained models — identity makes maps interpretable *because* there is no learned mixing; say so in the notes.
- Fusion experiments without a fixed seed — ablation deltas of 1–2 points are noise at these data sizes; report seeds alongside tables.
