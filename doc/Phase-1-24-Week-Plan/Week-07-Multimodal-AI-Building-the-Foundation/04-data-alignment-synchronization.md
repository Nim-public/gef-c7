# 04 — Data Alignment & Synchronization

> Week 7 index: [README.md](README.md)

**Session 2 topics:** *Data Alignment and Synchronization: Temporal Alignment, Cross-modal Validation, Missing Data, Alignment Pipeline.*

---

## What you'll learn

- Why alignment — not modeling — is where most multimodal projects fail
- Temporal alignment across frames, audio, and transcripts
- Cross-modal validation as automated integrity checks
- Missing-data policies that keep datasets honest
- A reusable alignment pipeline built on the manifest pattern

## 1. Alignment: the quiet prerequisite

Every multimodal technique ahead assumes **correct pairing**: CLIP learns from *true* image-text pairs; video models assume frame *t* matches audio *t*; RAG citations need chunk→asset identity. A single misaligned pair is not noise — it's a *contradictory training signal* and a *wrong eval label*.

Three alignment axes:

| Axis | Question | Example |
|---|---|---|
| **Pairing** (one-to-one/many) | does A belong with B? | image ↔ one of its 5 captions |
| **Temporal** | does time t in A match time t in B? | frame 200 ↔ audio 8.3s ↔ subtitle line |
| **Referential** | does metadata point to the right asset? | caption "img_0042.jpg" ↔ actual file |

## 2. Temporal alignment

Working with timestamps — frames, audio, and subtitles on one clock:

```python
import json

def align_subtitles_to_frames(subs: list[dict], fps: float, n_frames: int) -> dict:
    """subs: [{'start': 1.2, 'end': 3.4, 'text': '...'}] -> frame->text map"""
    frame_map = {}
    for s in subs:
        f0 = max(0, int(s["start"] * fps))
        f1 = min(n_frames - 1, int(s["end"] * fps))
        for f in range(f0, f1 + 1):
            frame_map.setdefault(f, []).append(s["text"])
    return frame_map

# clock drift check: subtitle timeline vs container duration
def drift_report(subs, video_duration_s):
    last_end = subs[-1]["end"]
    return {"last_sub_end": last_end, "video_end": video_duration_s,
            "drift_s": round(video_duration_s - last_end, 3)}
```

Common traps:

- **Timebases differ**: frames count (`fps`), audio samples (`sr`), seconds (`pts`) — convert once to seconds, centralize the conversion
- **Drift** — subtitles from transcription drift a few hundred ms over an hour; pad boundaries ±0.5s for retrieval, never for frame-accurate labels
- **Start offsets** — audio streams starting at 0.04s vs video at 0; normalize both timelines to the container's start

## 3. Cross-modal validation (automated, not vibes)

A validation pass that runs at ingestion *and* before training/eval:

```python
def validate_pair(row: dict, rules: dict) -> list[str]:
    errors = []
    if not row.get("image_path") or not Path(row["image_path"]).exists():
        errors.append("missing image")
    if row.get("duration_s") and not (0 < row["duration_s"] <= rules["max_duration"]):
        errors.append("duration out of range")
    if row.get("audio_sr") != rules["expected_sr"]:
        errors.append(f"sr {row.get('audio_sr')} != {rules['expected_sr']}")
    if row.get("caption") and len(row["caption"]) < rules["min_caption_chars"]:
        errors.append("caption too short")
    return errors
```

Standard checks per pairing type:

| Check | Pairing | Catches |
|---|---|---|
| asset exists + readable (try-open) | all | broken links, corrupt files |
| duration ≈ transcript length (±10%) | audio-text | truncated/mismatched pairs |
| caption non-empty + unique-ish | image-text | empty/duplicated captions |
| reference id resolves | metadata | the "referential" axis |
| modality fingerprint (sr, WxH) in range | all | wrong exports, resampling bugs |

Run it → `validation_report.jsonl` with one line per failing pair + failure code. Expect 1–5% failures on real corpora; *budget for them*.

## 4. Missing data policies

Missing modalities are the norm. Choose per column, deliberately:

| Strategy | When | Effect |
|---|---|---|
| **Drop row** | eval sets (never fabricate ground truth) | unbiased, smaller n |
| **Drop modality, keep rest** | training with modality-dropout tolerance | model learns robustness |
| **Impute with sentinel/default** | deployment inference (missing audio → empty transcript) | consistent shapes; must be *marked* |
| **Impute with model (caption an image, ASR audio)** | building text views of media | adds model error into labels — version it |
| **Flag and exclude from metrics** | eval subsets | keeps metrics honest |

The policy table goes in your dataset README — "what we did about missing X" is a reviewer's first question.

## 5. The alignment pipeline (putting it together)

```
manifest.jsonl (file 01 records)
   │  1. resolve references (paths → assets, try-open every file)
   │  2. normalize clocks (to seconds; fps/sr recorded)
   │  3. pair assets (join keys; one-to-many maps allowed)
   │  4. cross-modal validation (§3 rules per pair type)
   │  5. missing-data policy applied (flagged, not silent)
   ▼
aligned.jsonl  +  validation_report.jsonl      → DataLoaders (file 03)
```

```python
import hashlib, json
from pathlib import Path

def fingerprint(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:16]

def build_alignment(manifest_rows: list[dict], rules: dict) -> dict:
    aligned, issues = [], []
    for row in manifest_rows:
        errs = validate_pair(row, rules)
        if errs:
            issues.append({"id": row.get("id"), "errors": errs})
            continue
        row = {**row, "fingerprint": fingerprint(Path(row["path"]))}
        aligned.append(row)
    return {"aligned": aligned, "issues": issues,
            "stats": {"in": len(manifest_rows), "ok": len(aligned),
                      "dropped": len(issues)}}
```

Version the alignment output (`aligned_v2.jsonl`); preprocessing/model changes bump the version (file 02's determinism rule).

## Exercises

1. Take 3 YouTube-style clips with subtitles (any .srt): parse SRT → build the frame→text map at 25 fps; report frames with no subtitle coverage.
2. Write `validate_pair` with 6 rules for your capstone's assets; run over your manifest; produce the report. What % drops?
3. Drift experiment: shift all subtitle timestamps by +0.4s and re-run alignment; show 2 concrete mismatches it creates (frame shows next speaker's line).
4. Missing-data split: remove 15% of captions from a copy of your dataset; run your Week 5 retrieval eval on the full vs cleaned set. Quantify the damage of silent pairing errors.
5. Alignment manifest: extend `build_alignment` with a `pairing_version` field and a re-run that only processes *new* assets (incremental alignment).

## Pitfalls

- **Joining on filenames** — `IMG_1234.jpg` collides across cameras; fingerprint or UUID, not basename
- **Silent dropping** — every dropped row must appear in a report with a reason code
- **Imputed data in eval sets** — fabricated ground truth poisons metrics; drop in eval, impute (flagged) only in serving
- **Clock units confusion** — ms vs s vs frames; one conversion function, tested
- **Alignment treated as one-time** — new assets, new rules; make the pipeline re-runnable and versioned

## Resources

- Baltrušaitis et al., *Multimodal ML Survey* — the *alignment* section maps 1:1 to this file
- pyannote / WhisperX — production-grade timestamp alignment for audio-text
- HF [datasets: aligning and validating](https://huggingface.co/docs/datasets/process) — filter/map for validation passes
- The WebVTT/SRT format spec — subtitle timing you'll parse in the wild
