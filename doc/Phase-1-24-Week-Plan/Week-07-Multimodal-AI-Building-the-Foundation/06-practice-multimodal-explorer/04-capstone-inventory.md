# Capstone Modality Inventory — Scope Integration

**What you'll learn:** Part D (the capstone write-back): turn the week's
findings into the modality inventory table, the scope statement, and the
README section that Weeks 08–16 will assume exists.

## 1. The inventory is a *decision record*

The inventory from
[`../01-multimodal-ai-landscape/04-the-modality-gap.md`](../01-multimodal-ai-landscape/04-the-modality-gap.md)
becomes the capstone's scope when every cell is filled with *your* numbers
and every open question has a named week that answers it:

```markdown
## Modality inventory (Week 07)

| Field | text | image | audio | video |
|---|---|---|---|---|
| Unit | page | image | 30 s window | 12-frame clip |
| Count | 214 | 96 | 18 | 5 |
| Raw size | 1.2 MB | 310 MB | 74 MB | 2.1 GB |
| Encoder | minilm-l6 (384) | clip-b32 (512) | clap (512, wk 9) | clip-b32 (512) |
| Preproc settings | v3 | v3 | v3 (wk 8) | v3 |
| Text sidecar | — | OCR pending (wk 9) | ASR pending (wk 8) | ASR+OCR (wk 8–9) |
| Gap risk | truncation | unindexed charts | music beds | temporal |
| Fix owner | wk 4 done | wk 9 | wk 8 | wk 7 sampling done |
```

Rules that keep the table honest: counts come from the manifest (never
hand-typed); every "pending" cell names the week that fills it; encoder
columns include the dimension (the seam the index needs).

## 2. The scope statement (three sentences, not three pages)

Below the inventory, write exactly:

1. **In scope:** the modalities, units, and tasks (retrieval + grounded QA)
   the capstone commits to.
2. **Out of scope:** what you are *not* doing (e.g., real-time indexing,
   fine-tuning encoders, user uploads at demo time) — with one-line reasons.
3. **Deferred with a date:** borderline items and the week they get decided.

The scope statement exists because Week 13 (integration) is where scope
creep kills capstones. A table written in Week 07 is the contract you
re-negotiate explicitly instead of silently.

## 3. The README section, generated not written

The inventory and scope live in your capstone README under
"Modality inventory" — generated from the manifest + settings:

```python
# scripts/emit_inventory.py
def emit_inventory(manifest_path: str, settings: dict) -> str:
    df = pd.read_parquet(manifest_path)
    lines = ["## Modality inventory (auto-generated)", "",
             "| Field | " + " | ".join(sorted(df.modality.unique())) + " |",
             "|---|" + "---|" * df.modality.nunique()]
    counts = df.modality.value_counts().to_dict()
    lines.append("| Count | " + " | ".join(str(counts[m]) for m in sorted(counts)) + " |")
    lines.append(f"| Settings version | v{settings['version']} |")
    return "\n".join(lines)
```

Counts regenerate with the data; the "pending" cells are the only hand-written
part, and they are dated — this keeps the README from becoming fiction.

## 4. The handoff to Weeks 08–09

What the next weeks consume from this one:

| Week 08 (ASR) | Week 09 (…) | consumes |
|---|---|---|
| audio sidecar plan | encoder choice | inventory row "audio" |
| 30 s window setting | CLAP dim | `preproc-settings.json` |
| alignment offsets | gap mitigations | alignment parquet + gap-risk rows |
| sidecar status field | inventory refresh | `emit_inventory.py` |

Concretely: Week 08 starts by *reading your inventory's audio row* and
either confirming or amending the unit/setting decisions. If your audio
units change (30 s → 10 s), the settings version bumps, embeddings for that
modality re-encode, and `emit_inventory` regenerates the table — the whole
loop is one command per step.

## Exercises

1. Generate your inventory with `emit_inventory`; hand-edit only the
   "pending" cells; commit both the script and the generated section.
2. Write the scope statement; then invent the Week 13 version of yourself
   re-reading it — is any scope item actually ambiguous? Fix it now.
3. Dry-run the Week 08 handoff: read your audio row and write the one-paragraph
   ASR plan it implies (units, settings, sidecar field, alignment offsets).

## Pitfalls

- Inventory counts diverging from the manifest within a week — counts must be generated, or they are wishes.
- "Deferred" without a date — deferred-forever is the default fate; a week number makes it a promise.
- Scope written *after* the pipeline (Week 13) — write it now; revising a scope is cheap, revising a pipeline is not.

## Resources

- The inventory template: [`../01-multimodal-ai-landscape/04-the-modality-gap.md`](../01-multimodal-ai-landscape/04-the-modality-gap.md).
- Your corpus stats: `reports/corpus-stats.json` (explorer file 01).
