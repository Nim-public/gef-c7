# The Alignment Pipeline — Manifests, Versioning, Reports

**What you'll learn:** assemble files 01–03 into one pipeline: inputs, joins,
versioning discipline, and the three report artifacts it emits on every run.

## 1. Pipeline shape (one command, four stages)

```text
py scripts/align_corpus.py
  ├─ stage 1 ingest:   raw scan → manifest rows (hashes, EXIF, container meta)
  ├─ stage 2 align:    offset records per artifact (file 01)
  ├─ stage 3 validate: check catalog V1–V8 (file 02) + policies (file 03)
  └─ stage 4 report:   three artifacts under reports/
```

```python
# scripts/align_corpus.py — the orchestrator
from pathlib import Path
import pandas as pd

def run(data_root: str = "data", out: str = "reports") -> int:
    manifest = build_manifest(Path(data_root) / "raw")          # stage 1
    align = build_alignment(manifest, Path(data_root) / "raw")  # stage 2
    report = validate(manifest, None,
                      Path(data_root) / "processed/video-keyframes",
                      load_settings())                          # stage 3
    report = apply_policies_to_report(report, load_policies())
    write_reports(report, manifest, align, Path(out))           # stage 4
    return gate(report)                                         # CI exit code
```

Each stage is importable and testable alone; the orchestrator owns no logic.
This is the same shape as `build_manifest.py` from the landscape subfolder —
the alignment pipeline *extends* it rather than replacing it.

## 2. The joins (where alignment actually lives)

```python
def build_alignment(manifest: pd.DataFrame, raw: Path) -> pd.DataFrame:
    rows = []
    for r in manifest[manifest.modality == "video"].itertuples():
        container_s = probe_duration(raw / r.rel_path)          # ffprobe/PyAV
        audio_s, trim_offset = decode_audio_meta(raw / r.rel_path)
        rows += [
            {"unit_id": r.unit_id, "artifact": "frames",  "offset_s": 0.0,
             "scale": 1.0, "source": "sampling-rule"},
            {"unit_id": r.unit_id, "artifact": "audio",   "offset_s": 0.0,
             "scale": 1.0, "source": "decode"},
            {"unit_id": r.unit_id, "artifact": "asr",     "offset_s": trim_offset,
             "scale": 1.0, "source": "librosa.trim"},
            {"unit_id": r.unit_id, "artifact": "subtitles",
             "offset_s": estimate_sub_offset(r.unit_id),
             "scale": 1.0, "source": "manual-sync-point"},
        ]
        if abs(container_s - audio_s) > 0.5:                    # check V4 lives here
            rows.append({"unit_id": r.unit_id, "artifact": "audio",
                         "offset_s": 0.0, "scale": 1.0,
                         "source": "V4-WARNING"})
    return pd.DataFrame(rows)
```

Every offset row names its **source** — when alignment is wrong at 2 a.m.
before a demo, "where did 0.5 come from?" must be answerable from data.

## 3. Versioning discipline (three version stamps, one meaning)

| Stamp | Lives in | Changes when |
|---|---|---|
| `manifest_version` | manifest header row / filename | schema changes |
| `settings["version"]` | `preproc-settings.json` | output-affecting params change |
| `align["version"]` | alignment parquet | offset rules or sources change |

```python
def aligned_paths(manifest_ver: str, settings_ver: int, align_ver: int) -> dict:
    base = f"data/manifests/corpus-manifest-v{manifest_ver}.parquet"
    return {
        "manifest": base,
        "alignment": f"data/manifests/alignment-v{align_ver}.parquet",
        "embeddings": f"data/embeddings/clip-vit-b32/set-v{settings_ver}/matrix.npy",
    }
```

The discipline: **an artifact's version is part of its path.** No overwrites,
no "current" symlink ambiguity; stale artifacts are visible in `git status`
of `reports/` and deletable by glob.

## 4. The three reports

1. **`validation-report.md`** (file 02) — check × severity × count, gate
   line. CI reads it; humans skim it.
2. **`alignment-report.md`** — per video: artifacts, offsets, sources, and
   the coverage table (which clock spans exist). This is the file you open
   when a demo returns "the frame 40 s away from the quote."
3. **`missing-data-report.md`** (file 03) — policy actions taken: drops,
   flags, imputations with receipts. The due-diligence record for the
   published corpus.

All three regenerate in one command and are committed *as artifacts of a
run*, with the manifest version in their headers — reports are evidence,
not decoration.

## 5. Failure modes of the pipeline itself

| Symptom | Cause | Fix |
|---|---|---|
| Alignment report empty for some videos | stage 2 crashed mid-loop, stage 3 passed | per-unit try/except with rows in report |
| Two manifests differ only in row order | stage 1 unordered walk | sort by `unit_id` before write (determinism) |
| Reports show old version after re-run | stale reports not cleaned | stage 4 deletes `reports/*-v*.md` for lower versions |
| `estimate_sub_offset` returns 0.0 silently | no sync point found | it must *return None* and the row is a warning, not a fake offset |

The last row is the policy worth restating: **unknown beats wrong.** A
`None` offset surfaces as a missing-coverage warning; a fabricated 0.0
corrupts every `window()` query silently.

## Exercises

1. Implement `build_manifest` as a composition of the landscape file's
   functions, sorted and hashed; verify two runs produce identical bytes.
2. Add `--check-only` to `align_corpus.py`: run stages 3–4 against existing
   artifacts without rebuilding (the CI path), and confirm it exits 1 on an
   injected hash mismatch.
3. Trigger each pipeline failure mode above on purpose (crash a stage, walk
   unordered, fabricate an offset) and confirm the corresponding fix makes
   the failure visible.

## Pitfalls

- One giant function instead of four stages — nothing is testable, everything reruns.
- Offsets stored in code comments instead of the alignment parquet — the report and the data disagree within a week.
- Gate on warnings — the pipeline stops meaning "yes"; errors gate, warnings report.

## Resources

- Your manifest schema: [`../01-multimodal-ai-landscape/03-metadata-handling.md`](../01-multimodal-ai-landscape/03-metadata-handling.md).
- ffprobe/PyAV container metadata for stage 1/2 durations.
