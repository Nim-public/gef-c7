# Exercises — MCP Servers & FastMCP

Expanded set with worked approaches. The deliverable: your RAG tools
served over MCP, both battery tiers green, surface frozen at v1.

## 1. Server extraction (from 02-fastmcp-server)

**Task:** extract the Week-09 handlers into `scripts/mcp_rag_server.py`
with four tools/resources; connect from a stdio client; diff
`tools/list` against registry schemas.

**Worked approach:** the diff test is the extraction's acceptance gate —
schema drift between in-process and wire means the server re-defined
what the registry already specified. Single source: derive from the
registry module.

**Pass criterion:** 4 tools listed; schema diff empty; version string
matches tool-contract v.

## 2. Error fidelity across the wire (from 02)

**Task:** for each error class (unknown tool, schema fail, contract
error), verify the `isError` content preserves the hint text; then run
the agent against the served tools and confirm recovery step counts
match the in-process baseline.

**Worked approach:** the fidelity table is 3 rows × (in-process hint,
wire hint, recovery steps). Hints that get truncated or reworded by the
boundary are bugs — the model's recovery depends on them verbatim.

**Pass criterion:** 3/3 hints intact; recovery steps within +1 of
in-process.

## 3. Both batteries wired (from 03-client-batteries)

**Task:** Tier 1 in CI (every push, <10 s); Tier 2 nightly (3 runs/task,
report committed). Produce one combined report page.

**Worked approach:** the combined report is the honest status: Tier 1's
contract rows + Tier 2's behavioral pass rates, one header (model id,
date, server version). Any Tier-2 flip gets an annotation, not a fix —
drift is data.

**Pass criterion:** CI green; nightly report committed with 2 weeks of
history (or a plan for it).

## 4. Surface freeze + security pass (from 04)

**Task:** freeze v1 in `doc/capstone/tool-surface.md`; run the security
pass: hostile args (`k=10_000`, `unit_id="../etc/passwd"`), egress check
(no network calls in handlers), path sanitization on returns.

**Worked approach:** the security pass is a 30-minute checklist with the
four threat rows — each gets one test. The hostile-args tests join
Tier 1 permanently.

**Pass criterion:** v1 frozen with date; 4/4 security tests green and in
CI.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| 4-tool server, schema diff empty | diff test | 3 |
| Error fidelity 3/3 + recovery parity | fidelity table | 3 |
| Tier 1 in CI, Tier 2 nightly report | CI + reports/ | 4 |
| Surface frozen + security pass 4/4 | tool-surface.md + tests | 3 |
| Transport drill (stdio vs HTTP identical) | drill note | 2 |

**Pass bar:** 12/15 to proceed to file 04 (measurement). The battery
wiring (4-pointer) is the deliverable that makes every later week's
agent changes safe.

## 6. The out-of-process migration story

**Task:** document the migration in `reports/mcp-migration.md`: the
in-process registry's test list, the wire-parity test results (schemas,
errors, hints), the one behavioral difference found (if any), and the
rollback plan (registry-only mode behind a flag).

**Worked approach:** the story is the proof that MCP added transport, not
behavior. Any behavioral difference is either a bug (fix) or a documented
boundary semantic (e.g., timeouts now fire at the client).

**Pass criterion:** one-page migration story committed; parity table
complete; behavioral differences each have a verdict.

## Pitfalls recap

- Handlers reimplemented in the server instead of imported — two sources
  of truth; the diff test exists to kill this.
- Tier-2 suites without model pinning — a model bump silently rewrites
  your baselines.
- Security tests written but not in CI — the pass rots; wire it or it is
  decoration.
