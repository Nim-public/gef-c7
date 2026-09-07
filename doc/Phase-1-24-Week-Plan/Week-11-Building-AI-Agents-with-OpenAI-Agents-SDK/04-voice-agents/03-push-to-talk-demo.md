# Push-to-Talk Demo — The Minimal Working Build

**What you'll learn:** the demo that sidesteps turn-taking entirely:
push-to-talk removes endpointing and barge-in from the problem, leaving
a three-stage pipeline you can ship in an afternoon — and measure.

## 1. The architecture (what push-to-talk deletes)

```text
hold key ──▶ record ──▶ release ──▶ [STT] ──▶ [agent] ──▶ [TTS] ──▶ play
                  no VAD, no endpointing, no barge-in
```

Push-to-talk trades naturalness for determinism: the *user* does
endpointing (releasing the key), VAD shrinks to a gate on the recording,
and barge-in is irrelevant (you cannot talk while holding the key). The
budget from file 01 still applies — but only across the pipeline, not
the conversation.

## 2. The implementation

```python
# scripts/voice_demo.py
import sounddevice as sd, numpy as np, keyboard  # pip: sounddevice, keyboard
from agents import Runner, SQLiteSession

SR = 16_000

def record_until_release() -> np.ndarray:
    chunks = []
    with sd.InputStream(samplerate=SR, channels=1, dtype="float32") as stream:
        while keyboard.is_pressed("space"):
            data, _ = stream.read(1600)          # 100 ms chunks
            chunks.append(data.copy())
    return np.concatenate(chunks) if chunks else np.zeros((0,), dtype="float32")

def main():
    session = SQLiteSession("voice-demo", "data/voice.db")
    while True:
        print("hold SPACE to talk, ctrl+c to quit")
        x = record_until_release()
        if len(x) < SR // 2:                     # <0.5 s: ignore taps
            continue
        text = stt_chunk(x)                      # file 01's STT stage
        result = Runner.run_sync(agent, text, session=session)
        answer = result.final_output.answer      # typed output (file 01)
        audio = tts_stream(answer)
        sd.play(audio, SR); sd.wait()
        print(f"you: {text}\nagent: {answer}")

if __name__ == "__main__":
    main()
```

Under 60 lines, using everything you already built: the 16 kHz contract,
the typed agent, sessions. The new code is only *plumbing* — capture,
playback, and the loop.

## 3. The demo's measurement duty

A voice demo without a latency table is a party trick. The run logs:

| Metric | Source | Budget |
|---|---|---|
| capture length | sample count | user-controlled |
| STT ms | timer around `stt_chunk` | ≤800 |
| agent ms | trajectory store (`duration_ms`) | ≤1500 |
| TTS-to-first-byte ms | timer | ≤400 |
| total ms | sum | ≤2.5 s |

```python
import time
t0 = time.perf_counter(); text = stt_chunk(x); stt_ms = (time.perf_counter()-t0)*1000
```

The table prints per interaction — and lands in `reports/voice-latency.md`
as the demo's evidence.

## 4. From push-to-talk toward full duplex (the growth path)

| Step | Adds | Cost |
|---|---|---|
| 1. push-to-talk (this file) | working pipeline | — |
| 2. VAD-gated auto-record | hands-free start | VAD tuning (file 02) |
| 3. endpointing | natural turn ends | the two-failure-mode tuning |
| 4. barge-in | interruption | state machine (file 02 §4) |

Each step is one file-02 mechanism — the demo is the *substrate* for
them, not a dead end. Ship step 1 in the demo; steps 2–4 are stretch
rows in the capstone's future-work section.

## Exercises

1. Build the demo; run 10 queries; produce the latency table; name the
   stage that eats the budget (it is usually the agent — your W10
   numbers, now in a voice context).
2. Tap-filter drill: what happens with a 0.3 s tap? Verify the minimum-
   length guard and log the rejection.
3. Session drill: two queries in one episode ("what is the margin?" →
   "and on which chart?"); confirm the pronoun resolves — voice sessions
   inherit the text path's memory.

## Pitfalls

- Sample-rate mismatch between capture and STT — 44.1 kHz capture into a
  16 kHz model silently garbles; assert the rate at the boundary.
- Blocking TTS playback inside the agent loop — the next query queues
  behind the audio; play asynchronously (or accept it, in push-to-talk).
- Demo without the latency table — the budget is the engineering
  content; the talking is the garnish.

## Resources

- `sounddevice` docs (streaming capture); your W10 agent (`Runner.run_sync`).
- [`../01-cascade-stack.md`](../01-cascade-stack.md) — the budget table
  this demo fills with real numbers.