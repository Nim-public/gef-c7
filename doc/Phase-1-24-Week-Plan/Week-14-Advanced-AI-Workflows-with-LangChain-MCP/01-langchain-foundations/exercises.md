# Exercises — LangChain Foundations

Expanded set with worked approaches. The deliverable: your constitution
as versioned templates, an LCEL hot path, typed outputs, and the
`create_agent` port with the mapping table frozen.

## 1. Versioned prompts (from 01-prompt-templates)

**Task:** port the constitution and grounding prompt to YAML files with
`pvN` names; add startup validation; run the insufficiency battery
against the file-loaded template.

**Worked approach:** the startup validation is the load-bearing move —
`validate_template` at import turns missing-variable errors from demo
crashes into test failures. The battery re-run proves the port is
behavior-preserving.

**Pass criterion:** battery green on the file-loaded prompt; the version
stamped in trajectories; the pin note updated.

## 2. LCEL hot path (from 02-lcel-composition)

**Task:** express the W9 hot path as one LCEL chain; run 5 queries;
verify parity with the graph version; wire the resilience primitives
per the policy (retry reads, fallback models).

**Worked approach:** the guards live *inside* the runnables (`fetch_context`
keeps the W9 validators) — LCEL is wiring, not a new contract. The
resilience drill (killed primary) proves the ladder fires.

**Pass criterion:** 5/5 parity; the fallback event recorded; retry
counts in the ledger.

## 3. Typed chain (from 03-structured-output)

**Task:** port `Answer` + validator to `with_structured_output(include_raw=True)`;
store both raw and parsed in the trajectory row; run the phantom-citation
case.

**Worked approach:** the validator is the same W9-04 logic — only its
trigger moved to the chain boundary. The `raw` field keeps the token
accounting alive.

**Pass criterion:** phantom fails at validation; `raw.usage_metadata`
populates the ledger; the W11 parity test passes unchanged.

## 4. create_agent port (from 04-create-agent)

**Task:** port the agent to `create_agent` (tools, `response_format`,
checkpointer, retry middleware); run the 10-task eval; freeze the
four-column mapping table.

**Worked approach:** the port order from W11 file 06-01, fourth
application — tools, loop, typing, memory, battery after each. The
middleware port is the new step; the fault-injection test proves it.

**Pass criterion:** eval parity with W11; the mapping table frozen;
middleware fault-injection green.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Versioned prompts, startup validation | battery on pvN | 3 |
| LCEL parity + resilience drill | chain tests | 4 |
| Typed chain with raw forensics | structured tests | 3 |
| create_agent port + mapping freeze | port table | 4 |
| Pin note updated (pvN, versions) | pin note | 2 |

**Pass bar:** 13/16 to proceed to file 02 (the CSV analyzer). The port
(4-pointer) is the fourth framework re-expression — the battery is the
arbiter, as always.

## Pitfalls recap

- Templates without startup validation — mid-demo failures that a test
  would have caught.
- Retrying non-idempotent calls — reads retry, writes never; the policy
  decides, the primitive executes.
- Mapping tables without the fourth framework's column — four half-
  understood tools instead of one understood system.