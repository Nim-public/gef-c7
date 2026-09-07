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

## 4. The adopt decision's maintenance column (the standing cost)

| Adopted component | Standing cost |
|---|---|
| node parser | version pin + chunk-parity test |
| readers | format-coverage tests per reader |
| query engine (if shipped) | harness adapters + full parity |

The maintenance column is the adopt decision's honest cost — a store
that only filters is still useful but must be documented as such in the
architecture section. The W14-06 gate inventory grows by the adopted
component's tests; the memo states the growth.

## 5. The decision drills (the memo's evidence)

1. Run the comparison (file 03); write the verdict memo with cited
   numbers; commit as the capstone's retrieval decision.
2. Reversibility drill: the adopted component must be removable — a flag
   or an adapter boundary; verify by disabling it and re-running the
   eval.
3. Revisit drill: name the trigger that would flip adopt → ship (or
   reject); the trigger is measurable.
4. Provenance drill: every memo number links to the comparison report;
   the walk-through takes a reviewer under five minutes.
5. Appendix drill: build §7's evidence appendix; a reviewer clicks two
   claims at random — both resolve.

## 6. The verdict's evidence appendix (the memo's audit trail)

| Memo claim | Evidence artifact |
|---|---|
| retrieval parity | the comparison report (file 03) |
| readers save time | the ingestion timing from file 01 |
| adopt cost | the maintenance column (§4) |
| revisit triggers | the standing trigger list |

The appendix is the memo's audit trail — four claims, four artifacts.
The W11 framework-verdict format, applied to a component decision: the
reviewer clicks and verifies, no vibes.

## 7. The adopt decision's maintenance column (the standing cost)

| Adopted component | Standing cost |
|---|---|
| node parser | version pin + chunk-parity test |
| readers | format-coverage tests per reader |
| query engine (if shipped) | harness adapters + full parity |

The maintenance column is the adopt decision's honest cost — an adopted
component joins the pin notes, the parity tests, and the upgrade
schedule. The W14-06 gate inventory grows by the adopted component's
tests; the memo states the growth.

## Pitfalls

- Comparing implementations on different corpus/config versions — the
  protocol header exists to prevent it.
- n=10 conclusions about "better" — the table verifies the port;
  statistical claims need the full eval set and repeats.
- Hiding the W9-win rows — honest tables build trust in the verdict;
  the memo reads them as fitter evidence.
- Adoption without reversibility — the drill is the exit; adoption
  without an exit is a trap.