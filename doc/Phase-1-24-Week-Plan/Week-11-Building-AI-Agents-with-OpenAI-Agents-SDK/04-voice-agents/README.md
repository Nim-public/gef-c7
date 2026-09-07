# Deep-Dive: Voice Agents

Parent overview: [`../04-voice-agents.md`](../04-voice-agents.md)

Voice is a *latency* problem wearing an audio costume. This subfolder
builds the cascade stack (STT → agent → TTS) with a per-stage budget,
turn-taking mechanics, a minimal push-to-talk demo, and the
realtime-vs-cascade decision with real numbers.

## File map

| File | What it covers |
|---|---|
| [`01-cascade-stack.md`](01-cascade-stack.md) | STT → agent → TTS, per-stage budgets |
| [`02-turn-taking.md`](02-turn-taking.md) | VAD, endpointing, barge-in |
| [`03-push-to-talk-demo.md`](03-push-to-talk-demo.md) | The minimal working demo |
| [`04-realtime-vs-cascade.md`](04-realtime-vs-cascade.md) | Decision and costs |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-cascade-stack.md` — the budget that makes voice feel alive.
2. `02-turn-taking.md` — the hard part isn't the models.
3. `03-push-to-talk-demo.md` — ship something that works.
4. `04-realtime-vs-cascade.md` — decide with numbers.

## Prerequisites

- [`../../Week-08-Encoding-Modalities-Real-World-Architectures/02-encoding-audio-video/02-raw-audio-encoders.md`](../../Week-08-Encoding-Modalities-Real-World-Architectures/02-encoding-audio-video/02-raw-audio-encoders.md)
  — the 16 kHz mono contract.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/01-agent-assembly.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/06-practice-first-mcp-agent/01-agent-assembly.md)
  — the agent behind the voice.
