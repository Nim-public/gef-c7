# Exercises — The Six Levers

> Subfolder index: [README.md](README.md) · Parent: [../05-techniques-comparison.md](../05-techniques-comparison.md)

Decision drills — each produces a written artifact that feeds your capstone README and the mentor pitch.

---

## E1 — The lever audit (file 01)

1. Inventory your capstone's components; for each, name the levers pulled (with evidence) and the levers explicitly not pulled (with reasons).
2. Find one component where two levers conflict; resolve with a rule; document.
3. Cost-of-change table: engineering days per lever, per component — the table that drives sprint planning.

**Worked approach:** exercise 2's "not pulled" column is where reviewers probe hardest — unnamed rejections read as ignorance.

## E2 — The decision memos (file 02)

1. Four decision memos (1 page each) in the §-format: options → analysis → decision → evidence → rejected options.
2. Peer review: swap memos; attack each other's weakest rejection; revise.
3. The pivot drill: simulate the data-source change; re-run the affected memos; produce the v2 decisions.

**Worked approach:** the memos are dated and versioned — decisions get re-litigated; the trail keeps the re-litigation short.

## E3 — The trap hunt (file 02 §2)

1. The facts trap: find the exact place in your project where fine-tuning on data would rot — write the scenario, the failure, and the RAG alternative.
2. The style trap: where would prompting plateau and fine-tuning become necessary? Estimate the data volume for the fine-tune.
3. The security-trade drill: which levers *increase* attack surface (agents > pipelines; tools > none)? Document the security cost of each lever you pull.

**Worked approach:** exercise 3 connects the levers to E7 — every lever has a security price as well as an engineering price.

## Self-assessment

- Can you state, for each of the six levers, what it changes and one thing it cannot?
- Can you run the decision procedure (data → capability → style → cost) on a new scenario in 10 minutes?
- Is every lever decision in your capstone backed by a measured experiment or a named rejection?
