# 04 — Voice Agents

> Week 11 index: [README.md](README.md)

**Session 2 topic:** *Voice Agents.*

---

## What you'll learn

- The voice-agent stack: STT → text agent → TTS, and the realtime speech-to-speech alternative
- The latency budget that makes voice the hardest agentic surface
- A minimal working push-to-talk demo (Whisper + your W11 agent + TTS)
- Production concerns: turn-taking, barge-in, telephony, privacy

## 1. The two architectures

**A. Cascade (pipeline)** — your existing stack, connected:

```
mic audio ─► STT (Whisper, W8-02) ─► text ─► agent (SDK, files 01–03) ─► text ─► TTS ─► speaker
```

- Reuses *everything* you've built (guardrails, sessions, tools)
- Costs: three models in series → latency stacks; tone/prosody lost at the text boundary

**B. Realtime speech-to-speech** — one model hears and speaks (OpenAI Realtime API class):

- Sub-second responses, natural turn-taking, interruption handling built in
- Costs: your guardrails/tools attach differently (function tools still supported); less framework surface than the cascade; provider-coupled

Decision rule: **cascade for capstone and control** (you own every stage), **realtime for conversational polish** when the budget demands sub-second responses.

## 2. The latency budget (the design constraint)

Human conversation feels natural below ~1 s response gaps; everything above 2–3 s feels broken. Budget cascade-style:

| Stage | Typical | Notes |
|---|---|---|
| STT (Whisper small, 5 s clip) | 300–800 ms | streaming STT cuts perceived latency |
| agent loop (1 tool call) | 800–2500 ms | the killer — every extra turn adds a full LLM roundtrip |
| TTS | 200–500 ms | streaming TTS starts speaking the first sentence early |
| **total (1 tool)** | **1.3–3.8 s** | 2 tools → double the agent stage |

Mitigations, in order of leverage: **stream everything** (partial transcripts in, audio out sentence-by-sentence), **fewer turns** (voice prompts need tighter tool contracts — W10-02's rules, stricter), **smaller/faster models** for the voice path (W2-05), and **realtime API** when the cascade can't fit budget. Also: pre-compute (cache greetings, prime the TTS voice).

## 3. Minimal cascade demo (push-to-talk)

```powershell
pip install openai soundfile numpy
```

```python
import sounddevice as sd, soundfile as sf, numpy as np, base64, io
from agents import Agent, Runner
from openai import OpenAI

client = OpenAI()
agent = Agent(name="Voice capstone assistant",
              instructions="Answer capstone questions in <=2 sentences.",
              tools=[])

def record(seconds: int = 5, sr: int = 16000) -> np.ndarray:
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()

def stt(wav: np.ndarray, sr: int) -> str:
    buf = io.BytesIO(); sf.write(buf, wav, sr, format="WAV"); buf.seek(0)
    buf.name = "clip.wav"
    return client.audio.transcriptions.create(model="whisper-1", file=buf).text

def tts(text: str, voice: str = "alloy") -> None:
    speech = client.audio.speech.create(model="tts-1", voice=voice, input=text)
    audio = np.frombuffer(speech.content, dtype=np.int16)      # pcm16
    sd.play(audio.astype(np.float32) / 32768, 24000); sd.wait()

def once():
    wav = record()
    text = stt(wav, 16000)
    print("you:", text)
    reply = Runner.run_sync(agent, text).final_output
    print("bot:", reply)
    tts(reply)

once()      # push-to-talk: run per utterance; VAD automates the trigger in prod
```

Read it against the budget table: `stt` → `Runner.run_sync` → `tts` are the three stages, and `agent`'s tools decide how many roundtrips the middle costs. (W8-02's audio preprocessing rules apply to `wav` — 16 kHz mono is exactly right here.)

## 4. Production concerns (what breaks after the demo)

| Concern | Cascade answer | Realtime answer |
|---|---|---|
| **Turn-taking** (when does the user finish?) | VAD + endpointing (silence threshold) | built-in server VAD |
| **Barge-in** (user interrupts the bot) | stop TTS playback on mic energy; cancel agent run | built-in |
| **Hallucinated STT on silence** | trim silence (W8-02), min-length gate | model-side |
| **PII in voice** | same guards as text (W5-04) + don't store raw audio by default; voice = biometric PII | same |
| **Prompt injection by audio** ("ignore instructions" spoken) | STT → text → your existing guardrails apply | injectable via tools; test |
| **Telephony (8 kHz phone audio)** | resample + robust STT tier | provider media streams |

One more human factor: voice answers must be **shorter and simpler** than chat — write a voice-specific constitution ("≤2 sentences, no lists, spell out numbers") as a distinct system prompt, not the chat one.

## Exercises

1. Run the cascade demo; measure stage latencies (time each function). Which stage dominates for a *tool-using* answer vs a no-tool answer?
2. Barge-in prototype: play TTS in a thread; monitor mic energy and stop playback when the user speaks. What state must you clean up mid-run?
3. Voice constitution A/B: same 5 questions with the chat prompt vs a voice-tuned prompt (≤2 sentences rule). Read the TTS outputs aloud — which sounds like a product?
4. Injection by voice: play a TTS clip saying your W3-02 injection line; send the transcript through the guarded agent (file 02). Does the guardrail catch spoken-form injections?
5. Latency design doc: for your capstone, would voice be cascade or realtime? Write the p95 budget per stage and the one tool you'd expose first.

## Pitfalls

- **Chat-length answers read aloud** — 300-word responses are unusable by ear; voice prompts need their own constraints
- **Blocking the audio thread** — playback/capture in threads; one blocking call freezes the loop
- **Trust STT text as user intent** — mis-transcriptions route agents wrong; show/confirm critical actions
- **Storing raw voice casually** — biometric PII + retention laws; hash/reference, don't accumulate (W7-01 metadata discipline)
- **Realtime API lock-in without fallback** — keep the cascade path; providers change voice-model terms quickly

## Resources

- OpenAI [Speech-to-text](https://platform.openai.com/docs/guides/speech-to-text) & [TTS](https://platform.openai.com/docs/guides/text-to-speech) guides
- OpenAI [Realtime agents](https://openai.github.io/openai-agents-python/realtime/) + [Realtime API docs](https://platform.openai.com/docs/guides/realtime) — architecture B
- [openai-realtime-agents repo](https://github.com/openai/openai-realtime-agents) — supervisor/handoff patterns over realtime
- Whisper serving notes (W2-04) + WebRTC/telephony primers — for the deployment layer
