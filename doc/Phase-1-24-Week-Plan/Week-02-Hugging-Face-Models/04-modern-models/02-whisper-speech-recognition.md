# 04.2 — Whisper Speech Recognition

> Subfolder index: [README.md](README.md) · Parent: [../04-modern-models.md](../04-modern-models.md)

---

## What you'll learn

- The Whisper model tiers and their real trade-offs
- Timestamps, translation, and language detection
- Long-audio chunking and hallucination control
- Word-level timestamps for the diarization merge (E5-01)

## 1. The tier table, with real numbers

| Model | Params | WER (clean) | Relative speed | VRAM |
|---|---|---|---|---|
| tiny | 39M | ~8% | ~10× | ~1 GB |
| base | 74M | ~7.5% | ~7× | ~1 GB |
| small | 244M | ~6% | ~4× | ~2 GB |
| medium | 769M | ~5.5% | ~2× | ~5 GB |
| large-v3 | 1.55B | ~5% | 1× | ~10 GB |

`.en` variants: English-only, faster, slightly better on English. Distil-Whisper: ~6× faster, ~1% WER worse — the production sweet spot for volume.

```python
from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="openai/whisper-small",
               chunk_length_s=30)                       # long-audio chunking
out = asr("meeting.wav", return_timestamps=True,
          generate_kwargs={"language": "english", "task": "transcribe"})
print(out["text"][:200]); print(out["chunks"][:3])      # sentence chunks with times
```

## 2. The task matrix

| Task | Mechanism | Output |
|---|---|---|
| transcribe | task token: transcribe | text in source language |
| translate | task token: translate | text in **English** only |
| language detection | first 30s analyzed | detected language + probability |
| timestamps | cross-attention alignment | `chunks` with start/end |

The translate task is Whisper's built-in X→English — separate from the dedicated translation models (file 03-03) but zero-setup.

## 3. Long audio and hallucination control

Whisper processes 30-second windows; long recordings need chunking — and chunk boundaries create the classic failures:

| Failure | Cause | Mitigation |
|---|---|---|
| hallucinated phrases on silence | model "completes" silence | VAD-trim silence first (W15-02-era Silero) |
| repeated loops | window boundary artifacts | `condition_on_previous_text=False` or window overlap |
| dropped words at boundaries | words split across windows | overlap windows by 1–2 s, dedupe |
| wrong language detection | multilingual audio noise | force `language=` explicitly |

```python
out = asr("meeting.wav", return_timestamps=True, chunk_length_s=30,
          stride_length_s=(4, 2),                       # overlap windows
          generate_kwargs={"condition_on_previous_text": False,
                           "language": "english"})
```

The hallucinated-content failure is the dangerous one: Whisper on silence produces fluent fabricated sentences that *enter your corpus as facts* (E5-01's warning, mechanism explained). VAD-trimming is the fix.

## 4. Word-level timestamps (the diarization join)

```python
out = asr("meeting.wav", return_timestamps="word")
words = out["chunks"]                    # [{'text': ' Welcome', 'timestamp': (0.0, 0.42)}, ...]
```

Word-level stamps are the join key for speaker diarization (E5-01's merge) — assigning each word to the speaker whose turn overlaps it. Accuracy of the stamps (±100–200 ms) is sufficient for turn-level attribution, marginal for word-level precision — the E5-01 overlap-weighted merge exists for exactly this tolerance.

## Exercises

1. Tier benchmark: tiny/base/small on the same 5-minute recording — WER against your own transcription, plus real-time-factor (processing time ÷ audio time).
2. Hallucination drill: 60 s of silence and 60 s of faint room tone — what does Whisper emit? Then VAD-trim and compare.
3. Chunk-boundary probe: construct audio where a word spans the 30 s window boundary — what happens with and without stride overlap?
4. Translation mode: non-English audio with `task="translate"` — quality vs the dedicated NLLB pipeline (file 03-03).
5. Word-timestamp accuracy: 20 word stamps vs manual marking — distribution of the offset error; is it good enough for speaker attribution (E5-01)?

## Pitfalls

- **Silence hallucination entering corpora** — the fabricated sentences become RAG facts; VAD-trim always
- **`chunk_length_s` without stride** — words split at boundaries; use the stride overlap
- **Condition-on-previous-text loops** — the model repeats itself across windows on hard audio; disable and accept minor context loss
- **Auto language detection on short clips** — wrong language → wrong script; force the language
- **Trusting timestamps at word level blindly** — ±200 ms tolerance; merge by overlap, not exact equality (E5-01)

## Resources

- [Whisper paper](https://arxiv.org/abs/2212.04356) — §1 model, §2.1 (the 30s windows), table of tiers
- HF [ASR task guide](https://huggingface.co/docs/transformers/tasks/asr) — pipeline options
- [distil-whisper](https://github.com/distil-whisper/distil-whisper) — the speed-optimized variants
- E5-01 (diarization merge) — the consumer of these timestamps
