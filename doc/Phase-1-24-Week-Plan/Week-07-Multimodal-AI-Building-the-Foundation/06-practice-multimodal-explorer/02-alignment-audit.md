# Alignment Audit — Validation Report Generation

**What you'll learn:** Part B as a build guide: turn the validation catalog
into a one-command audit that produces the three reports from the alignment
pipeline and fails loudly when the corpus is not demo-safe.

## 1. The audit is a wrapper, not new logic

Everything was built in the alignment subfolder (checks V1–V8, policies,
stages). The audit script is the *composition* the rubric grades:

```python
# scripts/audit_alignment.py
from pathlib import Path
import pandas as pd
from align_corpus import build_manifest, build_alignment, load_policies
from validate import validate, gate

def audit(data_root: str = "data", out: str = "reports") -> int:
    manifest = build_manifest(Path(data_root) / "raw")
    align = build_alignment(manifest, Path(data_root) / "raw")
    rep = validate(manifest, None,
                   Path(data_root) / "processed/video-keyframes",
                   load_settings())
    rep = apply_policies_to_report(rep, load_policies())
    write_reports(rep, manifest, align, Path(out))
    return gate(rep)

if __name__ == "__main__":
    raise SystemExit(audit())
```

Exit code is the interface: `0` demo-safe, `1` errors present. CI and your
future self need nothing else.

## 2. What each report must contain (rubric mapping)

| Report | Required content | Rubric criterion |
|---|---|---|
| `validation-report.md` | V1–V8 × severity × count, gate line | "automated, not vibes" |
| `alignment-report.md` | per-video offsets + sources + coverage % | clock provenance |
| `missing-data-report.md` | drops/flags/imputations with receipts | policy discipline |

A report missing its header (manifest version, timestamp) fails the audit —
the header check is one `assert` in `write_reports`.

## 3. The audit as a pre-demo ritual

```text
demo checklist (runs in <1 min):
  1. py scripts/audit_alignment.py          → exit 0
  2. open reports/validation-report.md      → zero error rows
  3. open reports/missing-data-report.md    → every flag has an owner/due
  4. explorer "random sample" tab, 3 clicks → nothing sideways/black
```

Step 4 is deliberate: automated checks catch shape bugs, humans catch
semantic ones. The explorer from file 01 is the human half of the audit.

## 4. Audit on a fresh clone (the portability test)

The audit's real value shows on a teammate's machine:

```powershell
git clone https://github.com/<you>/gef-c7 ; cd gef-c7
py -m venv .venv ; .\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py scripts/audit_alignment.py      # → 1: data/ is gitignored (expected)
```

The expected result is **exit 1 with "manifest not found"** — the audit must
*say so* rather than crash in stage 3. Then `py scripts/ingest.py --demo-corpus`
builds the small demo corpus from the manifest-of-manifests (your inventory),
and the audit passes on the rebuilt data. This loop — audit, rebuild, audit —
is the workflow every later week assumes.

## Exercises

1. Add `--format json` to the audit (machine-readable for CI badges) and
   keep markdown for humans — one writer function, two renderers.
2. Make the audit fail when `reports/` contains stale-version artifacts
   (alignment parquet version > report header version) — the rot check.
3. Run the fresh-clone loop above on a clean directory; time it. If > 5 min,
   document which stage is slow and whether it can be cached.

## Pitfalls

- Audit that passes with zero units — an empty manifest gates *green*; add the trivial but crucial "corpus non-empty" check.
- Reports regenerated with the *old* manifest version after a schema bump — the header assert catches it only if versions are actually bumped.
- Checklist steps 1–3 automated but step 4 skipped forever — the ritual exists because eyes catch what hashes cannot.

## Resources

- Your validation catalog: [`../04-data-alignment-synchronization/02-cross-modal-validation.md`](../04-data-alignment-synchronization/02-cross-modal-validation.md).
- Exit-code conventions for CI gates.
