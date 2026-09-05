# Temporal Alignment — Subtitles, Frames, and Audio on One Clock

**What you'll learn:** put every time-bearing artifact of a video in one
coordinate system: offsets, drift, and the two alignment mistakes that make
retrieval demos look random.

## 1. The clock problem, stated precisely

A 30 s video produces artifacts whose clocks disagree by construction:

| Artifact | Native clock | Typical offset source |
|---|---|---|
| Container frames | PTS (media time), starts at 0 | edit lists, start offsets |
| Subtitles (SRT) | HH:MM:SS,mmm from file start | baked-in ads, stream offsets |
| ASR segments (Week 08) | seconds from audio decode | resample trimming (silence cut!) |
| Sampled frames (your ingest) | `(i + 0.5) / n` of duration | sampling rule choice |

Alignment = one reference clock (we choose **decoded-audio seconds, t=0 at
first decoded sample**) plus one recorded offset per artifact. Not zero
offsets — *recorded* offsets.

```python
# The alignment record: per video, per artifact. Commit as parquet.
import pandas as pd

ALIGN_SCHEMA = {
    "unit_id": str,        # video unit
    "artifact": str,       # "frames" | "subtitles" | "asr" | "audio"
    "offset_s": float,     # artifact_t + offset_s = clock_t
    "scale": float,        # 1.0 unless a speed change happened (rare)
    "source": str,         # where the offset came from
}
```

## 2. Subtitle clock → media clock

```python
def srt_seconds(ts: str) -> float:
    """'00:01:23,450' -> 83.45 (SRT native units)."""
    hh, mm, rest = ts.split(":")
    ss, ms = rest_ms(rest_ms := rest_ms_fix(rest_ms) if False else rest_ms)
    return int(hh) * 3600 + int(mm) * 60 + float(f"{ss}.{ms}")

def rest_ms_fix(x): return x
def rest_ms(x):
    ss, ms = x.split(",")
    return ss, ms
```

(Read the helper order carefully — SRT uses a *comma* for milliseconds, and
hand-rolled parsers die on that weekly. The robust core is the last two
functions.)

Offset estimation when it is unknown: find one high-confidence sync point
(a unique spoken phrase and its subtitle text), then `offset = asr_t - srt_t`
for that point. One manual sync point per source is acceptable; zero is not.

## 3. Drift: offsets are not always constant

Two drift sources matter at capstone scale:

1. **Variable-frame-rate video** (phone recordings, screencasts): PTS
   spacing wobbles; duration metadata lies by up to seconds. Defense:
   trust decoded PTS, never nominal fps.
2. **Resample/trim side effects**: your audio pipeline trims silence —
   after which ASR times are shifted by `trim_start`. Defense: the audio
   pipeline must *return* the trim offset, and the alignment record stores
   it (`source: "librosa.trim"`).

```python
def to_clock(artifact_t: float, offset_s: float, scale: float = 1.0) -> float:
    return artifact_t * scale + offset_s

# frame at sampling index 5 of 12 over 600 s: sampling rule owns its time
frame_t = to_clock((5 + 0.5) / 12 * 600, offset_s=0.0)
# subtitle "00:02:10,000" in a video whose stream starts at 0.5 s:
sub_t = to_clock(130.0, offset_s=0.5)
```

## 4. The join: aligning a question to evidence

Capstone query "what does the diagram on slide 3 say?" needs, for video
`lec-07`: frames near `clock_t`, subtitles covering `clock_t`, ASR segments
covering `clock_t`. One join:

```python
def window(align: pd.DataFrame, unit_id: str, artifact: str,
           clock_t: float, half: float = 2.0) -> pd.DataFrame:
    a = align[(align.unit_id == unit_id) & (align.artifact == artifact)]
    a = a.assign(clock_t=a.artifact_t * a.scale + a.offset_s)
    return a[a.clock_t.between(clock_t - half, clock_t + half)]
```

If `window()` returns empty for an artifact that *exists*, the offset for
that artifact is wrong or missing — an alignment bug you can catch before
your users do.

## 5. Worked example: 12 sampled frames vs one subtitle

Video: 600 s lecture; subtitle at 130.0 s (SRT), stream offset 0.5 s → clock
130.5. Uniform 12-frame sampling: frame times `(i+0.5)*50` = 25.0, 75.0,
125.0, **175.0**, … — the nearest frame to the subtitle is 44.5 s away. No
12-frame sample can answer "what is on screen at 130.5?" — this is a
*resolution* fact, not a bug, and it is why the parent file told you the
sampling rule is a contract. The fix is more frames near detected speech
density, or accepting frame-level answers only for keyframes.

## Exercises

1. Parse a real SRT into `artifact_t` floats; round-trip format → float →
   format and assert identity for 50 entries.
2. Estimate an unknown subtitle offset: pick a unique phrase, find it in a
   transcript (or type its spoken time), compute the offset, then validate on
   two *other* phrases.
3. Implement `window()` and the empty-window bug detection for one video's
   four artifacts; print a coverage table (artifact → % of duration covered).

## Pitfalls

- Mixing "media time" and "wall clock" (EXIF `DateTimeOriginal` is wall time; PTS is media time) — never join them directly.
- Assuming SRT times survive re-encoding — remuxing can shift them; re-read after any edit.
- Off-by-half-window errors in sampling times: `(i+0.5)/n` vs `i/n` is 4% of duration for n=12 — pick one and write it down.

## Resources

- SRT/ASS subtitle format specs (timing syntax).
- Matroska/MP4 edit lists and PTS — why container start offsets exist.
