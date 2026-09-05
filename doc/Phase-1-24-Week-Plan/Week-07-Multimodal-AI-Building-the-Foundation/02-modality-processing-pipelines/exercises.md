# Exercises — Modality Processing Pipelines

Expanded set with worked approaches. Run from the repo root with the project
`.venv` active (`py`, PowerShell). Use corpus files under `data/raw/`.

## 1. Processor parity suite (from 01-image-pipeline)

**Task:** turn `parity_check` into `tests/test_parity.py` covering five
images: one landscape, one portrait, one PNG with alpha, one screenshot, one
grayscale. All five must pass max-abs-diff < 1e-4.

**Worked approach:** the alpha and grayscale cases are where parity breaks —
alpha needs `flatten_rgb` before the processor, grayscale needs `.convert("RGB")`
(channels × 3). If portrait fails while landscape passes, your resize path
differs from the processor's `do_resize` + `do_center_crop` order; read the
`preprocessor_config.json` and mirror it exactly.

**Pass criterion:** `pytest tests/test_parity.py` green, and the test *fails*
if you flip CLIP's mean/std to ImageNet's (a mutation test proving the test
works).

## 2. Audio contract drill (from 02-audio-pipeline)

**Task:** write `tests/test_audio_contract.py`: for each audio file, decode →
mono → 16 kHz → processor, and assert `input_features.shape == (1, 80, 3000)`
for every 30 s window, plus `dtype == torch.float32`.

**Worked approach:**

```python
def windows_of(x, sr=16_000, win_s=30.0):
    n = int(win_s * sr)
    for i in range(0, len(x) - n + 1, n):     # hard windows; last partial dropped
        yield x[i:i + n]
```

The assertion fails most often at the *resample* step (length off by 1–2
samples). Fix with `resample_poly` and explicit `[:n]` slicing, not by
padding blind.

**Pass criterion:** every file in `data/raw/audio/` produces all-3000 windows
or is listed in a quarantine report with the reason.

## 3. Sampling bake-off (from 03-video-pipeline)

**Task:** on one ≤10 min video, run uniform-12, keyframes, and scene-detect.
For each: wall time, frames written, and *distinct-slide count* (label slides
by hand for the video once, then compare).

**Worked approach:** time with `time.perf_counter()` around the sampling
function only (not model encode). Distinct-slide count = number of unique
hand labels covered by the sample. Expected outcome: keyframes win on
slide-decks (I-frames at transitions), uniform-12 misses short slides,
scene-detect is most complete and 100× slower. Record results in
`reports/sampling-bakeoff.md` — this table justifies your capstone choice.

## 4. Determinism gauntlet (from 04-preprocessing-determinism)

**Task:** run `assert_deterministic` for image, audio, and video pipelines;
then introduce each bug below and confirm the gauntlet catches it:
(a) unseeded numpy noise aug, (b) unsorted merge in a 4-worker encode,
(c) changed resize filter.

**Worked approach:** (a) fails immediately with `array_equal` mismatch;
(b) fails only when worker completion order differs — run it several times;
(c) fails the *parity* test, not the determinism test (the pipeline is
deterministically wrong) — this distinction is the lesson: the two tests
complement, neither subsumes the other.

## 5. Capstone: settings file + gauntlet in CI (from 04-preprocessing-determinism)

**Task:** commit `data/manifests/preproc-settings.json` (version 3) and a
`tests/test_determinism.py` that reads it and runs the gauntlet on 5 units
per modality. Wire it so a settings bump without a re-run visibly fails.

**Worked approach:** the test embeds `SETTINGS["version"]` in the cache key
assertion: `unit_key(rel_path, settings)` must equal the key recorded in the
manifest for every sampled unit. A bumped-but-not-reprocessed corpus then
fails loudly with "cache key mismatch: reprocess or revert settings".

**Pass criterion:** bumping `version` to 4 in the JSON makes the test suite
red; running the reprocess script makes it green; reverting to 3 also green
(proving the check is version-aware, not just "recently touched").

## Pitfalls recap

- Tests that pass on toy data but not on your corpus — always point the suite at real `data/raw/` files, committed sizes permitting.
- Timing measurements polluted by first-call JIT/IO warm-up — discard the first run.
- Bake-off judged by "looks good" — only the hand-labeled slide count is a metric.
