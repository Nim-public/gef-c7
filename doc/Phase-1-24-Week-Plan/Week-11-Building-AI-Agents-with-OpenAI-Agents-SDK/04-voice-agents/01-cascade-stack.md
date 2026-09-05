# Cascade Stack — STT → Agent → TTS with Budget Table

**What you'll learn:** the three-stage cascade pipeline, its latency
budget (the number that decides if voice "feels" alive), and where each
stage's milliseconds go.

## 1. The pipeline and the budget

```text
mic ──▶ [VAD] ──▶ [STT] ──▶ [agent loop] ──▶ [TTS] ──▶ speaker
        100ms      300-800ms    1-4s            300-800ms
```

| Stage | Budget | Typical | Levers |
|---|---|---|---|
| VAD + endpointing | 150 ms | 100–200 | aggressiveness, chunk size |
| STT | 500 ms | 300–800 | streaming STT, model size |
| agent (retrieve + generate) | 1500 ms | 1–3 s | budget (W10), typed answer |
| TTS first-byte | 400 ms | 300–800 | streaming TTS, short first phrase |
| **Total** | **~2.5 s** | 2–6 s | — |

The perceptual line: interruptions under ~1 s feel conversational; 2.5 s
feels like a walkie-talkie; 5 s feels broken. The budget's job is to make
the *total* survive — and to name the stage that eats it.

## 2. Stage implementation sketches

```python
import soundfile as sf, numpy as np

def stt_chunk(x: np.ndarray, sr: int = 16_000) -> str:
    assert sr == 16_000 and x.ndim == 1                  # W8 audio contract
    return stt_model.transcribe(x)["text"]

def tts_stream(text: str) -> np.ndarray:
    audio = tts_model.synthesize(text)                   # returns PCM
    return audio

def voice_reply(x: np.ndarray) -> np.ndarray:
    text = stt_chunk(x)
    answer = run_agent_sync(text)                        # your W10 agent
    return tts_stream(answer.answer)                     # typed output, spoken
```

The typed `Answer` from W11 file 03 pays off immediately: TTS speaks
`answer.answer` and *ignores* the citation list — or surfaces it as "see
the corpus page" when the UI wants it.

## 3. Where the milliseconds hide

| Stage | Hidden cost | Fix |
|---|---|---|
| STT | decoding the whole recording before transcript | streaming/partial results |
| agent | retrieval re-encoding per query | warm caches (W7 discipline) |
| agent | LLM full answer before TTS | sentence-streaming into TTS |
| TTS | synthesizing silence/padding | trim, stream chunks |

The big one: **start TTS on the first sentence**, not the final answer.
Sentence-boundary streaming cuts perceived latency by the length of the
shortest first sentence — often 40% of the wait.

## 4. The cascade's honest weakness

Every stage is a *lossy translation*: STT drops names and numbers, the
agent cannot hear tone, TTS flattens emphasis. The mitigation stack:

| Loss | Mitigation |
|---|---|
| STT name errors | vocabulary biasing / hotwords from your manifest |
| no tone | design answers that don't need it (text-first product) |
| TTS monotony | SSML or a better voice; cap the ambition |

Cascade voice is a *feature* on top of a working text agent — never the
core. The capstone rule: the text path works without the voice path.

## Exercises

1. Build the three stages locally; measure per-stage latency on one
   query; fill the budget table with your numbers.
2. First-sentence streaming drill: TTS the first sentence vs the whole
   answer; measure perceived-latency delta (time to first audio).
3. Failure drill: kill each stage in turn; verify the text path still
   answers — the cascade must be a garnish, not a dependency.

## Pitfalls

- Audio at the wrong sample rate reaching STT — the W8 contract (16 kHz
  mono) applies inside the voice path too.
- Speaking the citation list aloud — citations are for the UI; script
  what gets spoken.
- Budget table with no measurements — the numbers above are industry
  ballparks; your stack's numbers are the real ones.

## Resources

- faster-whisper / TTS library docs for your chosen models.
- [`../../Week-08-Encoding-Modalities-Real-World-Architectures/02-encoding-audio-video/01-spectrogram-labs.md`](../../Week-08-Encoding-Modalities-Real-World-Architectures/02-encoding-audio-video/01-spectrogram-labs.md)
  — the audio preprocessing this consumes.
