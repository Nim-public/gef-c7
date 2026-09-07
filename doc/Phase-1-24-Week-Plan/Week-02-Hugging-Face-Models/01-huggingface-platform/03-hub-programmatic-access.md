# 01.3 — Hub Programmatic Access

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

---

## What you'll learn

- The cache layout — where downloads land and how to read them
- Revision pinning and the reproducibility workflow
- Auth: tokens, scoping, and CI usage
- Pushing your own artifacts (models, datasets, cards)

## 1. The cache layout — know where your gigabytes live

```
~/.cache/huggingface/
├── hub/
│   └── models--distilbert--distilbert-base-uncased-finetuned-sst-2-english/
│       ├── refs/           # revision pointers (main → commit sha)
│       ├── snapshots/      # the actual files, per revision
│       │   └── 735b0a1.../config.json, model.safetensors, tokenizer...
│       └── blobs/          # content-addressed storage (deduped)
├── datasets/
└── token/
```

Key properties: **content-addressed blobs** (identical files across models dedupe), **snapshots per revision** (pinning is just reading a different snapshot), and everything keyed under `HF_HOME` (override for shared caches on servers/CI).

```python
import os
os.environ["HF_HOME"] = "D:/hf-cache"        # before any HF import — set early
```

## 2. Revision pinning — the reproducibility contract

```python
from huggingface_hub import hf_hub_download, list_repo_commits

commits = list_repo_commits("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
sha = commits[-1].commit_id                        # or pick the one you validated

path = hf_hub_download(
    repo_id="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    filename="config.json", revision=sha)          # immutable snapshot
```

Every load in your capstone carries `revision=` (W2-01's rule): `AutoTokenizer.from_pretrained(id, revision=sha)`. The manifest (E8-01) records the sha — a silent upstream model update then *cannot* change your behavior.

## 3. Auth and tokens

```python
# interactive:
#   huggingface-cli login
# tokens: fine-grained scopes now exist — create a token with ONLY the needed
# permissions (read for downloads, write for pushing). Never use a write token in CI.
```

| Scenario | Token scope |
|---|---|
| downloading public + gated models you accepted | read (fine-grained) |
| pushing adapters/datasets (W17) | write, repo-scoped |
| CI regression runs | read-only bot token, separate account where terms require |

## 4. Pushing your own artifacts

```python
from huggingface_hub import HfApi

api = HfApi()
api.create_repo("your-name/capstone-baseline", private=True, exist_ok=True)
api.upload_file(path_or_fileobj="out/lora-v1/adapter/adapter_model.safetensors",
                path_in_repo="adapter_model.safetensors",
                repo_id="your-name/capstone-baseline")
api.upload_folder(folder_path="out/lora-v1/adapter", repo_id="your-name/capstone-baseline")
```

Publishing your own adapter (W17-05) with a model card: write the card *before* pushing (license, training data, eval numbers — the W2-02 audit applied to yourself). Private repos keep artifacts off the public Hub until you choose.

## 5. Space/CI token hygiene

| Rule | Why |
|---|---|
| fine-grained tokens, minimal scopes | blast radius (E7-04) |
| separate tokens per environment | dev/staging/prod isolation (E8-01's ladder) |
| tokens in Space secrets, never in code | LLM02/06 discipline |
| rotate on any suspected leak | token = identity |

## Exercises

1. Cache archaeology: explore your `HF_HOME` — find one model's snapshots, refs, and blobs; map a `revision=` load to the exact snapshot directory it reads.
2. Pin-and-verify: load a model at two different revisions; diff the `config.json`s — show what changed between them.
3. Token-scoping drill: create a fine-grained read-only token; attempt a push with it (should fail); document the error.
4. Push an adapter: publish your W16-04 LoRA adapter to a private repo with a card containing license/eval/lineage; load it back from the Hub and verify identity.
5. CI cache design: write the CI config that persists `HF_HOME` across pipeline runs — calculate the download time saved for your models.

## Pitfalls

- **HF_HOME set after imports** — the environment variable must exist before any HF library initializes its cache paths
- **Write tokens in CI** — a leaked write token can replace public models; read-only bot tokens only
- **Trusting `main` in production code** — silent upstream drift (W2-01's floating-ref rule)
- **Blob dedup confusion** — identical files across revisions share blobs; deleting "old" snapshots manually can break refs
- **Uploading without a card** — an artifact without license/eval/lineage is unusable by anyone (including future you)

## Resources

- [huggingface_hub docs](https://huggingface.co/docs/huggingface_hub/index) — cache, auth, upload APIs
- HF [cache layout reference](https://huggingface.co/docs/huggingface_hub/package_reference/cache) — the directory structure
- [Fine-grained tokens](https://huggingface.co/docs/hub/en/security-tokens) — scoping guide
- W2-01 parent, W16-01 (versioning), W17-05 (adapter publishing) — composed here
