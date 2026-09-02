# 03 — Realtime Voice in Production

> E5 index: [README.md](README.md)

**Core topic:** *Streaming, telephony, and production latency for voice agents — W11-04's budget table, operations edition.*

---

## What you'll learn

- Streaming architecture: chunked STT/TTS vs realtime speech-to-speech APIs
- VAD, endpointing, and barge-in — the turn-taking machinery
- Telephony integration (8 kHz, echo, jitter) and its quality implications
- The production observability set for voice (per-stage metrics, W15's discipline, audio edition)

## 1. The two production architectures (W11-04, operations edition)

**Cascade (streamed)** — your stack, streamed:

```
mic ─► [streaming STT] ─► partial transcript ─► [agent, W11] ─► sentence ─► [streaming TTS] ─► speaker
              ▲ VAD/endpointing decides when the user finished
```

**Realtime speech-to-speech** — one model over a websocket (OpenAI Realtime-class): sub-second turns, native barge-in, function tools supported.

Cascade wins on control/privacy/multilingual control; realtime wins on latency and naturalness. W11-04's decision rule stands; this file adds the *operations*.

## 2. Turn-taking machinery

| Mechanism | What it does | Knobs |
|---|---|---|
| **VAD** (voice activity detection) | is someone speaking? | Silero VAD (tiny, fast) — gate STT and barge-in |
| **Endpointing** | did the user finish? | silence threshold (300–700 ms) + semantic endpointing (LLM: "is this utterance complete?") |
| **Barge-in** | user interrupts the bot | stop TTS playback on mic energy; cancel the in-flight agent run (W11-04 §4) |

The endpointing trade: short silence threshold = fast but cuts people off mid-thought; long = natural but laggy. Semantic endpointing (a cheap LLM judging completeness) fixes the classic "wait, and also…" problem — at the cost of one extra call (route it to the SLM, W15-04).

## 3. Telephony (the 8 kHz reality)

Phone audio arrives 8 kHz μ-law — your W8-02 pipeline resamples, and quality genuinely drops:

- ASR tier: use a robust model tier (Whisper medium-class or telephony-tuned ASR); expect WER to roughly double vs clean audio
- Echo/latency: half-duplex defaults (listen OR speak) avoid echo without echo cancellation; full-duplex needs echo cancellation (Twilio Media Streams-class plumbing)
- Jitter/packet loss: stream TTS in small chunks; insert comfortable silence rather than stutter

Integration shape: Twilio/Vonage Media Streams → websocket → your STT/agent/TTS loop → audio back. The websocket is the audio twin of the W14-05 MCP transport table — one protocol, many providers.

## 4. Voice observability (W15's discipline, audio edition)

Per-call metrics (the voice p95 dashboard):

| Metric | Target |
|---|---|
| STT WER (on sampled clips vs human labels) | < 10% |
| endpoint accuracy (cut-offs per 100 turns) | < 3 |
| agent p95 (turns to answer) | < 2.5 s |
| TTS first-audio latency | < 500 ms |
| barge-in response time | < 300 ms |
| cost/minute | SLA-dependent |

Plus the voice-specific quality signals: interruption frequency, silence ratio, ASR-confidence low turns (re-ask), and hand-off-to-human rate (W5-04's escalation, spoken edition).

## Exercises

1. Build the streaming cascade: Silero VAD → chunked Whisper → your W11 agent → sentence-streamed TTS (file E5-02). Measure per-stage latencies against the W11-04 budget table.
2. Endpointing sweep: silence threshold ∈ {200, 400, 700} ms — count premature cuts and perceived lag. Pick and justify.
3. Barge-in drill: start a long TTS reply and speak over it — measure stop-response time; then fix it (playback thread + cancel).
4. Semantic endpointing probe: 10 utterances that pause mid-thought ("and then I want the…") — does the LLM endpointer wait where the silence-threshold one cuts? (Table.)
5. Cost/minute model: cascade (STT + LLM + TTS) vs realtime API pricing at 30 min/day usage — crossover point for your capstone.

## Pitfalls

- **No barge-in** — users shout over a bot that won't stop; it's the #1 "this feels broken" signal
- **Half-duplex echo** — mic picks up the TTS speaker and the agent transcribes *itself*; echo cancel or gate mic during playback
- **Streaming STT without finalization** — partial transcripts flip meaning at the end; act only on finalized segments
- **Telephony resampling skipped** — 8 kHz audio fed to a 16 kHz pipeline without resampling = quality collapse (W8-02)
- **Per-stage metrics missing** — without per-stage p95 you can't tell whether to fix the STT, the agent, or the TTS; instrument first (W15-02)

## Resources

- OpenAI [Realtime API](https://platform.openai.com/docs/guides/realtime) + [Realtime agents](https://openai.github.io/openai-agents-python/realtime/) — architecture B
- [Silero VAD](https://github.com/snakers4/silero-vad) — the endpointing workhorse
- Twilio [Media Streams](https://www.twilio.com/docs/voice/media-streams) — the telephony websocket layer
- W11-04 (stack + budgets), E5-01/02 (transcript + TTS), W15-01/02 (reliability/observability) — composed here
