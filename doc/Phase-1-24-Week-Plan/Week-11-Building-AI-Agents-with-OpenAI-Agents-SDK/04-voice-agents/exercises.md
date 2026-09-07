# Exercises — Voice Agents

Expanded set with worked approaches. The deliverable: the push-to-talk
demo with a measured latency table, turn-taking mechanics rehearsed, and
the cascade-vs-realtime decision recorded.

## 1. Cascade built and measured (from 01-cascade-stack)

**Task:** wire the three stages around your W10 agent; produce the
per-stage latency table over 10 queries; name the budget-eating stage.

**Worked approach:** the table is the deliverable — the numbers replace
the file's ballparks. Expect the agent stage to dominate (it was already
1.5 s in text) and STT/TTS to be functions of audio length.

**Pass criterion:** 10-row table committed (`reports/voice-latency.md`);
the eating stage named with its share.

## 2. First-sentence streaming drill (from 01)

**Task:** implement sentence-boundary streaming into TTS (split the
typed answer at sentence ends); measure time-to-first-audio vs
whole-answer TTS.

**Worked approach:** the typed `Answer` makes the split trivial (the
answer string arrives before citations); the delta usually lands at
30–50% of perceived latency — the single cheapest voice win available.

**Pass criterion:** both timings measured; the delta in the table; the
streaming path is now the default.

## 3. Endpointing tuning (from 02-turn-taking)

**Task:** record 10 queries with deliberate thinking pauses; find your
silence threshold (never-truncates, never-dawdles); then run the
barge-in drill (speak over TTS; cancel <300 ms).

**Worked approach:** the threshold is personal and room-dependent —
measure on your demo setup and record it with the audio samples'
characteristics. The barge-in drill validates the state machine's
SPEAKING→LISTENING guard.

**Pass criterion:** your endpoint number recorded; cancellation latency
<300 ms on 8/10 attempts.

## 4. The decision memo (from 04-realtime-vs-cascade)

**Task:** run the decision procedure with your ledger numbers; append
the verdict to `doc/capstone/agentic-boundary.md` (the voice clause).

**Worked approach:** the verdict cites §2's cost table with your agent
cost filled in, plus the grounding argument. The revisit trigger: a
product requirement for sub-second open-domain conversation.

**Pass criterion:** memo updated; the seam inventory (what survives a
realtime swap) listed.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Cascade built; per-stage table | reports/voice-latency.md | 4 |
| First-sentence streaming default | timing delta | 3 |
| Endpointing + barge-in rehearsed | drill numbers | 3 |
| Decision memo with your costs | boundary memo | 3 |
| Text path works with voice dead | failure drill | 3 |

**Pass bar:** 13/16 to proceed to file 05 (observability). The latency
table (4-pointer) is the voice week's real artifact — the talking is
context.

## 6. The voice fallback ladder

**Task:** implement graceful degradation for the voice path: STT down →
text-only prompt in the UI; agent down → cached last answer + banner;
TTS down → text response. Each with a drilled test.

**Worked approach:** the ladder is the W8 fusion degradation matrix,
voice edition — each rung has one kill-switch test. The demo should
*never* hard-fail because one audio stage did.

**Pass criterion:** three rungs drilled; the demo degrades with a
visible banner; the latency table gains a "degraded mode" column.

## 7. The demo script for review day

**Task:** write `scripts/voice_review.py`: 5 scripted queries through the
full voice path, printing the latency table line per query and the
transcript — the artifact the capstone review plays.

**Worked approach:** the script is the deterministic version of the demo
— no live typing, seeded queries, the table as evidence. It doubles as
the regression test for the voice path.

**Pass criterion:** one command runs the whole review; the table's
totals stay within the budget; transcript artifacts land in `reports/`.

## Pitfalls recap

- Voice demo without the latency table — a party trick; the budget is
  the engineering.
- Sample-rate mismatches at stage boundaries — assert 16 kHz mono at
  every seam (the W8 contract, still load-bearing).
- Voice built as the core instead of a garnish — the text path must
  survive the voice path's death; the failure drill proves it.