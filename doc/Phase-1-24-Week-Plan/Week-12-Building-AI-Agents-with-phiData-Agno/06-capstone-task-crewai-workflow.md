# 06 — Weekly Task: CrewAI Multi-Agent Workflow in Your Capstone

> Week 12 index: [README.md](README.md) · **Due: before Week 13 (by 5 Dec)**

**Task (from the schedule):** *Implement a CrewAI-based multi-agent workflow within your capstone project.*

The formal task introduces a *fourth* framework — CrewAI, the role-based multi-agent system — and asks for a **workflow**, not a demo: defined roles collaborating over your capstone data, evaluated against your W11 single agent.

---

## 1. Deliverable

```
crew/
  crew.py               # agents + tasks + crew assembly
  tools.py              # CrewAI tool wrappers (reuse your capstone systems)
  config/
    agents.yaml         # role/goal/backstory (CrewAI's declarative style)
    tasks.yaml
  eval/
    results.md          # crew vs W11 single-agent comparison table
  README.md             # role design, process choice, failure modes
```

Demo: one crew run on a real capstone question — showing per-role outputs, the final artifact, and the comparison numbers.

## 2. CrewAI essentials

```powershell
pip install crewai
```

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="Capstone Knowledge Researcher",
    goal="Find and cite documented facts about {topic} from the knowledge base",
    backstory="Meticulous analyst who grounds every claim in retrieved documents "
              "and never invents policy details.",
    tools=[search_knowledge_tool],          # your W9/W12 retriever as a CrewAI tool
    llm="gpt-4o-mini", verbose=True,
)

analyst = Agent(
    role="Data Analyst",
    goal="Answer numeric questions from capstone tables using read-only SQL",
    backstory="Ex-SQL analyst; shows the executed query and the row values for every number.",
    tools=[sql_query_tool],                 # W6-03 pipeline
    llm="gpt-4o-mini",
)

writer = Agent(
    role="Report Writer",
    goal="Compose a concise, cited answer from research findings and data",
    backstory="Technical writer who turns findings + numbers into 5-sentence answers with citations.",
)

task_research = Task(description="Find everything about: {question}",
                      expected_output="Bullet findings with [doc:id] citations",
                      agent=researcher)
task_analyze  = Task(description="Compute the numbers needed for: {question}",
                      expected_output="SQL + result rows + 3-sentence interpretation",
                      agent=analyst)
task_write    = Task(description="Write the final answer from the two work products.",
                      expected_output="Final answer with citations and the numbers used",
                      agent=writer, context=[task_research, task_analyze])

crew = Crew(agents=[researcher, analyst, writer],
            tasks=[task_research, task_analyze, task_write],
            process=Process.sequential, verbose=True)

result = crew.kickoff(inputs={"question": "Compare the refund policy with actual refund volumes."})
```

Concept mapping (your W11 vocabulary, crew edition):

| CrewAI | W11 SDK | W10 hand-rolled |
|---|---|---|
| `Agent(role, goal, backstory)` | `Agent(instructions)` | system message |
| `Task(description, expected_output, agent)` | a `Runner.run` stage | one loop pass / chain link |
| `Crew(process=sequential\|hierarchical)` | handoffs (implicit graph) / delegation-as-tools | your loop + router |
| `context=[tasks]` | explicit passing of `final_output` | scratchpad (W10-02) |
| `memory=True` | `Session` | episodic memory (W10-02) |

## 3. Design the roles (the graded thinking)

Role design = the W10-05 constitution, split by responsibility:

- **Researcher**: prose facts only; citation contract; insufficiency escape
- **Analyst**: numbers only; SQL audit trail; refuses prose questions
- **Writer**: synthesis only; **no tools** (grounded purely in the two work products — a built-in hallucination guard)

Guardrails in CrewAI: encode the W3-02/W10-04 rules into backstories ("never retry after denial", "cite or omit") — CrewAI's programmatic guardrails are thinner than the SDK's tripwires; say so in the README (framework comparison honesty).

## 4. Evaluation (graded — same rigor as W10)

Run **both** systems on the same 10 W10 cases:

| Metric | W11 single agent | W12 crew | Delta |
|---|---|---|---|
| success rate |  |  |  |
| steps/tokens per task |  |  |  |
| citation coverage |  |  |  |
| tool-error rate |  |  |  |
| wall-clock p95 |  |  |  |

Plus CrewAI-specific observations: does `hierarchical` (manager decides order) beat `sequential` on your tasks? What does `memory=True` change over repeated runs? Log with your W10-04 harness (crew runs produce their own logs — normalize to the same JSONL schema).

## 5. Rubric

| Area | Weight |
|---|---|
| Crew definition (roles, tasks, process, inputs) | 25% |
| Capstone tools wired into crew agents | 20% |
| Comparison table vs W11 (same cases, honest numbers) | 25% |
| README (role rationale, framework notes, failure modes) | 15% |
| Failure handling (insufficiency, injection battery through crew) | 10% |

## 6. README architecture section (answer explicitly)

1. **Role table**: role → goal → tools → why this split (least privilege, W10-04)
2. **Process choice**: sequential vs hierarchical — measured, not vibes
3. **Framework comparison**: CrewAI vs W11 SDK vs W12 Agno on your four framework needs (tools, orchestration, observability, guardrails) — one line each
4. **Failure modes** (≥3) from crew runs, with one-line diagnoses
5. **W13 bridge**: which crew behavior would you rather express as an *explicit graph* (LangGraph)? Name the nodes/edges you'd draw — that's Week 13's starting sketch

Bring the comparison table to Office Hours (3 Dec): the multi-agent frameworks all promise the same primitives with different ergonomics — your table is the evidence, and W13 turns the same workflow into an explicit graph.
