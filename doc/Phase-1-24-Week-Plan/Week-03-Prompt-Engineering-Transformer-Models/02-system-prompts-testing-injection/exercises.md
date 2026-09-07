# Exercises — System Prompts, Testing & Injection

> Subfolder index: [README.md](README.md) · Parent: [../02-system-prompts-testing-injection.md](../02-system-prompts-testing-injection.md)

Labs for this subfolder. Shared fixture: the W3 bot (constitution + history + tools) and its pytest battery.

---

## E1 — Constitution forensics (file 01)

1. Section-mapping audit: map every line of your constitution to a failure it prevents; delete the unmapped lines; verify the battery still passes.
2. Deletion drill: remove one section; identify which battery cases now fail — the section's measured value.
3. Budget compression: ≤150 tokens without losing a passing case; document what you cut and why it was safe.

**Worked approach:** the deletion drill is the constitution's proof-of-work — every surviving line has a failing test that justifies it.

## E2 — Multi-turn engineering (file 02)

1. Drift measurement: adherence decay over 30 turns (W3-02 §2's exercise, quantified); find the re-anchor interval.
2. Summarization audit: what the recap loses, classified acceptable/unacceptable; the re-injection list updated.
3. The budget allocator test: oversized few-shot block vs the allocator — verify the system/question/priority sections survive.

**Worked approach:** exercise 1's decay curve is the re-anchor interval's evidence — measure it on your constitution, not a generic one.

## E3 — The test pyramid (file 03)

1. Pyramid conversion: 5 manual checks → 3 unit (stubbed) + 2 contract; runtime before/after.
2. The replay client: 20 recorded responses; verify replay parity with live outputs on the same seeds.
3. The CI gate: prompts changed → gates run → planted regression blocked → fix verified (W15-02's hosted dataset or local pytest).

**Worked approach:** exercise 2's replay parity check validates the stubbing boundary — if replayed and live differ, the stub is testing fiction.

## E4 — Injection defense certification (file 04)

1. Surface map + layer-bypass suite: the full matrix (file 04 §1/§3) run against your agent; per-family results.
2. The combo attack: document-embedded + multi-turn + valid-tool-call chain — does any layer catch the assembled attack?
3. Residual-risk documentation: every bypass classified (fix/ticket/accept) with the accepted-risk entries written.

**Worked approach:** exercise 2's combo attack is the real threat model — individual-layer tests pass while the assembled attack succeeds; the drill exposes the composition gap.

## Self-assessment

- Can you state which constitution section prevents which failure — with the test that proves it?
- Can you implement the three history operations and predict what each loses?
- Can your agent survive the five-family injection battery with a documented residual-risk list?
