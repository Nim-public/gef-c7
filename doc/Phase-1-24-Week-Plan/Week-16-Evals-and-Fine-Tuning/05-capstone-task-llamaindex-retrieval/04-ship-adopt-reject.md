# Ship / Adopt / Reject — The Evidence-Based Decision

**What you'll learn:** the three-way decision for LlamaIndex: *ship* it
(replace your W9 stack), *adopt* it (use its readers/chunkers alongside
your stack), or *reject* it (keep W9 entirely) — each verdict citing
the comparison numbers.

## 1. The three verdicts

| Verdict | Meaning | Evidence that triggers it |
|---|---|---|
| ship | LlamaIndex replaces the W9 retrieval stack | R@K + faithfulness ≥ W9 across all slices |
| adopt | use its readers/node parsers, keep your retrieval | its ingestion wins, retrieval parity |
| reject | keep W9 entirely | no metric advantage at equal cost |

The verdict is per-*component*, not per-framework: adopt the node
parser while rejecting the query engine is a legitimate outcome — the
W10 tool-surface discipline (adopt components, not frameworks) applied.

## 2. The decision memo

```markdown
## LlamaIndex decision (W16)
- Verdict: ADOPT (node parser only)
- Evidence: chunk parity with W4 settings (file 02's pin);
  retrieval R@5 −0.01 vs W9 (within noise); readers save ~2 h of
  ingestion code for new formats
- Rejected: query engine (our synthesizer + citation gate are stricter)
- Revisit: if LlamaIndex's retriever beats W9 on the weak slice
```

The memo is the decision's record — verdict, evidence, rejected parts,
revisit trigger. The same format as the W11 framework verdict; the
discipline is program-wide.

## 3. The cost of adoption (what changes in the codebase)

| Adoption level | Codebase change | Maintenance |
|---|---|---|
| reject | none | none |
| adopt node parser | the ingestion path imports LlamaIndex | one dependency |
| ship | the retrieval path + harness adapters | a second engine to version |

The maintenance column is the decision's real cost — every adopted
component joins the pin notes, the parity tests, and the upgrade
schedule. The W14-06 gate inventory grows by the adopted component's
tests.

## Exercises

1. Run the comparison (file 03); write the verdict memo with cited
   numbers; commit as the capstone's retrieval decision.
2. Reversibility drill: the adopted component must be removable — a flag
   or an adapter boundary; verify by disabling it and re-running the
   eval.
3. Revisit drill: name the trigger that would flip adopt → ship (or
   reject); the trigger is measurable.