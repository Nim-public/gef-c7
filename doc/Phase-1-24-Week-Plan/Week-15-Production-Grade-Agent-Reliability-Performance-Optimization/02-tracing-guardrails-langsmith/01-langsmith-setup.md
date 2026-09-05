# LangSmith Setup — Automatic Tracing, Projects

**What you'll learn:** the hosted tracing switch: environment setup, the
project model, what LangSmith captures automatically for LangChain and
LangGraph runs, and how it complements (not replaces) your harness.

## 1. The setup

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="lsv2_..."
export LANGSMITH_PROJECT="gef-c7-prod"      # one project per environment
```

| Setting | Effect |
|---|---|
| `LANGSMITH_TRACING=true` | LangChain/LangGraph runs trace automatically — zero code |
| `LANGSMITH_PROJECT` | groups runs: `gef-c7-dev`, `gef-c7-prod`, `gef-c7-eval` |
| API key | separate from model keys (the W11 hygiene rule) |

One environment variable turns on tracing for every LangChain and
LangGraph run — no code changes. The project split is the observability
version of the environment split: dev traces never pollute prod views.

## 2. What gets captured (and how it maps to your store)

| Captured | Your W10 store equivalent |
|---|---|
| full run trees (inputs/outputs per step) | trajectory trace JSONL |
| latencies per span | the ledger |
| token counts per call | the fitter ledger |
| errors with stack context | the failure log |
| feedback (scores attached to runs) | the judge columns |

LangSmith is the *interactive* view; your parquet store remains the
*analysis* surface. The merge (W11 file 05-03) works the same way:
export from the platform, join into your rows. The two-view rule from
W12's UI strategy applies to hosted tracing too.

## 3. What to send (the send-policy)

| Data | Send? | Rationale |
|---|---|---|
| run trees, latencies, token counts | yes | the observability payload |
| full prompts with corpus content | sample only | your corpus is private |
| user-identifying content | never | the firewall extends here |
| eval scores | yes | the hosted comparison needs them |

The send-policy is the W11 trace hygiene rules, hosted edition. The
default LangSmith configuration sends *everything*; the sampling and
scrubbing (file 04) are what make sending compatible with a private
corpus.

## 5. The setup pin note (the observability manifest)

```markdown
# Observability setup (W15)
- LangSmith: tracing on, projects dev/prod/eval, key separated
- send-policy: reports/send-policy.md (sampled content, no PII)
- retention: platform default overridden per policy (file 04)
- mapping: hosted fields ↔ W10 store fields (file 01 §3)
- local store: authoritative, scrubbed, indefinite
```

The setup pin note is the observability manifest — the same pin
discipline applied to the tracing layer. It records what is sent, where
it goes, and which local artifacts remain authoritative.

## Exercises

1. Enable tracing on the dev project; run 5 eval tasks; verify runs
   appear with full trees; compare against your trajectory rows.
2. Project-split drill: dev and prod projects; confirm a dev query never
   appears in the prod view.
3. Mapping drill: for one run, list every LangSmith field and its W10
   store counterpart — the merge table, hosted edition.
4. Pin drill: write the manifest page; every claim links its drill or
   config.

## Pitfalls

- Tracing left on with default settings in prod — full corpus content
  leaves your machine; the send-policy is not optional.
- One project for everything — dev noise buries prod signal; split by
  environment.
- Treating LangSmith as the store — it is a view with retention you do
  not control; the parquet stays authoritative.