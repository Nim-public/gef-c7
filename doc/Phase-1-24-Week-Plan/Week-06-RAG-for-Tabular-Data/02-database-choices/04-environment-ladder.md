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

## Exercises

1. Create the environment split in your config (`ENV=dev|staging|prod`);
   verify the settings differ per env and the model stays pinned.
2. Ladder drill: promote a staged change to "prod" on your machine; the
   acceptance gates re-run as part of the promotion.
3. Leak drill: attempt to copy a prod database file into dev; the policy
   (and your own checklist) refuses — the no-prod-to-dev rule, made
   explicit.