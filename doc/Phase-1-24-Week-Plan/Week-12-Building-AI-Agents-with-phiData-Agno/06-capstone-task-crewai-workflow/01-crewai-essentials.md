# CrewAI Essentials — Roles, Tasks, Crew, Process

**What you'll learn:** the four objects (Agent, Task, Crew, Process), how
a crew executes, and the mapping onto your W10/W11 vocabulary.

## 1. The four objects

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="Corpus Researcher",
    goal="Find and cite corpus evidence for the query",
    backstory="Meticulous analyst who reads sources fully before answering "
              "and never invents numbers.",
    tools=[retrieve_tool, get_unit_text_tool],
    llm="pinned-model-id",
)

research_task = Task(
    description="Research: {query}. Return evidence with unit_ids.",
    expected_output="Markdown: findings + a citations list of unit_ids.",
    agent=researcher,
)

writer = Agent(role="Answer Writer",
               goal="Compose a grounded answer from research",
               backstory="Precise writer who only uses supplied evidence.")
write_task = Task(description="Answer using the research.",
                  expected_output="Grounded answer with [unit_id] citations.",
                  agent=writer, context=[research_task])

crew = Crew(agents=[researcher, writer],
            tasks=[research_task, write_task],
            process=Process.sequential,
            verbose=True)

result = crew.kickoff()
print(result.raw)
```

| CrewAI object | Your W10/W11 equivalent |
|---|---|
| `Agent(role, goal, backstory)` | instructions (constitution) — decomposed into three prompts |
| `Task(description, expected_output)` | a pipeline stage's contract |
| `Crew(process=...)` | the loop + topology (handoff vs chain) |
| `context=[...]` | state passing between tasks (W11 file 03-04) |

## 2. Role/goal/backstory as prompts

The trio is prompt engineering with fixed slots:

| Slot | Function | W10 equivalent |
|---|---|---|
| `role` | identity → behavioral frame | agent `name` + job line |
| `goal` | the success criterion | the task contract's "done" |
| `backstory` | persona, *style*, and constraints | constitution excerpts |

The discipline carries over: backstories that state constraints
("never invents numbers") are constitution rules in costume — and they
get the same battery treatment (a case per rule). A backstory that is
flavor text ("you love coffee") is noise; W10 file 05's rules apply to
the slots.

## 3. Task wiring: context and expected_output

| Task field | Function | Tie-in |
|---|---|---|
| `context=[task_a]` | prior task outputs injected | W11 chaining's typed seam |
| `expected_output` | the contract the writer agent sees | your typed-output fields, in prose |
| `output_pydantic` (optional) | typed task output | W11 `output_type`, task-level |

`context` is how the writer sees the research — the summary pattern
(W11 file 03-04) applies: pass the artifact, not the full transcript.

## 4. Crews vs your topologies

| CrewAI | W11 equivalent |
|---|---|
| sequential process | chaining (fixed order) |
| hierarchical process | manager delegation (agents-as-tools) |
| `Flow` (start/listen) | your hand-rolled chain controller |
| `kickoff()` | `Runner.run` |

Flows are CrewAI's explicit orchestration layer — your W11 chain code,
formalized with a state object. The mapping table (file 04) completes
the three-framework picture.

## Exercises

1. Rebuild the W11 chain (extractor → answerer) as a two-agent crew;
   run the eval set; compare outcomes and tokens vs both prior
   implementations.
2. Backstory drill: write one *constraint-bearing* backstory ("never
   invents numbers"); verify the numeric battery case passes through
   the crew.
3. Mapping freeze: extend the W12 completion table with CrewAI rows;
   cite one run per cell.

## 5. CrewAI's mental model in one sentence

A crew is a *typed chain where the types are role-voices*: tasks are the
stages, context is the seam, and the process keyword chooses whether the
order is your list or a manager's plan. Every concept you built in W10
and W11 exists here under a friendlier name — which is exactly why the
comparison table (file 04) gets filled with runs instead of vibes.

## Pitfalls

- Backstories that are pure flavor — the slots are prompts; write
  constraints into them or they are noise.
- `context` omitted on dependent tasks — the writer guesses; wire the
  research task explicitly.
- `verbose=True` in production traces — it is a debug flag; your harness
  remains the system of record.