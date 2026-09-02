# Extension E5 — Audio Production: Diarization, TTS & Realtime Voice

> Extensions overview: [../README.md](../README.md)

**Builds on:** W8-02 (audio encoding) · W11-04 (voice agents) · W9 (RAG over transcripts)

**Practice build:** [04-practice-meeting-assistant.md](04-practice-meeting-assistant.md)

---

## Why this extension matters

W11-04's push-to-talk demo is the toy; this week is the production stack: **who said what** (diarization), **speak back** (TTS/voice quality), and **stay under budget at scale** (realtime patterns, telephony). The flagship build — a meeting assistant that records, transcribes, diarizes, indexes into your RAG, and answers "what did Priya commit to?" with speaker-level citations — is one of the strongest capstone demos available.

## What you will be able to do after this week

- [ ] Run speaker diarization (pyannote) and merge it with Whisper transcripts
- [ ] Build the meeting-assistant pipeline: record → transcribe → diarize → index → query with speaker citations
- [ ] Produce quality TTS output; understand voice cloning capability + consent obligations
- [ ] Deploy realtime voice within a latency budget (W11-04's table, production edition)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-diarization-speech-analytics.md](01-diarization-speech-analytics.md) | Who-said-what: diarization + transcript alignment | 3 h |
| 2 | [02-tts-voice-cloning.md](02-tts-voice-cloning.md) | TTS models, quality knobs, cloning consent | 2 h |
| 3 | [03-realtime-voice-production.md](03-realtime-voice-production.md) | Streaming, telephony, production latency | 2–3 h |
| 4 | [04-practice-meeting-assistant.md](04-practice-meeting-assistant.md) | Meeting assistant end-to-end (practice) | 4 h |

## Environment setup

```powershell
pip install pyannote.audio whisper-timestamped soundfile librosa
pip install TTS                        # Coqui TTS (file 02)
# pyannote needs a HF token + model-license acceptance (gated models)
```

## Self-check before E6

1. Whisper gives you text with timestamps; diarization gives you speaker turns. What's the join key — and what breaks when someone talks over someone?
2. A meeting summary quotes a decision to the wrong speaker. Which pipeline stage do you blame, and how do you verify?
3. Voice cloning a teammate's voice for the demo — what must you have before generating a single word?
4. Telephony audio is 8 kHz. Why does your 16 kHz-trained ASR degrade, and what's the fix (W8-02's rules)?
5. Your realtime voice bot's p95 is 2.4 s. Which stage cuts first (W11-04's budget table) — and what does streaming buy you?
