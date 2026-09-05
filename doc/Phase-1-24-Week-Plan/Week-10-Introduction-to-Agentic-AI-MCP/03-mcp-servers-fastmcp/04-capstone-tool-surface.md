# Capstone Tool Surface — Read-Only-First, Versioned

**What you'll learn:** the tool surface your capstone actually exposes —
the full list, each tool's contract line, the read-only posture, and the
versioning that keeps clients honest.

## 1. The surface, v1 (frozen for the capstone)

| Tool | Signature (essentials) | Returns | Class |
|---|---|---|---|
| `retrieve` | `(query, modality?, k?) → hits[]` | unit_id, text, score, path | read |
| `get_unit_text` | `(unit_id) → text` | full text or hint-error | read |
| `get_image` | `(unit_id) → path` | processed image path | read |
| `corpus_stats` | `() → summary` | counts, versions (resource) | read |

Four tools. Every one maps to a Week-09 tested function. The surface is
*frozen*: new tools require a v2 and a revisit trigger — the same
decision-memo discipline as encoders.

## 2. Why four is enough (and five is a decision)

| Candidate tool | Verdict | Reason |
|---|---|---|
| `compute_margin(units)` | defer | model can compute from returned text; add when traces show repeated arithmetic failures |
| `write_note` | v2 + HITL | write access = new failure class (W9 battery) |
| `history_page` | host-side, not MCP | memory belongs to the host (file 02) |
| `search_web` | out of scope | corpus-bound capstone; new data source = new eval |

The discipline: tools are added when *trajectories prove the gap*
(file 04's trace mining), not when imagination does. Each addition
carries: schema, error contract, battery cases (both tiers), and a
version bump.

## 3. The versioned surface contract

```text
Tool surface v1 (2026-09-05):
  retrieve, get_unit_text, get_image, corpus_stats (resource)
  All read-only. Errors = isError + hint text.
  Client minimum: initialize version assert, tool-list diff on connect.

v2 policy: additive-only (new tools). Breaking changes = v3, new endpoint.
```

The client asserts the version at `initialize` and diffs `tools/list` —
a server that adds or removes tools unannounced fails the connection
check, not the demo.

## 4. Security posture, stated once

| Threat | Control |
|---|---|
| injection via retrieved text (W9) | firewall at prompt-build, host-side |
| prompt data exfiltration via tools | read-only + no network egress in tools |
| tool arg abuse | jsonschema + server-side revalidation |
| runaway agent | episode budget (host) + timeouts (server) |

The server revalidates arguments even though the client does — the
client is the model's side of the wire, and the model is exactly the
component you do not fully trust.

## 5. The surface in one page — the client-facing contract

```text
GEF C7 tool surface v1 (2026-09-05)
  server: gef-c7-rag, version 1.0.0, read-only
  tools:
    retrieve(query, modality?, k?) -> hits[]      scores + ids + paths
    get_unit_text(unit_id)         -> text        hint-error on unknown
    get_image(unit_id)             -> path        processed image path
  resources:
    corpus://stats                 -> summary     counts, versions
  errors: isError + hint text (shape of valid input + next action)
  limits: k ∈ [1,20] server-enforced; timeouts per tool
  client minimum: version assert at initialize; tools/list diff on connect
```

This page is what any future client (Week 11 UI, Week 12 evaluator,
another agent) reads instead of your code. It is generated where possible
(from the registry) and frozen by the same decision-memo discipline as
encoders and boundaries.

## Exercises

1. Freeze your surface: write the four-tool table with your real
   signatures; mark any deviation from Week-09 contracts as a bug.
2. Revalidation drill: call the server directly with schema-valid but
   semantically hostile args (`k=10_000`, `unit_id="../../etc/passwd"`);
   verify the server clamps or rejects — client trust is zero.
3. Version drill: bump the server's tool list by one tool without
   bumping the version; verify the client's diff check fails the
   connection.
4. Contract-page drill: regenerate §5 from the server's actual
   `tools/list` output; diff against the hand-written page — they must
   agree, or the page is fiction.

## Pitfalls

- Surfaces that grow per demo need — v2 policy or the battery coverage
  rots within two weeks.
- Trusting client-side validation — the server revalidates; the wire is
  hostile territory.
- Tools that log or return absolute paths — server responses are
  model-visible; keep them repo-relative and sanitized (W9 firewall).

## Resources

- Your Week-09 tool contract (the v1 source); file 04 — the harness that
  measures this surface.
- MCP spec: tool result structure, resource URIs, initialize handshake.
