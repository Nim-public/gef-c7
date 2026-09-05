# Deep-Dive: Tools, Handoffs & Guardrails

Parent overview: [`../02-tools-handoffs-guardrails.md`](../02-tools-handoffs-guardrails.md)

This subfolder ports your W10 tool discipline onto SDK primitives:
`function_tool` (schemas from signatures, `is_enabled` gating), handoffs
(control transfer as a tool call), input/output guardrails as tripwires,
and the W9 battery mechanized as pytest.

## File map

| File | What it covers |
|---|---|
| [`01-function-tool.md`](01-function-tool.md) | Schemas from signatures, failure_error_function, is_enabled |
| [`02-handoffs.md`](02-handoffs.md) | Control transfer, descriptions, last_agent |
| [`03-input-guardrails.md`](03-input-guardrails.md) | Tripwires, judge-agents, exceptions |
| [`04-output-guardrails.md`](04-output-guardrails.md) | Citation/schema validation as tripwires |
| [`05-battery-as-pytest.md`](05-battery-as-pytest.md) | The W9 battery, mechanized |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-function-tool.md` — your registry, expressed as decorators.
2. `02-handoffs.md` — the router's job, as a primitive.
3. `03-input-guardrails.md` — tripwires before the model answers.
4. `04-output-guardrails.md` — your audits as output gates.
5. `05-battery-as-pytest.md` — everything above, under CI.

## Prerequisites

- [`../01-agents-sdk-quickstart/`](../01-agents-sdk-quickstart/) — anatomy, loop, typed outputs.
- [`../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/02-tool-registry.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/02-tools-and-memory/02-tool-registry.md)
  — the contracts being ported.
