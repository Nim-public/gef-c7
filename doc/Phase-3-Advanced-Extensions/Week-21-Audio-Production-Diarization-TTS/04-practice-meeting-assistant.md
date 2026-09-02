# 04 — Practice: Meeting Intelligence Assistant

> E5 index: [README.md](README.md) · **Due: before E6**

*(Practice build — the flagship audio pipeline: record → transcribe → diarize → index → query with speaker citations → action items → spoken summary.)*

---

## 1. Deliverable

```
meeting-intel/
  ingest.py              # audio → Whisper transcript (word timestamps) → diarization merge (E5-01)
  analytics.py           # talk-time, interruptions, commitments (E5-01 §4)
  index.py               # turn-group chunks → your W4/W9 RAG index with speaker/time metadata
  qa.py                  # meeting QA with speaker+time citations
  speak.py               # TTS summary (E5-02, consent-compliant voice)
  eval/
    results.md           # WER sample, speaker accuracy, retrieval/QA quality
  README.md              # pipeline, decisions, consent notes
```

Demo: 5-minute meeting (3 speakers, consented) → diarized transcript → RAG QA ("what did Priya commit to?", "who raised the pricing concern?") → spoken action-item summary.

## 2. Requirements (graded)

### Ingestion (E5-01)
- [ ] Whisper word-timestamped transcript + pyannote diarization merged (overlap-weighted)
- [ ] Overlap flagging + short-interjection merging demonstrated
- [ ] Speaker labels mapped to real names (enrollment or manual confirm), documented

### Analytics + RAG (E5-01 §4)
- [ ] Analytics table (talk-time, interruptions, questions) on a real meeting
- [ ] Turn-group chunks indexed with speaker/time metadata (W4-05 harness-compatible)
- [ ] QA with speaker+time citations: "Priya, 12:04–12:18" format, ≥90% of factual claims cited
- [ ] Commitment extraction: "who committed to what, by when" table from the LLM, verified against the transcript

### Voice output (E5-02/03)
- [ ] TTS summary with sentence streaming + number/date expansion (E5-02 ex. 3)
- [ ] Consent packet for any cloned/enrolled voice (E5-02 §3 — required if cloning, optional otherwise)

### Evaluation (W15-05 discipline)
- [ ] WER sample: 60 s of audio vs your own transcript
- [ ] Speaker-accuracy sample: 20 turns hand-checked
- [ ] Meeting QA: 10 questions with citations — accuracy + citation coverage

## 3. Rubric

| Area | Weight |
|---|---|
| Ingestion (merge quality, overlap handling, speaker mapping) | 30% |
| Analytics + RAG QA with speaker citations | 30% |
| Voice output (streaming, expansion, consent) | 20% |
| Evaluation (WER, speaker accuracy, QA) | 15% |
| README (pipeline, consent, decisions) | 10% |

## 4. README sections (answer explicitly)

1. **Pipeline diagram**: audio → transcript → diarization → analytics → index → QA → voice (ASCII, per-stage latency)
2. **Join quality**: speaker-accuracy estimate, crosstalk handling, the merge rule you shipped
3. **Consent & privacy**: recording consent, voice enrollment consent, audio retention policy, PII in transcripts (W11-04's table, restated for meetings)
4. **Capstone integration**: which capstone questions does meeting QA answer that W4–9 retrieval couldn't? (Commitments? decisions? owners?)
5. **E6 bridge**: your voice stack's remaining latency gaps — which inference/decoding optimizations (speculative decoding, constrained output, quantized STT) would you apply? (E6's preview, pre-applied to your numbers.)

## 5. Stretch (pick one)

- Live mode: the meeting pipeline running on a live mic with 30 s windows and incremental indexing (streaming RAG)
- Action-item tracker: commitments extracted across *multiple* meetings into a SQLite table (W6) — "what did we promise the client?" answered across meetings
- Speaker-adaptive QA: "what did *I* say?" resolved from the authenticated user's speaker embedding (consent-gated)

Bring the QA demo to your next mentor session: speaker-cited meeting intelligence is the single most demo-able audio capability — and the consent/citation discipline is what makes it production-credible rather than a novelty.
