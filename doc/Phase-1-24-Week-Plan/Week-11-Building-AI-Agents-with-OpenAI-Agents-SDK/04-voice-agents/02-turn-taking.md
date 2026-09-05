# Turn-Taking — VAD, Endpointing, Barge-In

**What you'll learn:** the three mechanics that make voice conversational
rather than walkie-talkie: voice activity detection, end-of-turn
detection, and barge-in — each with a detector and a failure mode.

## 1. VAD — where speech is

```python
import numpy as np

class EnergyVAD:
    """Baseline energy VAD — fine for push-to-talk, weak for real convo."""
    def __init__(self, thresh_rms: float = 0.01, hangover_ms: int = 300):
        self.thresh = thresh_rms; self.hangover = hangover_ms
        self._silent_for = 0

    def is_speech(self, chunk: np.ndarray, sr: int = 16_000) -> bool:
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        speech = rms > self.thresh
        if speech:
            self._silent_for = 0
        else:
            self._silent_for += len(chunk) / sr * 1000
        return speech or self._silent_for < self.hangover
```

Energy VAD is the floor (free, wrong in noise); a small neural VAD
(Silero-class, ~1 ms/chunk) is the production default. The hangover
parameter — how long silence is tolerated before declaring end — is the
*same knob* as endpointing below; tune them together.

## 2. Endpointing — when the turn ended

| Strategy | Mechanism | Failure |
|---|---|---|
| fixed silence | 500 ms of silence → end | slow speakers get cut off |
| adaptive | silence threshold scales with speech rate | needs calibration |
| semantic | small model judges "is the sentence complete?" | +latency, +cost |

```python
def endpoint(vad_silence_ms: int, speech_rate_wpm: int) -> int:
    base = 400 if speech_rate_wpm > 140 else 700
    return base                                        # adaptive-ish default
```

The two failure modes are opposite: too-early endpointing truncates
thinking pauses ("what is, uh, the margin on..."), too-late feels
unresponsive. The capstone default: 500–700 ms adaptive + semantic
endpointing only if the demo demands it (the latency budget punishes
it).

## 3. Barge-in — interrupting the agent

```python
class BargeIn:
    def __init__(self):
        self.speaking = False
        self.tts_stream_cancel = False

    def on_user_audio(self, chunk: np.ndarray, vad: EnergyVAD):
        if self.speaking and vad.is_speech(chunk):
            self.tts_stream_cancel = True        # stop TTS immediately
            self.speaking = False                # return the floor
```

Barge-in is what separates a voice *assistant* from a voice *announcer*:
the user must be able to cut the agent off. Mechanics: VAD keeps
listening during TTS playback; speech during playback cancels the TTS
stream and returns the floor to the user. The caught-mid-answer text
stays in history — the agent re-reads it on the next turn (sessions,
file 01).

## 4. The state machine (the whole system, one diagram)

```text
IDLE ──speech──▶ LISTENING ──endpoint──▶ THINKING ──first token──▶ SPEAKING
  ▲                                                                │
  └────────────────── barge-in (speech during SPEAKING) ◀──────────┘
```

| Transition | Guard |
|---|---|
| LISTENING → THINKING | endpoint fired AND VAD confirms non-speech |
| SPEAKING → LISTENING | barge-in OR playback complete |
| THINKING → SPEAKING | first TTS byte ready |

Every voice bug is a missing or mis-tuned transition guard; the state
machine is the debugging surface.

## Exercises

1. Tune endpointing on your own speech: record 10 queries with thinking
   pauses; find the silence threshold that never truncates and never
   dawdles; write your number down.
2. Barge-in drill: play TTS and speak over it; verify cancellation latency
   (time from speech onset to TTS stop) < 300 ms.
3. State-machine audit: instrument the transitions; log any illegal
   transition (e.g., THINKING → LISTENING without endpoint); zero illegal
   transitions is the bar.

## Pitfalls

- VAD tuned in silence, demoed in a noisy room — threshold on your
  actual mic and room, or carry a neural VAD.
- Barge-in without history repair — the agent re-answers from scratch
  and loses the interrupted context; sessions (file 01) keep it.
- Endpointing measured in file, not milliseconds — the budget table is
  in ms; keep units consistent.

## Resources

- Silero VAD (neural, tiny, fast); WebRTC VAD as the classic baseline.
- [`../01-cascade-stack.md`](../01-cascade-stack.md) — the budget these
  mechanics spend.