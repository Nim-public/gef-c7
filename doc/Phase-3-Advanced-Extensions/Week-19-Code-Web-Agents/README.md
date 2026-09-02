# Extension E3 — Code Agents & Web Agents

> Extensions overview: [../README.md](../README.md)

**Builds on:** W10–13 (agent stack) · W14 (LangChain) · W13-04 (code-gen loop)

**Practice build:** [05-practice-repo-agent.md](05-practice-repo-agent.md)

---

## Why this extension matters

Two agent domains are transforming engineering work right now: **code agents** (SWE-bench-class systems that navigate repos, edit files, run tests — the Cursor/Claude-Code/Devin pattern) and **web agents** (browser automation where the model reads pages and clicks). Both reuse your entire agent stack (W10–14) with domain-specific action spaces and safety requirements. This week builds both patterns hands-on.

## What you will be able to do after this week

- [ ] Describe the SWE-agent loop: repo navigation, localization, edit, validate
- [ ] Build a repo-QA agent over your capstone codebase (tools: grep, read, file map)
- [ ] Build a Playwright-driven web agent that reads pages and takes actions
- [ ] Explain computer-use agents (screenshot → action) vs DOM/browser agents
- [ ] Integrate agents into CI pipelines with gates (W10-04 HITL, graph-native)

## How to study this week

| Order | File | Topic | Est. time |
|---|---|---|---|
| 1 | [01-code-agents-swe-patterns.md](01-code-agents-swe-patterns.md) | The SWE-agent loop, repo tools, localization | 3–4 h |
| 2 | [02-web-browser-agents.md](02-web-browser-agents.md) | Playwright agents, DOM extraction, action spaces | 3 h |
| 3 | [03-computer-use-agents.md](03-computer-use-agents.md) | Screenshot agents vs DOM agents vs API agents | 2 h |
| 4 | [04-agents-in-ci-pipelines.md](04-agents-in-ci-pipelines.md) | Agents in CI: review bots, fix bots, gates | 2 h |
| 5 | [05-practice-repo-agent.md](05-practice-repo-agent.md) | Repo QA + fix agent over your capstone (practice) | 4 h |

## Environment setup

```powershell
pip install playwright langgraph
playwright install chromium
```

## Self-check before E4

1. Your repo-QA agent grep'd the wrong module and answered confidently. Which tool *result* formatting change (W10-05) would have exposed the miss?
2. Web agent stuck in a login loop: is that a browser-agent failure or a planning failure (W13-04's loop bounds)? What gate catches it?
3. Why do computer-use agents cost 10–100× an API-agent call for the same task? (Name the per-step inputs.)
4. Which of your capstone's CI steps would you give to an agent *today* with zero risk — and which one never?
5. What does the SWE-agent paper's "interface design" lesson say about your repo tools' output formats?
