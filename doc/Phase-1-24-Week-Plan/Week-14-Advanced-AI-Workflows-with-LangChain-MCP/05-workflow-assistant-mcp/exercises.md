# Exercises — Workflow Assistant with MCP

Expanded set with worked approaches. The deliverable: the federated
adapter, the containment matrix verified, one gated cross-server chain,
and the federated injection battery.

## 1. The adapter (from 01-mcp-adapter)

**Task:** build the multi-server adapter; print the federated surface;
run the collision drill (two `search` tools) and the contract drill
(version bump).

**Worked approach:** the namespacing and version asserts are the
adapter's two load-bearing features — the drills prove both. The
federated surface table goes into the tool-contract page as its
federated edition.

**Pass criterion:** 3 servers connected, version-asserted; the collision
drill shows both tools callable; the version bump fails loudly.

## 2. Containment (from 02-scope-containment)

**Task:** implement the containment matrix; run the env probe inside
each server (CI-asserted); the path-scoping and exposure drills.

**Worked approach:** the env probe is the token-isolation proof —
printed from *inside* each server process, asserted in CI. The exposure
drill proves the adapter filters what the model sees.

**Pass criterion:** 3/3 env probes clean; path scoping enforced; the
exposure list matches the servers' tools.

## 3. The gated chain (from 03-gated-chains)

**Task:** build the ingest chain (files → RAG) with gates; run the
battery's four cases; assert server-call sequences from the trace.

**Worked approach:** the server-call sequence is the chain's trace
assertion — cross-server failures are ordering failures, and the trace
is where they surface. The partial-failure case is the chain's hardest
test.

**Pass criterion:** 4/4 battery cases; sequences asserted; the
partial-failure retry plan produced.

## 4. Federated injection (from 04-cross-server-injection)

**Task:** run the federated battery (4 cases); the realistic-footer
drill; extend the ingest firewall to metadata if needed.

**Worked approach:** the footer case is the realistic attack — the
content scan must catch poison hidden in legitimate documents. Every
stage's defense fires; the containment table gains its drill evidence.

**Pass criterion:** 4/4 cases contained; the metadata gap (if found)
fixed; the containment table complete.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Adapter: namespaces + version asserts | collision/version drills | 4 |
| Containment matrix verified | env probes | 4 |
| Gated chain: 4 cases + sequences | chain battery | 4 |
| Federated injection contained | battery + footer drill | 4 |
| Federated contract page | tool-contract.md | 2 |

**Pass bar:** 15/18 to proceed to file 06 (the framework verdict). The
federated injection battery (4-pointer) is the security deliverable —
the federation must add stages of defense, not doors.

## 6. The federated pin note (the workflow assistant's manifest)

**Task:** consolidate the federated stack in `reports/sdk-versions.md`:
the adapter config, the containment matrix, the chain's state schema
version, and the injection battery command — one block.

**Worked approach:** the federated build has the most moving parts of
any week — the manifest lists every server, its scope, and its
verification date.

**Pass criterion:** the manifest lists all servers with green commands
as recorded.

## 7. The federation security page

**Task:** write `reports/federation-security.md`: the trust-boundary
diagram (file 04's §4), the containment matrix, the injection battery
results, and the containment scope-of-scope (file 02's §6) — the
federation's security face.

**Worked approach:** the page composes the drills into one evidence
sheet — the reviewer question is "what happens when one server is
compromised?" and each row answers with its blast radius and defense.

**Pass criterion:** the page answers the compromise question per server
in one read, citing the drills.

## Pitfalls recap

- Unnamespaced federated tools — collisions surface as wrong answers;
  the prefix prevents the class.
- Server-to-server trust — no server trusts another's output raw; the
  boundaries page states it.
- Gates skipped inside chains — every state change gates; the battery
  asserts the sequence.