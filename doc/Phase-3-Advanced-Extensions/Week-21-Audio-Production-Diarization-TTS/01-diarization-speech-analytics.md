# 01 — Diarization & Speech Analytics

> E5 index: [README.md](README.md)

**Core topic:** *Who said what — speaker diarization merged with ASR transcripts, and the analytics built on top.*

---

## What you'll learn

- Diarization vs transcription — two models, one join
- pyannote pipelines: diarization + forced alignment with Whisper timestamps
- The merged transcript schema (speaker turns with word-level times)
- Speech analytics: talk-time, interruptions, question detection — meeting/call QA metrics

## 1. Diarization vs transcription

- **ASR (Whisper)** answers *what was said, when* — but not *who*
- **Diarization** answers *who was speaking, when* — but not *what*
- The product is the **join**: speaker-labeled transcript turns. The join is where quality is won or lost (W13-01's alignment discipline, audio edition).

```python
from pyannote.audio import Pipeline

diar = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                use_auth_token="hf_...")     # gated: accept license on the Hub
diarization = diar("meeting.wav", num_speakers=3)            # known count helps a lot
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:7.2f} {turn.end:7.2f} {speaker}")
```

## 2. The merge: Whisper timestamps × speaker turns

```python
import whisper_timestamped as wt

audio = wt.load_audio("meeting.wav")
result = wt.transcribe(audio, "whisper-small")   # word-level timestamps

def merge(result, diarization) -> list[dict]:
    turns = []
    for seg in result["segments"]:
        mid = (seg["start"] + seg["end"]) / 2
        speaker = max(diarization.itertracks(yield_label=True),
                      key=lambda t, _: 0, default=(None, None, "SPEAKER_00"))[2]
        # better: overlap-weighted assignment below
        best, best_overlap = "SPEAKER_00", 0.0
        for turn, _, spk in diarization.itertracks(yield_label=True):
            ov = min(seg["end"], turn.end) - max(seg["start"], turn.start)
            if ov > best_overlap:
                best_overlap, best = ov, spk
        turns.append({"speaker": best, "start": seg["start"], "end": seg["end"],
                      "text": seg["text"].strip()})
    return turns
```

Overlap-weighted assignment beats midpoint for segments spanning two speakers; word-level times (Whisper's per-word stamps) refine it further — assign each *word*, then group words by speaker within segments.

Known hard cases (test all three): crosstalk (both speak — pick dominant by overlap, flag `overlap=true`), speaker label churn (SPEAKER_00/01 swap identity across segments — a clustering artifact; fix with stable naming or embeddings), and short interjections ("yes", "right") — too short for reliable diarization; merge into the neighboring turn.

## 3. The merged transcript schema (the RAG contract)

```python
{"meeting_id": "m-123", "participants": ["Priya", "Ravi", "Sam"],
 "turns": [{"speaker": "Priya", "start": 12.4, "end": 18.9,
            "text": "We'll commit to the 5-day refund window for tier 2."}],
 "analytics": {"talk_time": {"Priya": 640, "Ravi": 410}, "interruptions": 7}}
```

Chunking for RAG (W4-02): chunk by *speaker turn groups* (a topic exchange, 3–6 turns) — never mid-turn — with speaker and time-range metadata. Citations become `"Priya, 12:04–12:18"` — the meeting-assistant's killer feature (file 04).

## 4. Speech analytics (the metrics layer)

| Metric | Computation | Use |
|---|---|---|
| talk-time share | sum turn durations per speaker | dominance/balance (calls QA) |
| interruptions | turn starts while another's turn is active | conflict/agility signal |
| question rate | count turns ending in "?" (or classifier) | engagement |
| commitment detection | LLM on turns: "who committed to what, by when" | action items (file 04's flagship) |
| sentiment arc | per-turn sentiment (W2-02 classifier) over time | escalation detection |

All computed from the merged schema — no audio models needed past this point. That's the design principle: **audio models convert sound to structured text; everything downstream is your W1–14 text stack.**

## Exercises

1. Diarize a 3-speaker recording (your own, consented) at known/unknown speaker counts — compare turn quality. What changes when `num_speakers` is wrong?
2. Implement `merge` with overlap-weighted assignment; hand-audit 10 turns against the audio. Speaker-accuracy estimate?
3. Crosstalk drill: record two people talking over each other for 5 s — how do the turns and overlap flags come out?
4. Build the analytics table (§4) for a real meeting; write 3 observations an account manager would care about.
5. RAG-index a diarized meeting (W4-05 pipeline, turn-group chunks); ask "what did Priya commit to?" — does the answer cite the speaker+time? This is file 04's core demo.

## Pitfalls

- **Trusting diarization labels as identities** — SPEAKER_00 is a cluster id, not a person; map to names via enrollment samples or user confirmation
- **Mid-turn chunking** — speaker context lost; chunk by turn groups (§3)
- **Overlap unflagged** — crosstalk turns are unreliable; mark and down-weight them in analytics
- **Storing raw meeting audio casually** — consent, retention, and biometric-PII rules (W11-04's table) apply doubly to meetings
- **Speaker count hardcoded** — wrong `num_speakers` silently merges people; use auto + confirm

## Resources

- [pyannote.audio docs](https://huggingface.co/pyannote/speaker-diarization-3.1) — pipeline, gating, tuning
- [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) — word-level timestamps
- W8-02 (preprocessing), W9 (indexing), W11-04 (voice stack) — composed here
- Bredin & Laurent, *pyannote.audio 2.1/3.1* papers — the diarization models
