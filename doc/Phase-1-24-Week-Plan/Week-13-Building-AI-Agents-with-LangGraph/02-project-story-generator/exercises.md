# Exercises — Story Generator

Expanded set with worked approaches. The deliverable: a playable
three-chapter story with structured choices, crashes that heal, and the
pattern extracted for reuse.

## 1. The story graph (from 01-story-state)

**Task:** build the state + generate/apply nodes; run three chapters;
verify world-JSON coherence across chapters (validator clean).

**Worked approach:** the world-whole-rewrite is the coherence move —
the validator (no duplicate characters, threads tracked) runs per
generation; three clean chapters is the pass bar.

**Pass criterion:** 3 chapters, validator green each time, options
2–4 every turn.

## 2. Pause + resume (from 02-wait-pattern)

**Task:** wire the interrupt; run to pause; resume with a choice; then
the crash drill — kill mid-story, resume in a new process.

**Worked approach:** the crash drill is the durability proof — the
checkpointer holds the story, the thread_id is its identity. A killed
process resuming mid-sentence is the whole argument for structural
persistence.

**Pass criterion:** pause → choice → resume works; the crash drill
restores the same story state.

## 3. The fallback ladder (from 03-choice-application)

**Task:** implement both application routes; test all four choice types
(listed, free-in-world, world-breaking, incoherent); the last one loops
once then degrades to an open thread.

**Worked approach:** the incoherent case is the fun one — the graph
must not crash on "asdf"; it re-prompts once, then records an open
thread. The counter bound (file 01-03) is the loop breaker.

**Pass criterion:** four choice types handled; the story survives all
of them; the trajectory rows record each choice.

## 4. The pattern extraction (from 04-transferable-pattern)

**Task:** build `interactive_flow(generate_fn, apply_fn, options_fn)`;
rebuild the story with it; write the three capstone-flow candidates
with the pattern's mapping.

**Worked approach:** the builder is the week's real deliverable — the
story was the rehearsal. The candidates (approval, ingestion, query
review) each get a one-paragraph mapping to the four pattern elements.

**Pass criterion:** the builder runs the story as its first instance;
three candidates listed with the chosen one justified.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| 3-chapter story, validator clean | transcript + tests | 3 |
| Crash drill heals | durability test | 4 |
| Four choice types handled | fallback tests | 4 |
| Pattern builder + candidates | builder code + list | 3 |
| Options schema enforced 2–4 | schema test | 2 |

**Pass bar:** 13/16 to proceed to file 03 (the ticket router). The
crash drill (4-pointer) is the WAIT pattern's proof — persistence is
the point of the whole checkpointing arc.

## 6. The story demo script

**Task:** write `scripts/story_demo.py`: seeded story, scripted choices
(the reviewer "plays"), printing chapters + options + world diffs per
turn — one command, three chapters, deterministic with a fixed seed.

**Worked approach:** the demo is the story's evidence artifact: same
discipline as the W9 metrics demo — the artifacts (chapters, world
diffs) land in `reports/story-demo.md`, and the reviewer can replay the
identical run from the seed.

**Pass criterion:** one command produces the three-chapter transcript;
world diffs show the choices taking effect; the run is reproducible.

## 7. The story-gen pin note

**Task:** extend `reports/sdk-versions.md` with the story stack:
LangGraph version, checkpointer backend, interrupt list, and the
crash-drill test command.

**Worked approach:** the story generator is the first durable flow —
the pin note records what the crash drill verified (backend, thread
scheme, resume semantics) so the durability claim has a version.

**Pass criterion:** note committed; the crash drill command green as
recorded.

## Pitfalls recap

- Piecemeal world patches — coherence dies by chapter 4; whole-document
  rewrites with validators.
- UI-held story state — the checkpointer is the story's home; the
  thread_id is its name.
- Incoherent-choice crashes — the fallback ladder keeps players playing;
  the loop cap keeps the graph terminating.