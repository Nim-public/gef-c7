# Environment Ladder — Dev / Staging / Prod Data Policies

**What you'll learn:** the environment ladder: dev, staging, and prod
data policies — what data lives where, what flows between environments,
and the rules that prevent prod data leaking into dev demos.

## 1. The ladder

| Environment | Data | Purpose | Access |
|---|---|---|---|
| dev | seeded synthetic corpus | building, tests | you only |
| staging | full corpus copy, fresh ingest | pre-release validation | you + reviewers |
| prod | the real corpus | the demo, real use | the deployed app |

| Flow | Rule |
|---|---|
| dev → staging | scripted rebuild from the same seed + real docs |
| staging → prod | promoted only after acceptance gates pass |
| prod → dev | **never** (PII and real data stay in prod) |

The W13 environment policy (checkpoint hygiene, thread isolation) and
the W9 deployment rules (secrets, queue limits) apply per environment —
the ladder is where they're organized.

## 2. What differs per environment (the config split)

| Setting | dev | staging | prod |
|---|---|---|---|
| model | pinned, temp 0 | pinned, temp 0 | pinned, temp 0 |
| tracing | 100% sampled | 100% | 10–20% + failures |
| budgets | generous (debugging) | production values | production values |
| data | synthetic seeded | full corpus copy | the real corpus |
| gates | fast batteries | full acceptance | full acceptance |

The config split is the settings-version discipline per environment —
the budgets.json, send-policy, and pin notes all carry an environment
field. The pinned model and temperature never differ; everything
operational does.

## 3. The promotion checklist (staging → prod)

```text
[ ] acceptance gates green on staging (full run)
[ ] the five bars (W16 file 04) measured on staging
[ ] the corpus copy verified (hash match with prod source)
[ ] secrets via env vars only (no keys in configs)
[ ] the fallback drills rehearsed on the prod host
```

The checklist is the W14 acceptance command, re-run on the staging copy
of the *prod* environment — the promotion is a gate passage, not a copy
command.

## 5. The environment pin note (the ladder's record)

```markdown
# Environments (W06)
- dev: seeded corpus, tracing 100%, generous budgets
- staging: full corpus copy, full acceptance gates
- prod: the real corpus, sampling 20%+failures, production budgets
- model/temperature: identical across all three
- promotion: staging → prod via the acceptance checklist only
- prod → dev: never (the leak drill refuses)
```

The pin note is the ladder's record — per-environment settings and the
promotion rule. It is the W9 deployment checklist's data-policy
chapter.

## 6. The ladder drill record (the promotion's evidence)

```text
promotion: staging → prod (local rehearsal)
gates: accept.py --full on the staging copy → 6/6 PASS
corpus hash: staging == prod source ✓
secrets: env-only scan clean ✓
fallback drills: rehearsed on prod host ✓
verdict: promoted; the promotion checklist is the receipt
```

The drill record is the promotion's evidence — the gates re-run on the
staging copy, the corpus hash verified, the secrets scanned, the
fallbacks rehearsed. Promotion is a gate passage with a receipt.

## Exercises

1. Create the environment split in your config (`ENV=dev|staging|prod`);
   verify the settings differ per env and the model stays pinned.
2. Ladder drill: promote a staged change to "prod" on your machine; the
   acceptance gates re-run as part of the promotion.
3. Leak drill: attempt to copy a prod database file into dev; the policy
   (and your own checklist) refuses — the no-prod-to-dev rule, made
   explicit.
4. Pin drill: write the note; the promotion checklist referenced.
5. Record drill: fill §6 from a real promotion rehearsal; the checklist
   items checked off in the record.