# 02 — TTS & Voice Cloning

> E5 index: [README.md](README.md)

**Core topic:** *Text-to-speech quality, control, and voice cloning — with the consent obligations that come with it.*

---

## What you'll learn

- TTS model landscape: API voices vs open models (Coqui) vs cloning
- Quality/control knobs: voice, speed, prosody markers
- Voice cloning: what's possible, what it costs, and the consent/legal line
- SSML-style control and streaming TTS for agents (W11-04's output stage)

## 1. The TTS landscape

| Tier | Examples | Traits |
|---|---|---|
| API voices | OpenAI TTS, ElevenLabs, Azure Neural | best quality, per-character cost, fixed voice catalog (some cloning tiers) |
| Open models | Coqui XTTS-v2, Piper, F5-TTS | free, self-hosted, cloning support (XTTS), quality varies |
| Cloning services | ElevenLabs Voice Cloning, Azure Custom Voice | near-identical voices — **consent-gated by policy** |

Selection for the capstone: **API voice** for demos (quality in 5 minutes), **open model** for privacy/on-prem requirements, **cloning** only with documented consent (§3).

## 2. Open TTS with Coqui

```powershell
pip install TTS
```

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

tts.tts_to_file(
    text="The refund window for tier two is five business days.",
    speaker_wav="data/voices/enrolled.wav",      # 6s+ clean reference sample
    language="en",
    file_path="out/reply.wav")

# multilingual: same voice, other languages (hi, de, es, ...)
```

Quality knobs that matter: reference-sample *cleanliness* (noise in → cloned artifacts out), sentence splitting (long text needs per-sentence synthesis + concatenation, or prosody drifts), and speed control (`speed=0.95` reads better for agents).

## 3. Voice cloning — the capability and the line

What's possible: 6 seconds of clean reference audio → a convincing clone speaking *any* text in *any* supported language.

The obligations (non-negotiable in this program):

1. **Explicit consent** — written, from the voice owner, for the specific use; a verbal OK in a meeting is not consent
2. **Disclosure** — cloned-voice outputs must be labeled as synthetic where users hear them (product or demo)
3. **No third-party voices** — cloning a public figure/celebrity/colleague without consent is impersonation; several jurisdictions criminalize it
4. **Watermarking where available** — some APIs embed inaudible watermarks; prefer them
5. **Retention** — reference samples stored encrypted, deleted on opt-out (W7-01 metadata discipline)

The test: if the voice owner watched your demo, would they consent to what they're hearing? If not certain — don't.

## 4. Agent integration (W11-04's TTS stage, quality edition)

```python
def speak_reply(text: str) -> None:
    for sentence in split_sentences(text):        # stream per sentence
        wav = tts_sentence(sentence)
        play(wav)                                 # or stream chunks to the client
```

- **Split before speaking** — the first sentence plays while the rest synthesizes (latency hiding, W11-04's budget)
- **Numbers/dates/citations read poorly** — expand ("₹45,000" → "forty-five thousand rupees") before TTS; keep the citation text for the UI, not the ear
- **Consistent voice identity** — one enrolled voice per assistant persona across sessions (W3-02's persona consistency, spoken)

## Exercises

1. Generate the same 3 sentences with 3 voices (2 API, 1 Coqui); blind-rate naturalness with 3 listeners. Table.
2. Reference-quality A/B: clone from a clean 10s sample vs a noisy 10s sample — describe the artifact difference.
3. Number-expansion drill: TTS "Order #45,002 shipped 03/04" raw vs pre-expanded — which is intelligible? Write the expander (W1-02 regex skills).
4. Multilingual: same voice, English and Hindi sentences (XTTS) — prosody and pronunciation quality; note failure modes.
5. Consent packet: draft the one-page consent + disclosure document for using a teammate's cloned voice in the capstone demo. (This is a deliverable, not bureaucracy.)

## Pitfalls

- **Cloning without written consent** — program-fail; see §3's line
- **Reading citations/IDs aloud** — "bracket doc 42" is ear-poison; strip citations from spoken text, keep in UI (W11-04)
- **One giant TTS call for a paragraph** — prosody drift + slow start; sentence-split and stream
- **Emotion-free defaults** — flat delivery reads as robotic; add punctuation-driven prosody and speed variation per sentence type
- **TTS cost by character** — long answers are expensive to speak; the voice constitution (W11-04's ≤2 sentences rule) is a cost control too

## Resources

- [Coqui TTS docs](https://docs.coqui.ai/) — XTTS-v2 usage + multilingual notes
- OpenAI [TTS guide](https://platform.openai.com/docs/guides/text-to-speech) · ElevenLabs [docs](https://elevenlabs.io/docs) — API voices + cloning policies
- [SSML primer](https://www.w3.org/TR/speech-synthesis11/) — prosody control vocabulary
- W11-04 (latency budgets), W8-02 (audio preprocessing for reference samples) — composed here
