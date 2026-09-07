# 01.5 — Spaces & Deployment

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

---

## What you'll learn

- Space anatomy: SDK choice, repo structure, README config
- Hardware tiers and their real capabilities
- Secrets, storage, and the first-boot discipline
- When Spaces is the right deployment vs your own stack

## 1. Space anatomy

A Space is a git repo with an app:

```
my-space/
├── README.md            # yaml front matter = the Space config
├── app.py               # the Gradio/Streamlit app
├── requirements.txt     # pip dependencies, pinned
└── (models load from the Hub at boot — not committed)
```

```yaml
# README.md front matter
---
title: Capstone Triage Demo
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
---
```

The config drives the build: SDK choice, Python version (`sdk: gradio` + `python_version`), and hardware (`suggested_hardware`). Change the config → Space rebuilds.

## 2. Hardware tiers (reality check)

| Tier | Hardware | Runs comfortably |
|---|---|---|
| CPU basic (free) | 2 vCPU, 16 GB | encoders, 0.5B SLMs, small pipelines |
| CPU upgrade | 8 vCPU, 32 GB | bigger SLMs, concurrent traffic |
| GPU tiers | T4/A10G-class | 7B models, diffusion (W2-04) |
| ZeroGPU | dynamic H200 slices | on-demand GPU for demos |

The fp16 memory math (W2-04) applies: a 7B model needs ~14 GB weights + KV — beyond the free CPU tier. Design demos around ≤1B models on free hardware, or use the Inference API for the heavy step (W9-01's tier table).

## 3. First-boot discipline

The Space installs `requirements.txt`, then runs `app.py` — and models download **during boot**:

```python
import os
from huggingface_hub import snapshot_download

MODEL_REVISION = "735b0a1"                     # pinned (W2-01)
snapshot_download("distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                  revision=MODEL_REVISION)     # pre-pull before app start
```

- **Startup time is user-facing** — a 5 GB download on first boot means minutes of "building"; pre-pull in the Dockerfile or accept the wait
- **Pinned revisions** — `main` moving upstream breaks a running demo silently (W2-01's rule, demo edition)
- **Secrets** — set in Space settings (`HF_TOKEN`, API keys); read via `os.environ` — never in the repo

## 4. Storage and state

| Need | Mechanism |
|---|---|
| persistent files | paid persistent storage, or external (HF Datasets/S3) |
| user uploads | ephemeral — gone on restart unless persisted |
| logs | stdout → Space logs; export important events (W10-04) |

Ephemeral storage means: the catalog-entries JSONL (W9-01's app 2) resets on restart — persist to a Dataset or external store if the data matters. The W9-01 design rule applies: Spaces demos are *demos*; the production path stays in your own stack.

## 5. Spaces vs your own deployment (W9-01 §4 revisited)

| Criterion | Spaces | Own stack (FastAPI + vLLM) |
|---|---|---|
| setup | minutes | hours |
| control | config-level | full |
| scaling | tier upgrades | your infra |
| cost | free → paid tiers | infrastructure |
| fit | demos, portfolio | production |

Portfolio guidance: **every capstone demo artifact gets a Space** (recruiters can click), while the production path stays in your own stack — the two share code, not infrastructure.

## Exercises

1. Deploy the W9-01 cataloger to a Space; measure first-boot time and identify the boot-time bottleneck (model download vs pip install).
2. Secrets drill: add an API-key secret; read it in the app; verify it's absent from the repo and logs.
3. Ephemeral-storage proof: write a file, restart the Space, confirm it's gone — then add persistent storage or an external store and re-verify.
4. Pin-and-break drill: deploy with `revision=main` for a model that updates upstream — observe what changes; then pin and confirm stability.
5. Hardware sizing: run your cataloger on CPU basic; measure concurrent-request behavior (2 users) — decide the tier you'd pay for.

## Pitfalls

- **Model downloads inside the request handler** — boot-time pre-pull only (W9-01's load-once rule)
- **fp16 expectations on CPU** — crashes or silent fp32 fallback; use CPU-safe dtypes (W2-04)
- **Unpinned Space SDK versions** — a Gradio major update can break the app on rebuild; pin `sdk_version`
- **Logs as the only persistence** — Space restarts clear ephemeral state; export anything you need (W10-04)
- **Public demos with real user data** — Spaces are public; mask PII before it ever reaches the app (W5-04)

## Resources

- [Spaces docs](https://huggingface.co/docs/hub/spaces-overview) — config, hardware, secrets
- W9-01 (Gradio), W2-01 (pinned revisions), W15-02 (observability) — composed here
- [Gradio sharing guide](https://www.gradio.app/guides/sharing-your-app) — `share=True` mechanics and limits
