# Exercises — The Hugging Face Platform

> Subfolder index: [README.md](README.md) · Parent: [../01-huggingface-platform.md](../01-huggingface-platform.md)

Labs for this subfolder. Shared artifact: a `platform_log.md` where every drill's findings are recorded — it becomes the W2-06 protocol's evidence.

---

## E1 — Discovery protocol (file 01)

1. For your capstone task, run the full discovery workflow (filter → license → language → downloads → cards → widgets) and produce a 5-model shortlist table.
2. Compare trending vs downloads for the same task — identify one model that appears in trending but not downloads, and investigate why (new? marketing? real?).
3. File-tab audit for the shortlist: sizes, sharding, tokenizer presence, safetensors vs bin — flag any candidate that can't run on your hardware.

**Worked approach:** exercise 1's table is the W2-06 §3 shortlist's first column — discovery and selection are one continuous protocol.

## E2 — Card audit deep dive (file 02)

1. Six-question audit on 3 shortlisted models — with a *verdict row* per model (usable baseline / needs eval / exclude).
2. License-chain research: pick one gated model; trace the license terms to their source; write the obligations list for a team of 3 using it.
3. Dataset card audit for your training/eval data — PII statement, license, splits; flag missing fields.

**Worked approach:** the audit produces the "why this model" evidence the mentor session will ask for — attach the completed tables to the W2-06 README.

## E3 — Cache and pinning (file 03)

1. Cache archaeology: map one model's `refs → snapshots → blobs` chain by hand; verify a `revision=` load reads the exact snapshot you expect.
2. Drift detection: snapshot a model's `config.json` today; re-check in a week (or force with a different revision) — document any drift and the pinning fix.
3. Token scoping: create fine-grained read/write tokens; attempt a push with the read token; document the failure and the scoping lesson.

**Worked approach:** exercise 2's drift check is the E8-01 registry argument in miniature — one config diff is a behavior change.

## E4 — Datasets at scale (file 04)

1. Streaming vs load: 1M-row dataset — compare peak memory, iteration speed, and shuffle quality (buffer sizes).
2. Batched map benchmark: tokenization with `batched=True` at `num_proc` 1/4/8 — throughput table.
3. Versioned dataset build: your capstone data → stratified splits → `save_to_disk` versioned → reload and assert equality.

**Worked approach:** exercise 3's shuffle-quality metric (label distribution in the first 100 samples) quantifies the streaming approximation — the number that decides whether streaming is acceptable for training.

## E5 — Spaces deployment (file 05)

1. Deploy the W2-02 sentiment tool as a Space; measure first-boot time; break it down (pip install vs model download vs app start).
2. Secrets + PII: add a provider key as a Space secret; submit synthetic PII through the app and verify it's scrubbed before logging (W5-04).
3. Restart resilience: write a file, restart, confirm gone; then implement the Dataset-persisted variant and confirm survival.

**Worked approach:** exercise 1's boot-time breakdown usually reveals that model download dominates — the fix is pre-pulling with `snapshot_download` in the Dockerfile (file 05 §3).

## Self-assessment

- Can you go from "I need a sentiment model" to a pinned, licensed, evaluated candidate in under 30 minutes?
- Can you explain the cache layout well enough to debug a corrupted download?
- Can you deploy a demo to Spaces with secrets handled and no ephemeral-data surprises?
