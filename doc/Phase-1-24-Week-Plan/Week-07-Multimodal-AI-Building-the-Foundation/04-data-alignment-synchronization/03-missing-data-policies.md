# Missing Data Policies — Drop / Impute / Flag Decision Tables

**What you'll learn:** real corpora have holes: no EXIF, no subtitles, corrupt
frames, silent audio. Decide per hole type *before* it happens, encode the
decision as data, and stop ad-hoc `if pd.isna(...)` sprawl.

## 1. The policy table (your corpus's constitution)

| Hole type | Default policy | Why | Encoded as |
|---|---|---|---|
| Missing EXIF timestamp | **flag** (`captured_at=""`), keep unit | timestamp rarely affects retrieval | manifest column stays empty |
| Missing hash | **error** — refuse ingest | identity is not optional | validation V1 |
| Corrupt image (undecodable) | **drop**, log to quarantine | can't process, can't index | `data/manifests/excluded.parquet` |
| Corrupt audio (decodable but noisy) | **flag** (`notes+="audio:low-snr"`), keep | ASR may still extract value | notes + warning |
| Missing subtitles | **flag**, plan ASR (Week 08) | text sidecar pending, not absent | `sidecar_status="pending"` |
| Missing OCR (scanned page) | **drop from text index, keep image unit** | image embeddings still work | per-index allow-list |
| Video with 0 keyframes | **re-sample uniformly**, flag | keyframe strategy failed | settings override + notes |
| Empty text after cleaning | **drop** for text index | empty vectors are noise | per-index allow-list |
| Unknown license | **drop** from published corpus | legal default is exclusion | permissions file 03 |

Three verbs, in strict precedence: **drop** (unit never enters an index),
**flag** (unit enters, marked — downstream decides), **impute** (fill a
derived value and *record the imputation source*). Impute is rare: timestamps
from filename, duration from container. Never impute *content*.

## 2. Encoding policies as data, not code

```python
# data/manifests/policies.json — committed, versioned
{
  "version": 2,
  "rules": [
    {"when": {"field": "captured_at", "op": "missing"}, "then": "flag",
     "note": "timestamp optional for retrieval"},
    {"when": {"field": "sha256", "op": "missing"}, "then": "error"},
    {"when": {"field": "license", "op": "not_in", "values": ["CC0-1.0", "CC-BY-4.0", "UNLICENSED"]},
     "then": "drop", "target": "published"},
    {"when": {"field": "modality", "op": "eq", "values": ["video"],
              "and": {"field": "n_keyframes", "op": "eq", "values": [0]}},
     "then": "resample_uniform", "note": "settings.video.strategy=uniform"}
  ]
}
```

The evaluator is 30 lines; the point is the *artifact*: policies survive
team turnover because they are a file, not a memory.

```python
def apply_policies(df: pd.DataFrame, rules: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    flags, drops = [], []
    for rule in rules:
        mask = _matches(df, rule["when"])
        act = rule["then"]
        if act == "flag":
            flags.extend(df.loc[mask, "unit_id"])
        elif act == "drop" and rule.get("target") == "published":
            drops.extend(df.loc[mask, "unit_id"])
        elif act == "error":
            assert not mask.any(), f"policy error: {rule['when']}"
    return df, pd.DataFrame({"unit_id": sorted(set(drops))})
```

## 3. Flag vs drop: the published/local split

The capstone has two consumers of the manifest:

- **Local pipeline** (your dev runs): permissive — flagged units included.
- **Published corpus/index** (what you share or demo): strict — dropped
  units excluded, flags re-reviewed.

```python
def published_view(manifest: pd.DataFrame, policies: pd.DataFrame) -> pd.DataFrame:
    drop_ids = set(policies.unit_id)
    strict = manifest[~manifest.unit_id.isin(drop_ids)]
    return strict[strict.license.isin(ALLOWED)].reset_index(drop=True)
```

One manifest, two views, zero ambiguity about what a demo is showing. The
classic failure this prevents: a demo retrieves a unit whose OCR text was
imputed from a *different* page because the flag was never reviewed.

## 4. Imputation with receipts

```python
def impute_captured_at(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing EXIF timestamps from filename patterns; record source."""
    import re
    pat = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
    def from_name(name: str) -> str:
        m = pat.search(name)
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T00:00:00" if m else ""
    need = df.captured_at == ""
    guess = df.loc[need, "rel_path"].map(lambda p: from_name(Path(p).name))
    df.loc[need, "captured_at"] = guess
    df.loc[need, "notes"] += " |imputed:captured_at=from_filename"
    return df
```

The `|imputed:` receipt in `notes` is the whole exercise: an imputed value
that cannot be distinguished from a measured one is a lie in your data.

## 5. The three questions before any policy decision

1. **Is this hole about identity, content, or metadata?** Identity holes
   (hash, id) → error. Content holes → drop for the affected index. Metadata
   holes → flag.
2. **Can it be regenerated later?** Sidecars pending Week 08 → flag with
   `sidecar_status="pending"`, not drop.
3. **Who consumes the unit?** Published index (strict) vs local pipeline
   (permissive) — the answer changes the verb.

## Exercises

1. Write `_matches(df, when)` for the four ops above and unit-test each with
   a 5-row fixture (one row per op outcome).
2. Run `impute_captured_at` on a manifest with 3 missing timestamps; show the
   before/after diffs and confirm receipts appear in `notes`.
3. Your demo must exclude imputed timestamps. Write the filter from the
   receipts (`notes.str.contains("|imputed:", regex=False)`) and count the
   affected units.

## Pitfalls

- Policies that exist only in a Slack thread — encode as JSON or they will be re-litigated weekly.
- `df.notes += ...` silently NaN-ing empty notes — initialize `notes` to `""` at manifest build.
- Dropping from "the corpus" when you mean "the published index" — drops are per-target; local keeps everything not corrupt.

## Resources

- Pandas `isna`/`notna` semantics; `str.contains` with `regex=False` for literal receipts.
- The manifest schema: [`../01-multimodal-ai-landscape/03-metadata-handling.md`](../01-multimodal-ai-landscape/03-metadata-handling.md).
