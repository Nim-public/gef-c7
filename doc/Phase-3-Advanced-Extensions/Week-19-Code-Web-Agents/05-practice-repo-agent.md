# 05 — Practice: Repo QA & Fix Agent

> E3 index: [README.md](README.md) · **Due: before E4**

*(Practice build — a read-only repo agent plus a gated fixer, run against your actual capstone repository, with the CI integration demonstrated locally.)*

---

## 1. Deliverable

```
repo-agent/
  tools.py               # repo_map / grep_code / read_file / apply_edit / run_tests (E3-01)
  qa_agent.py            # read-only QA agent (file 01 §4)
  fixer.py               # bounded fix loop → PR proposal (file 04 §3)
  ci/
    review_bot.py        # PR review entry point (diff → findings comment)
    workflow.yml         # the CI workflow file (file 04 §2)
  eval/
    qa_cases.jsonl       # 10 repo questions with file:line gold answers
    results.md           # QA accuracy + fixer drill results
  README.md              # tool-interface notes, gate table, failure modes
```

Demo: 3 repo questions answered with `file:line` citations; one planted-bug fixer cycle (propose → approve → apply → tests pass); one CI review-bot run (locally executed) posting a comment.

## 2. Requirements (graded)

### QA agent (file 01)
- [ ] Tools: repo_map, grep_code (capped), read_file (windowed) — all with workspace containment + secret-file deny lists (`.env` etc.)
- [ ] 10 repo questions answered with `file:line` citations; ≥8/10 verified correct
- [ ] "Not found in repo" behavior demonstrated on 2 out-of-repo questions

### Fixer (file 04 §3)
- [ ] Bounded loop (≤2 repair iterations) with sandboxed test runs (tempdir + timeout, W13-04)
- [ ] Gate: proposed patch shown as diff; apply only on approval
- [ ] Provenance: PR/proposal description includes the failure log, the plan, and attempts made

### CI (file 04)
- [ ] `review_bot.py` runnable locally on a diff file; posts/updates one review comment (marker-based idempotency)
- [ ] Workflow YAML committed (even if only run locally via `act`/script)
- [ ] Gate table in `README.md`/CONTRIBUTING (file 04 §4)

## 3. Rubric

| Area | Weight |
|---|---|
| Tool interface quality (caps, containment, structured returns) | 25% |
| QA agent accuracy + citation discipline | 25% |
| Fixer safety (sandbox, gates, provenance, bounded loop) | 25% |
| CI integration (workflow, idempotency, gate table) | 15% |
| README + failure modes | 10% |

## 4. README sections (answer explicitly)

1. **Tool interface notes**: what each tool returns, caps, and the SWE-agent interface lessons you applied (E3-01 §1) — with one measured A/B (file 01 ex. 2)
2. **Gate table**: your repo's version of file 04 §4
3. **Failure modes** (≥3) from QA/fixer runs, with trace evidence
4. **Security notes**: containment, secret deny lists, sandbox details (W13-04 §2 rules, restated for your setup)
5. **E4 bridge**: which vision-tier gaps (computer use, E4) does your workflow have — and would any *not* be solvable by better API/DOM access? (The tier ladder, applied to your own tooling.)

## 5. Stretch (pick one)

- Repo-map improvements: embed file summaries (W9) so the agent can semantic-search the repo, not just grep — measure localization steps delta
- Multi-repo support: the QA agent answers questions across two repos with scoped mounts — what changes in the tools?
- Auto-changelog: a triager agent that reads merged PRs weekly and drafts a changelog entry (W14-04's automation, read-only + draft gate)

Bring the QA accuracy and the fixer PR to your next mentor session — the capstone phase will ask "can the agent maintain its own codebase?", and this is your evidence.
