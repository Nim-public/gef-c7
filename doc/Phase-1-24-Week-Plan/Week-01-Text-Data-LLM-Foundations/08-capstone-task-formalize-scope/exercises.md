# Exercises — Capstone Task: Formalize Scope

> Subfolder index: [README.md](README.md) · Parent: [../08-capstone-task-formalize-scope.md](../08-capstone-task-formalize-scope.md)

Labs that turn the scope from a document into evidence. All labs feed the final `capstone-scope.md` deliverable.

---

## E1 — The wish-list converter (file 01)

1. Take 3 vague project ideas ("AI for HR", "chatbot for our docs", "automate support") and convert each into the full scope template — user, cost, capability, data, metric, non-goals.
2. Compare your three conversions: which sections were hardest to make concrete? That difficulty is a signal about the idea, not about you.

**Worked approach:** the hardest section is usually *data* — if you can't fill it in 20 minutes, the idea needs a different data strategy (file 02).

## E2 — Data-room build (file 02)

1. Assemble the data room: every source in one folder tree with a manifest (W7-01) — sources, counts, licenses, PII class per field.
2. Run the §1 table against the data room: every row verified against an actual artifact (file in hand, schema readable).
3. PII census: run the scrubber over a 20-record sample; produce the per-field sensitivity table (file 02 §3) — none/low/medium/high per field, with the handling decision.

**Worked approach:** the census output is the PII row of your scope — "emails: medium → masked at ingest" beats "contains PII".

## E3 — Feasibility evidence pack (file 03)

1. Run all 7 checks; build `feasibility.md` — one row per check: experiment, result, artifact link, date.
2. For each failed check: write the mitigation (switch source / change scope / add mitigation) and the *new* experiment that validates it.
3. Go/no-go memo: the §4 decision block filled with your triggers — signed off by a peer before the mentor session.

**Worked approach:** the peer sign-off on no-go triggers is the cheapest insurance in the program — a second pair of eyes catches the trigger you wrote to never fire.

## E4 — Pitch pressure-test (file 03)

1. Build the 5 slides; rehearse twice solo, once with a peer as hostile reviewer.
2. Collect every question asked; classify: answerable-now / needs-work / out-of-scope. For needs-work: the fix and the slide it belongs on.
3. Revise the pitch; re-rehearse. Target: no question in the first 3 minutes you can't answer with a number or a diagram.

**Worked approach:** the hostile-reviewer round surfaces the questions mentors ask — capturing them *before* the session is the difference between a pitch and a conversation.

## Self-assessment

- Can you fill the entire scope template for your project without a single "TBD"?
- Can you state your data volume per pipeline stage, with counts?
- Can you name your no-go triggers from memory — and the evidence behind your GO?
