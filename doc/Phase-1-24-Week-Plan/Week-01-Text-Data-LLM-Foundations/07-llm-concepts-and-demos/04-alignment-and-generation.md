# 07.4 — Alignment & the Generation Loop

> Subfolder index: [README.md](README.md) · Parent: [../07-llm-concepts-and-demos.md](../07-llm-concepts-and-demos.md)

---

## What you'll learn

- The autoregressive generation loop made visible — with streaming
- Where pre-training, SFT, and RLHF each show up in behavior
- The stop condition machinery (EOS, stop sequences, finish reasons)

## 1. The loop, made visible with streaming

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini", stream=True,
    messages=[{"role": "user", "content": "Count from 1 to 10."}])

for chunk in stream:
    delta = chunk.choices[0].delta.content
    finish = chunk.choices[0].finish_reason
    if delta: print(delta, end="", flush=True)
    if finish: print(f"\n[finish: {finish}]")
```

Each chunk is one step of the loop: the model produced a distribution, sampled one token, appended it, repeated. The `[finish: stop]` marker at the end is the EOS decision (W1-01's special token) surfacing through the API.

## 2. Where each alignment stage shows up in behavior

| Stage | What it installed | How you observe it |
|---|---|---|
| **Pre-training** | language fluency, world knowledge | base model autocomplete (W8-04's lab) |
| **SFT** | the assistant *format* — answers, not continuations | instruct model stops and answers |
| **RLHF / preference tuning** | helpfulness calibration, refusals, hedging | refusal phrasing, "as an AI" framing, tone |

The observable signatures (test them in file 04's grid): the base model never refuses (no refusal training); the instruct model hedges under uncertainty (calibration training); the instruct model formats lists/JSON on request (SFT format compliance). None of these come from pre-training alone.

## 3. The stop machinery

| Mechanism | Level | Example |
|---|---|---|
| EOS token | model behavior | the trained `<|im_end|>` emission |
| `stop` sequences | API | `stop=["\n\n"]` cuts at a blank line |
| `max_completion_tokens` | API hard cap | `finish_reason="length"` |
| your own check | application | parse the partial, decide |

Design rule: rely on EOS for natural endings, `stop` sequences for structural boundaries (e.g., cutting before an agent's `Observation:` block — W10-05), and `max_completion_tokens` as the hard ceiling. All three compose.

## 4. Streaming in production (W11-04's integration)

- **First-token latency** is what users feel — streaming hides the full generation time behind progressive output
- **Citation handling while streaming** — buffer until you can validate the citation markers, then flush (W5-04's output guards on a stream)
- **Cancellation** — a user navigating away should cancel the in-flight request (`stream.close()`); otherwise you pay for tokens nobody reads
- **Reconnection** — mid-stream disconnects need either resend-with-context or a resumable session (W13-06's checkpoints, API edition)

## Exercises

1. Loop visualization: stream a 200-token answer; count chunks vs tokens — are they 1:1? (Usually not — chunks can be multi-token; characterize the chunking.)
2. Stop-sequence lab: generate an interview transcript with `stop=["\nInterviewer:"]` — verify the cut is clean and before the marker.
3. Alignment observation: ask 5 questions that a base model answers badly (from file 04's grid) — show the instruct model's SFT and refusal behaviors on the same prompts.
4. Streaming cost check: does streaming change `usage`? (Compare streamed vs non-streamed on identical prompts.) Any difference matters for the E8-03 ledger.
5. Cancellation drill: close the stream mid-generation; verify no charge for ungenerated tokens (check usage) and the connection state.

## Pitfalls

- **Building UI on `delta.content` without None-checks** — role/setup chunks have no content; guard every access
- **Assuming chunks are whole tokens** — they're whatever the transport delivers; buffer and split on your own boundaries
- **Streaming past the stop sequence** — the API stops *before* emitting the stop string in most cases, but verify per provider
- **Forgetting `stream_options={"include_usage": true}`** — usage arrives only in the final chunk when requested; without it, streaming calls cost-tracking blind (E8-03)
- **Cancellation leaks** — an unclosed stream keeps the connection and billing alive

## Resources

- OpenAI [streaming responses docs](https://platform.openai.com/docs/api-reference/streaming) — chunk shapes, `stream_options`
- W1-07 (parent), W8-04 (base behavior), W13-06 (resumable state) — composed here
- [Server-sent events primer](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) — the transport under streaming
