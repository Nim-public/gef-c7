# Corpus Prep — Manifests, Captions, Crops

**What you'll learn:** the practice deliverable's stage 1: bring your own
corpus through the full prep path — manifest, captions with versioning,
crops with provenance — and the audit ritual that gates it.

## 1. The prep pipeline, assembled

```text
data/raw/ ──▶ build_manifest (W7) ──▶ validate (W7 gate)
          ──▶ captions (W8 BLIP, versioned) ──▶ crops (charts only)
          ──▶ ingest_multimodal (W9-04) ──▶ audit reports (W7-06 ritual)
```

Every stage exists from prior weeks; prep is their composition *on your
corpus*. The only new work is deciding, per unit, which sidecars apply:

| Unit type | Caption? | OCR? | Crops? |
|---|---|---|---|
| Photo | yes | no | no |
| Chart/screenshot | yes | yes | yes |
| Scanned page | no | yes | no |
| Text chunk | — | — | — |

## 2. The decision table as code

```python
def prep_unit(row) -> dict:
    kind = classify_unit(row)          # photo|chart|scan|text
    return {
        "caption": blip_caption(row.rel_path) if kind in ("photo", "chart") else "",
        "ocr": ocr_text(row.rel_path) if kind in ("chart", "scan") else "",
        "crops": region_crops(row.rel_path) if kind == "chart" else [],
    }
```

`classify_unit` starts rule-based (filename hints, OCR hit-rate, image
stats) and logs its decisions — misclassifications surface in the audit
and tune the rules, not the pipeline.

## 3. The audit ritual, adapted

```text
1. py scripts/build_manifest.py --report       → coverage table
2. py scripts/validate_corpus.py               → gate: errors == 0
3. py scripts/audit_alignment.py               → sidecar coverage per class
4. explorer "random sample" ×3                 → eyes on 12 units
```

Step 3's addition this week: the missing-data report now includes *sidecar
coverage per unit class* — charts without OCR are the number to drive to
zero before indexing.

## 4. The classification table, worked end-to-end

A concrete 12-unit example — the table your prep run produces:

| unit_id | kind | caption? | ocr? | crops? | sidecar_status |
|---|---|---|---|---|---|
| u001 | photo | ✓ | — | — | ready |
| u002 | chart | ✓ | ✓ | ✓(4) | ready |
| u003 | scan | — | ✓ | — | ready |
| u004 | text | — | — | — | n/a |
| u005 | photo | ✓ | — | — | ready |
| u006 | chart | ✓ | ✗ | ✗ | **blocked: no OCR** |

The audit's headline number: charts-without-OCR (u006) must reach zero —
either the OCR run completes or the unit is flagged out of the served
corpus. One blocked chart unit silently poisons every chart query it
would have answered.

```python
def coverage_report(df) -> dict:
    per_class = df[df.kind == "chart"]
    return {"charts": len(per_class),
            "with_ocr": int(per_class.sidecar_status.eq("ready").sum())}
```

## 5. Prep costs — the runbook numbers

| Stage | Time (2k units) | Re-runs when |
|---|---|---|
| manifest build | ~40 s | corpus files change |
| captions (photos+charts) | ~25 min CPU | captioner version bump |
| OCR (charts+scans) | ~6 min | OCR engine change |
| crops (charts) | ~2 min | crop strategy change |
| ingest to LanceDB | ~2 min | any of the above |
| audit + gate | ~1 min | always (every prep) |

```python
# every stage logs its own duration — the runbook writes itself:
log.info("stage=%s units=%d sec=%.0f", "captions", n, dt)
```

The runbook turns "prep takes a while" into a schedulable job: full prep
is a ~40-minute overnight run; targeted re-runs (caption bump) are
minutes. Budget honestly in the capstone plan.

## Exercises

1. Run the full prep on your corpus; fill the sidecar-coverage table per
   unit class; drive chart-without-OCR to zero or flag the stragglers.
2. Misclassification hunt: sample 10 classified units; verify class
   labels; fix one rule and re-run — the loop that tunes `classify_unit`.
3. Version drill: bump `caption_version` for photos only; verify only
   photo rows re-embed — and record the measured re-run cost against the
   runbook table.

## Pitfalls

- OCR on photos (wasted seconds, noisy sidecar text) — the class decision
  table exists to prevent exactly this.
- Crops on scans — crop provenance assumes clean layout; scans go
  page-level.
- Prep without the audit — every prior week's lesson says: no numbers, no
  trust.

## Resources

- W7 files 01/04/06 (manifest, alignment, explorer); W8 file 03 (BLIP).
- Your unit-class table — the prep script's configuration.
