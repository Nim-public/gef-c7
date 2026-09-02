# 04 — Agents in CI Pipelines

> E3 index: [README.md](README.md)

**Core topic:** *Agents inside CI/CD — review bots, fix bots, and the gate design that makes them safe in automation.*

---

## What you'll learn

- The three CI agent shapes: reviewer, fixer, triager — with trigger design
- The gate hierarchy: which pipeline stages an agent may touch autonomously
- Determinism and cost controls that make agent CI steps stable
- The failure drill: what happens when the agent is wrong in automation

## 1. The three shapes

| Shape | Trigger | Actions | Risk |
|---|---|---|---|
| **Reviewer** (read-only) | PR opened/updated | post findings as comments | low — comments are reversible |
| **Fixer** (writes code) | failing CI / labeled issue | open a PR with a patch | medium — a PR is reviewable by design |
| **Triager** (organizes) | new issues | label, route, dedupe, summarize | low-medium — metadata only |

The W3-05/W11-03 logic applies: pick the shape by *reversibility*. Comments and labels are reversible → autonomous. Code changes → PR (reviewable) never direct-push. Anything touching deploys/secrets → not an agent.

## 2. Reviewer bot (compose W14-03)

The W14-03 Code Review Agent becomes a CI step:

```yaml
# .github/workflows/ai-review.yml
on: [pull_request]
jobs:
  ai-review:
    runs-on: ubuntu-latest
    permissions: {pull-requests: write, contents: read}
    steps:
      - uses: actions/checkout@v4
      - run: pip install langchain openai
      - run: python review_bot.py           # fetches the diff (E3-01 tools), posts findings
        env: {OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}, GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}}
```

CI-specific rules (beyond W14-03's design):

- **Diff-only review** — full files as context, findings anchored to diff lines (W14-03 §6)
- **Cost per PR** — cap review tokens; large PRs get a summary comment + "too large for full review"
- **Idempotency** — re-runs update the same review comment (find by marker) instead of posting duplicates
- **No blocking by default** — findings are advisory until you measure the false-positive rate (W14-03 ex. 3); only then add a required check

## 3. Fixer bot (the bounded loop)

```python
def fix_failing_ci(failure_log: str) -> None:
    plan = planner(failure_log)                          # W13-04's plan node
    for attempt in range(2):                             # bounded (W11-03)
        patch = write_patch(plan)
        if not tests_pass_locally(patch):                # W13-04's run_tests node — sandboxed
            plan = debug(plan, test_output); continue
        open_pr(patch, links_to_failure=True)            # PR, never push (W3-02/W10-04)
        return
    comment_needs_human(failure_log)
```

Rules that keep fixers trustworthy: **PRs only** (a human reviews every change); **local tests before the PR** (the self-repair loop runs in a sandbox — W13-04's discipline); **one concern per PR** (a fixer that touches six things is unreviewable); **full provenance in the description** (failure log, plan, what was tried — the W10-04 trace, posted).

## 4. Gate hierarchy (what an agent may touch)

| Pipeline stage | Agent autonomy |
|---|---|
| lint/format | full auto (deterministic tools anyway) |
| test *authoring* | PR + review (tests define correctness) |
| dependency bumps | PR + review + lockfile diff check |
| review comments | autonomous (advisory) |
| issue labels/routing | autonomous (metadata) |
| merge | **never** — human or branch-protection rules only |
| deploys/secrets | **never** |

This table is the W10-04 gate hierarchy translated to CI vocabulary — print it in your repo's CONTRIBUTING.

## 5. Determinism & cost controls

- **Pin everything**: model version, prompt versions (W3-02), tool versions — CI reproducibility demands it (W16-01's versioning)
- **Cache LLM calls** keyed by (diff hash, prompt version) — re-runs on unchanged PRs are free (W15-04)
- **Route by PR size**: small diffs → capable model; huge diffs → summary + human (W15-04's routing)
- **Budget per run**: `RunBudget` from W15-01 — an agent CI step that hangs blocks the pipeline; timeouts are not optional
- **Skip conditions**: `[skip-ai]` in the PR title, draft PRs, docs-only changes — cost control as configuration

## Exercises

1. Build the reviewer bot against this repo (`review_bot.py` + workflow file); open a test PR with a planted bug; verify the finding posts with line anchors (W14-03 ex. 2's calibration).
2. Idempotency drill: re-run the workflow on the same PR — confirm one updated comment, not duplicates.
3. Fixer drill: break a test on a branch; run the fixer locally (script mode); inspect the PR it would open — is it reviewable (provenance, single concern)?
4. Gate table: write your repo's version of §4's table into CONTRIBUTING.md; then try to make the fixer merge — verify branch protection blocks it.
5. Cost audit: tokens per PR review × your team's PR volume — monthly cost; then apply skip-conditions and routing (W15-04) and re-measure.

## Pitfalls

- **Secrets in CI-visible logs** — failure logs pasted into PRs can carry tokens; scrub (W2-02) before posting
- **Agent-authored tests** — a fixer that writes the tests it must pass is self-grading (W13-04's rule); tests come from the spec/maintainer
- **Review fatigue** — noisy bots get muted; track acceptance rate of findings as a product metric (W15-02's alert-tuning)
- **Unpinned models in CI** — a silent model update changes review tone/coverage mid-sprint (W16-01 versioning)
- **Auto-merging agent PRs** — even "verified" ones; the merge gate stays human or rule-based (branch protection), full stop

## Resources

- GitHub Actions [docs](https://docs.github.com/en/actions) + [GITHUB_TOKEN permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication) — the scoping model
- W14-03 (reviewer design), W13-04 (fix loop), W10-04 (gates/metrics), W15-01 (limits in pipelines) — composed here
- SWE-agent (E3-01) — the research ancestor of fixer bots
- [GitHub branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches) — the technical enforcement of §4's table
