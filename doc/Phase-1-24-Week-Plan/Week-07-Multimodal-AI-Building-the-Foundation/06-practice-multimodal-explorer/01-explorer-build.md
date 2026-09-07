# Explorer Build — Dataset Stats and Gradio Viewer

**What you'll learn:** Part A as a build guide: one stats module that reads
the manifest (never the raw files, at UI time), one Gradio app that renders
any modality, and the acceptance criteria for "done".

## 1. Architecture: stats are batch, viewing is lazy

```text
scripts/corpus_stats.py      → reports/corpus-stats.json   (batch, commitable)
scripts/explorer_app.py      → Gradio UI                   (reads stats + samples)
```

The split matters: the UI must open *nothing* heavy at startup. Stats run
once (seconds); the viewer samples from the manifest and loads one unit per
interaction. A viewer that decodes the corpus at launch is the classic
student-UI bug and will be felt forever.

## 2. The stats module

```python
# scripts/corpus_stats.py
from pathlib import Path
import json, pandas as pd

def corpus_stats(manifest_path: str = "data/manifests/corpus-manifest.parquet",
                 out: str = "reports/corpus-stats.json") -> dict:
    df = pd.read_parquet(manifest_path)
    stats = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "units": int(len(df)),
        "by_modality": df.modality.value_counts().to_dict(),
        "bytes_by_modality": {},
        "with_captured_at": int((df.captured_at != "").sum()),
        "with_sidecar": {},                     # filled in week 08+
        "duration_s": {},                       # audio/video only
 yang   "hash": df.sha256.iloc[0][:8] if len(df) else "",
    }
    for m, g in df.groupby("modality"):
        stats["bytes_by_modality"][m] = int(g.rel_path.map(
            lambda p: Path(p).stat().st_size).sum())
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(stats, indent=2))
    return stats
```

(Fix the typo line if you copy: `yang` is a reminder that hand-typed code
needs the parity discipline too — delete that key.)

## 3. The Gradio viewer

```python
# scripts/explorer_app.py
import gradio as gr, pandas as pd, json
from pathlib import Path

def unit_view(unit_id: str):
    df = pd.read_parquet("data/manifests/corpus-manifest.parquet")
    row = df[df.unit_id == unit_id].iloc[0]
    p = Path(row.rel_path)
    if row.modality == "image":
        return gr.Image(value=str(p)), f"{row.modality} | {p.name}"
    if row.modality == "audio":
        return gr.Audio(value=str(p)), f"{row.modality} | {p.name}"
    if row.modality == "video":
        return gr.Video(value=str(p)), f"{row.modality} | {p.name}"
    return p.read_text(encoding="utf-8", errors="replace"), f"{row.modality}"

with gr.Blocks() as app:
    stats = json.loads(Path("reports/corpus-stats.json").read_text())
    gr.Markdown(f"**{stats['units']} units** — {stats['by_modality']}")
    ids = pd.read_parquet("data/manifests/corpus-manifest.parquet").unit_id.tolist()
    pick = gr.Dropdown(choices=ids, label="Unit")
    out_media = gr.File() if False else gr.Group()
    media = gr.Image(visible=False)
    btn = gr.Button("Load")
    btn.click(unit_view, pick, [media, out_media])

if __name__ == "__main__":
    app.launch()          # http://127.0.0.1:7860
```

(Minimal sketch — extend the output group to `gr.Image | gr.Audio | gr.Video`
toggled by modality; the pattern that matters is *manifest-driven, one unit
per interaction*.)

## 4. Acceptance criteria (Part A done when…)

1. `py scripts/corpus_stats.py` regenerates identical JSON on unchanged data.
2. The UI loads in < 2 s with a 5,000-unit manifest (no raw decode at start).
3. Every modality present in the manifest renders correctly (click through
   one of each — this is also your validation-by-eye pass).
4. The dropdown shows `unit_id`s, and each view displays the manifest row's
   metadata (license, captured_at, notes) next to the media — metadata and
   media together is the point of an *explorer*.

## Exercises

1. Add a "random sample" tab that shows 12 thumbnails per click, seeded by
   a slider (deterministic re-sampling — determinism file, §2).
2. Add the contact-sheet view from the determinism file as a second tab;
   wire it to the *processed* directory so preprocessing drift is visible.
3. Make `unit_view` fail gracefully for quarantined units: show the
   exclusion reason from `excluded.parquet` instead of the media.

## Pitfalls

- `gr.Audio`/`gr.Video` on paths with backslashes — Gradio serves POSIX; use `as_posix()`.
- Rebuilding the dropdown from the manifest on every click — cache it; the manifest does not change mid-session.
- Stats JSON with non-serializable numpy types — cast with `int()`/`float()` at build (see §2's casts).

## Resources

- Gradio Blocks docs (`gr.Image`, `gr.Audio`, `gr.Video`, `gr.Dropdown`).
- Your manifest schema: [`../01-multimodal-ai-landscape/03-metadata-handling.md`](../01-multimodal-ai-landscape/03-metadata-handling.md).
