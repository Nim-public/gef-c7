# Exercises — Conversational Bot

> Subfolder index: [README.md](README.md) · Parent: [../06-capstone-task-conversational-bot.md](../06-capstone-task-conversational-bot.md)

Labs that finish the bot. Shared fixture: the W1-05 ticket dataset and the W3-02 injection battery.

---

## E1 — The behavior grid (file 01)

1. Behavior grid: 4 question types × 2 models (base/instruct, W8-04's grid) — complete it for your bot's domain questions.
2. Token accounting: per-turn counts over a 20-turn session — plot the growth; verify the trim.
3. Constitution persistence: constitution adherence at turns 1/10/20 — decay measured, re-anchor interval set.

**Worked approach:** exercise 1's grid is the base-vs-instruct experiment (W8-04) run on YOUR prompts — the results feed the W2-05 model ladder.

## E2 — The battery hardening (files 02/03)

1. Battery expansion: 15 cases (5 happy, 4 boundary, 3 injection, 3 off-domain) — all green or documented.
2. The paraphrase drill: each adversarial case × 3 paraphrases — flakiness measured per phrasing (W23-02's variant problem).
3. Injection regression: every fixed bypass becomes a test; verify the suite catches a deliberate guardrail removal.

**Worked approach:** exercise 2's paraphrase dimension is where prompt-based defenses are weakest — measure before trusting (W23-02 §3's calibration).

## E3 — Translation production (file 02)

1. Both designs on 10 domain questions — term preservation, fluency, and cost table.
2. The glossary sync: domain terms from the W2-06 model README → translation glossary — one source, both consumers.
3. The mixed-language session: 5 turns alternating languages — does the native design hold the language? Does the cascade drift?

**Worked approach:** exercise 3's mixed-language session is the hardest multilingual test — the design that survives it is your production choice.

## E4 — The voice-readiness audit (E5 bridge)

1. Read 10 bot answers aloud — mark unspeakable content (URLs, IDs, code, tables).
2. Rewrite 5 answers for voice (≤2 sentences, spelled-out numbers) — the voice constitution variant.
3. Measure: TTS time per answer variant — the latency cost of the voice rewrite.

**Worked approach:** exercise 2's voice rewrite is the W11-04 voice constitution in miniature — the same discipline, started now.

## Self-assessment

- Can you state the bot's contract (input/output/error/failure paths) without opening the code?
- Can you add a new adversarial case to the battery and have it run in CI in under 2 minutes?
- Can you defend the translation design choice with your measured comparison?
