# Dataset Versioning — Immutable, Changelog, Held-Out Slices

**What you'll learn:** the eval set's governance: immutable versions
(never edited in place), a changelog with reasons, and held-out slices
that stay held out — the dataset as a versioned artifact like code.

## 1. The version model

```text
eval-sets/
  v1/  cases.parquet   changelog.md   (frozen)
  v2/  cases.parquet   changelog.md   (frozen)
  v3/  cases.parquet   changelog.md   (current)
```

| Rule | Why |
|---|---|
| versions are immutable | scores are only comparable within a version |
| additions are additive-only | breaking changes = a new major version |
| every bump has a changelog entry with reasons | the set's history is auditable |
| held-out slices exist per version | leakage control |

The W11 baseline rule (baselines move via accepted runs) applied to the
dataset itself: the set is *frozen* per version; improvements are new
versions.

## 2. The changelog entry (the bump's contract)

```markdown
## v2 → v3 (2026-09-05)
Added:
- 3 mined cases from failure class "chart-ocr-missing" (W14-04-03)
- 1 ambiguous-case family (clarification accepted)
Changed:
- case 10's gold corrected (SQL re-verified; the old gold was wrong)
Removed:
- case 7 (duplicate of case 12, discovered in the parity audit)
Held-out delta: 2 of the 4 new cases reserved for the held-out slice.
```

| Entry type | Requires |
|---|---|
| added | the motivating artifact (failure cluster, gap ticket) |
| changed | the re-verification evidence |
| removed | the discovery (dup audit, leakage check) |

The changelog is the dataset's git log — every case's provenance from
creation to retirement. The W14 self-improving loop writes its rows
here automatically.

## 3. Held-out slices (the leakage control)

| Slice | Size | Rule |
|---|---|---|
| dev slice | ~70% | prompts may be tuned on it |
| held-out slice | ~30% | touched only at eval time |
| rotation | per major version | held-out cases rotate in |

```python
def split_heldout(df: pd.DataFrame, seed: int = 42, frac: float = 0.3):
    rng = np.random.default_rng(seed)
    mask = rng.random(len(df)) < frac
    return df[~mask], df[mask]        # dev, held-out
```

The held-out slice is the honesty reserve: prompts and few-shot examples
may be tuned on the dev slice; the held-out slice is touched only at
eval time — and its rotation (per major version) prevents the held-out
set from becoming dev through repetition.

## 5. The dataset's governance page (the version model as a document)

```markdown
# Eval dataset governance (W16)
- location: eval-sets/vN/ (parquet + changelog.md per version)
- immutability: frozen versions; improvements = new versions
- splits: dev ~70% / held-out ~30%, stratified by class, seed recorded
- provenance: every case cites its motivating artifact
- review: the changelog is reviewed like code (PRs touch the set)
- leakage checks: dedup audit + held-out rotation per major version
```

The governance page is the dataset's constitution — the rules that keep
the eval set trustworthy as it grows through the self-improving loop.
It is the W16 answer to "who watches the watchmen": the dataset's own
changelog, splits, and leakage audits.

## Exercises

1. Restructure your eval set into the version model; write the v1
   changelog; commit the freeze.
2. Split drill: create the dev/held-out split; verify no case appears in
   both; the held-out slice's class distribution matches dev's.
3. Bump drill: add two mined cases as a v2 bump with a proper changelog;
   re-run the harness on both versions — the scores differ, the
   changelog explains why.
4. Governance drill: run the §5 page's checks (dedup, rotation,
   provenance); every check green; the page cites them.