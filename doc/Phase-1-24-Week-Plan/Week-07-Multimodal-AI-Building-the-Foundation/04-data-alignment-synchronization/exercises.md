# Exercises — Data Alignment & Synchronization

Expanded set with worked approaches. Run from the repo root; all artifacts
land under `data/manifests/` and `reports/` (gitignored data, committed code).

## 1. One-clock drill (from 01-temporal-alignment)

**Task:** for one video in `data/raw/video/`, produce the four offset rows
(frames, audio, ASR placeholder, subtitles) and print the coverage table
(artifact → % of duration covered by `window(clock_t, half=2)` over a 20-point
probe).

**Worked approach:**

```python
probe_points = [d * 0.05 for d in range(20)]          # 5%, 10%, ... of duration
coverage = {
    art: sum(bool(len(window(align, uid, art, t))) for t in probe_points) / 20
    for art in ["frames", "subtitles", "audio"]
}
```

**Pass criterion:** frames/audio cover ~100% (sampling spans duration);
subtitles cover only their spans (report the real number); any artifact at
0% means its offset row is wrong — fix before continuing.

## 2. Check catalog in CI (from 02-cross-modal-validation)

**Task:** `tests/test_validation.py` runs `validate()` over a 10-row fixture
manifest with four *injected* defects (missing file, hash mismatch, wrong
frame count, license not in allow-list) and asserts each produces the right
check + severity row.

**Worked approach:** build the fixture manifest programmatically (tmp_path
for files), inject one defect per row, and assert on the report DataFrame —
including the negative case (a clean row produces *no* rows in the report).
The negative assertion is what prevents the validator from becoming a
noise generator.

**Pass criterion:** green test, then wire `py scripts/align_corpus.py --check-only`
into CI; inject a live defect (touch a file) and watch CI go red.

## 3. Policy table enforcement (from 03-missing-data-policies)

**Task:** given a manifest with 12 units — 2 unknown-license, 3 missing
timestamps, 1 undecodable image — produce the three views: local (all
decodable), published (strict), and quarantine report. Assert counts: local
11, published 8, quarantine 3.

**Worked approach:** `apply_policies` for drops, `published_view` for the
strict view, and `impute_captured_at` *before* computing the local view
(imputation happens before flag-based views so receipts exist). The
undecodable image lands in quarantine at *ingest* (stage 1), not policy
time — policies govern units that exist.

## 4. Version-stamp integrity (from 04-alignment-pipeline)

**Task:** test that all three version stamps agree with the artifacts on
disk: manifest filename version == `manifest_version` header; embeddings
path contains `settings["version"]`; alignment file contains `align_ver`.
Then bump settings version and assert the *old* matrix is still found (by
path) while the *new* path does not exist yet.

**Worked approach:**

```python
def test_versions_on_disk():
    paths = aligned_paths(manifest_ver=3, settings_ver=3, align_ver=2)
    assert Path(paths["manifest"]).exists()
    assert f"set-v{SETTINGS['version']}" in paths["embeddings"]
```

**Pass criterion:** the test suite fails if someone renames an artifact
without bumping its stamp — proven by a rename drill in the test comments.

## 5. Capstone: the demo that survives 2 a.m. (from all files)

**Task:** your capstone README gains an "Alignment guarantees" section: the
three report paths, the gate command, and one sentence per artifact clock
stating its reference and offset source. A teammate must be able to answer
"why does this frame not match this quote?" from the reports alone.

**Worked approach:** generate the section from the alignment parquet (do not
hand-write offsets into prose — they rot). One command
(`py scripts/align_corpus.py --emit-readme-section`) appends the generated
markdown; review it like code.

**Pass criterion:** re-running the emit after a data change updates only the
numbers, not the structure — and `git diff` of the README proves it.

## Pitfalls recap

- Coverage probes at 20 fixed points miss short subtitle spans — probe at subtitle boundaries too for the coverage metric to mean anything.
- Validator asserting inside the function — pure functions + caller-owned severity, or the CI gate becomes untestable.
- Version stamps incremented "for cleanliness" without artifact changes — now no one trusts stamps; bump only when outputs change.
