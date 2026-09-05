# Deep-Dive: CrewAI — Roles, Tasks, Crews, Processes

Parent overview: [`../06-capstone-task-crewai-workflow.md`](../06-capstone-task-crewai-workflow.md)

CrewAI is the role-first framework: agents defined by role/goal/backstory,
tasks with expected outputs, crews with sequential or hierarchical
processes. This subfolder covers the essentials, least-privilege role
design, the process choice measured, and the comparison against your W11
SDK build.

API verified against context7 id `/websites/crewai`.

## File map

| File | What it covers |
|---|---|
| [`01-crewai-essentials.md`](01-crewai-essentials.md) | Roles / tasks / crew / process |
| [`02-role-design.md`](02-role-design.md) | Least-privilege specialist split |
| [`03-process-choice.md`](03-process-choice.md) | Sequential vs hierarchical, measured |
| [`04-comparison-vs-w11.md`](04-comparison-vs-w11.md) | Same cases, all three frameworks |
| [`exercises.md`](exercises.md) | Expanded exercises with worked approaches |

## Study order

1. `01-crewai-essentials.md` — the four objects, in code.
2. `02-role-design.md` — role/goal/backstory as prompts, not decoration.
3. `03-process-choice.md` — the orchestration decision, with numbers.
4. `04-comparison-vs-w11.md` — the three-framework final table.

## Prerequisites

- [`../01-agno-introduction/03-framework-mapping.md`](../01-agno-introduction/03-framework-mapping.md)
  — the mapping habit.
- [`../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/03-multi-agent-orchestration/`](../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/03-multi-agent-orchestration/)
  — the topology concepts CrewAI re-expresses.
