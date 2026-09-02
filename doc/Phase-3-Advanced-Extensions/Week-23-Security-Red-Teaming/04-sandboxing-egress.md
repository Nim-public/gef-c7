# 04 — Sandboxing & Egress Control

> E7 index: [README.md](README.md)

**Core topics:** *Sandbox tiers for code-executing agents, egress control, and blast-radius engineering.*

---

## What you'll learn

- The sandbox tier ladder: process → container → micro-VM — what each contains, what escapes
- Egress control: what an agent may *reach*, and how to enforce it at the network layer
- Blast-radius engineering: designing for "the agent is fully compromised" as the baseline
- The concrete sandbox for your W19 code agents and W14-05 assistant

## 1. The blast-radius baseline

Design assumption for any agent with execution/tools: **it is compromised from birth** (W3-02: injection is unsolved). Then every control answers one question — *"if fully hijacked, what can it destroy, exfiltrate, or spend?"*

| Control layer | Limits |
|---|---|
| credentials scope | what it can authenticate as |
| filesystem | what it can read/write |
| network egress | where it can connect |
| compute | how long/how much it can run |
| blast radius | the *union* of the above under one hijack |

## 2. The sandbox tier ladder

| Tier | Mechanism | Contains | Escapes via |
|---|---|---|---|
| 1. Restricted process | no network, temp dir, restricted builtins (W14-02's eval) | naive file reads | kernel/local exploits |
| 2. Container (Docker) | FS/network namespaces, resource caps | same-container processes | container escapes (rare), mounted secrets |
| 3. Micro-VM (Firecracker/gVisor) | hardware-virtualized boundary | almost everything | (research-grade) |
| 4. Separate machine | physical/network isolation | everything short of network | egress misconfiguration |

Mapping: W13-04's `subprocess + tempdir` is tier 1 (teaching); your capstone's code agents should be tier 2 minimum; anything multi-tenant or internet-facing → tier 3.

```python
# tier 2 sketch: the W13-04 test runner inside a locked-down container
docker run --rm --network none \
  --read-only --tmpfs /tmp:size=64m \
  --cap-drop ALL --security-opt no-new-privileges \
  --memory 512m --cpus 1 \
  -v "$PWD/task:/task:ro" \
  python:3.12-slim py -m pytest -q /task
```

`--network none` (no egress at all for test runs), read-only root, dropped capabilities, hard memory/CPU ceilings — each flag is a blast-radius wall. The task directory mounts **read-only**; results come back via a writable `/tmp` only.

## 3. Egress control

For agents that *need* network (your MCP tools, W14-05):

- **Allow-list destinations** at the proxy/firewall: the agent's egress passes through a proxy permitting only `api.openai.com`, `api.github.com`, `your-db-host` — everything else drops
- **DNS-level** deny (fail-closed) for exfiltration-by-DNS
- **No direct internet** from sandbox tiers 2–3 — egress via the proxy only
- **Secrets never in the sandbox** — the *proxy/gateway* holds credentials; the agent calls the gateway with a scoped short-lived token (W10-03's gateway pattern)

```python
EGRESS_ALLOWLIST = {"api.openai.com", "api.github.com", "db.internal:5432"}

def egress_check(host: str) -> bool:
    return host in EGRESS_ALLOWLIST          # enforced at the proxy, not in agent code
```

Enforced at the *network* layer — agent-code checks are advisory (W10-02's executor principle: the model proposes, infrastructure disposes).

## 4. Tool blast-radius review (the checklist)

For every tool (W14-05's inventory):

| Question | Fix if bad |
|---|---|
| What's the worst single call? | scope down (read-only variants, dry-run flags) |
| Is it idempotent? | add keys/dedup; retries safe (W10-02) |
| Does it touch other users' data? | tenant filter at the tool (W5-03 prefilter) |
| Can it be called in a loop cheaply? | rate limit + budget hooks (W15-01) |
| Does its *output* enter another model's context? | sanitize observations (W10-05, LLM01 indirect) |

Run this table at every tool addition — it's the security equivalent of W10-02's design-rules table.

## Exercises

1. Build the tier-2 sandbox runner for your W13-04 code agent (`docker run --network none ...`); verify: code that tries `requests.get` fails; code that reads `/etc/passwd` fails; the test still runs.
2. Egress audit: run your W14-05 assistant with proxy logging on for one day; list every destination contacted — anything not in the allow-list is a finding.
3. Secret-hygiene review: grep your sandbox images/configs for tokens; move all credentials to the gateway (§3); verify the sandbox has *zero* env secrets.
4. Blast-radius table: complete file 01 §4's checklist for every tool in your capstone; rank tools by worst-single-call outcome.
5. Escape drill: attempt the classic container escapes (mount host paths, write outside tmpfs, network to internal hosts) — verify each wall holds; document any that don't.

## Pitfalls

- **"--network none" for tools that need network** — then the tool runs *outside* the sandbox and the sandbox is theater; put network-needing steps behind the gated gateway instead
- **Mounted secrets** — `-v ~/.kube:/home/.kube` mounts your cluster; never
- **Root inside the container** — `--cap-drop ALL` + non-root user; root with a container escape is host root
- **Egress allow-lists without DNS enforcement** — hardcoded IPs bypass hostname allow-lists; fail-closed DNS
- **Sandbox tiers tested only at build time** — verify at runtime too (egress logs, resource metrics — W15-02's alerts)

## Resources

- Docker [security docs](https://docs.docker.com/engine/security/) — capabilities, read-only, tmpfs
- gVisor (Google) / Firecracker (AWS) — tier-3 sandboxing
- W10-03 (gateway pattern), W13-04 (code agents), W14-05 (cross-server), W15-01/02 (limits/observability) — composed here
- OWASP LLM06 (file 01) — excessive agency is the risk this file engineers away
