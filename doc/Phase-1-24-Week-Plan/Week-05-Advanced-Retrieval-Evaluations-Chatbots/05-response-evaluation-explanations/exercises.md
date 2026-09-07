# Exercises — Ragas & Explanations

> Subfolder index: [README.md](README.md) · Parent topic: [../05-response-evaluation-explanations.md](../05-response-evaluation-explanations.md)

Labs for this subfolder.

---

## E1 — The Ragas pipeline (file 01)

1. Build the 30-case eval from production logs; run all four metrics; produce the slice table.
2. The diagnosis drill: the lowest metric → the mapped fix → the re-run — the before/after delta.
3. The dilution test: faithfulness at k ∈ {3, 5, 10, 20} — the curve that justifies your k selection.

**Worked approach:** exercise 2's before/after is the improvement-evidence pattern — the delta is what makes the change defensible.

## E2 — The explanation audit (file 01)

1. Implement the three explanation levels (citations, transparency, self-check); test on 10 answers.
2. The user study: show 5 answers with different explanation levels to a peer; which level builds the most trust?
3. The explanation consistency: the same question at T=0 produces the same explanation across runs? (Or is the explanation also nondeterministic?)

## Self-assessment

- Can you name the four Ragas metrics and the pipeline stage each diagnoses?
- Can you produce a before/after improvement with measured deltas?
- Can you implement explanation levels and test their consistency?
