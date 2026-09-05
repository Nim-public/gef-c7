# Agno Agent Structure — Model, Instructions, Tools, Knowledge

**What you'll learn:** the four core Agent fields, how they map to your
hand-rolled components, and the Agno-specific behaviors (team roles,
structured output, tool flags) that surround them.

## 1. The four fields, mapped to W10

```python
from agno.agent import Agent
from agno.models.openai import OpenAIResponses

agent = Agent(
    model=OpenAIResponses(id="gpt-5.2"),      # 1. model: provider-wrapped
    instructions=[                            # 2. rules (list or str)
        "Answer only from tool results; cite unit_ids.",
        "If tools find nothing, say not found.",
    ],
    tools=[retrieve_tool, get_unit_text_tool],  # 3. callables or Toolkits
    knowledge=knowledge,                      # 4. vector-db-backed corpus
    markdown=True,
    show_tool_calls=True,                     # audit trail in output
)
```

| Agno field | W10 equivalent | Notes |
|---|---|---|
| `model` | your `llm` wrapper | provider classes (`OpenAIChat`, `Claude`) |
| `instructions` | constitution string | list-of-rules is idiomatic |
| `tools` | `ToolRegistry` | plain functions, `@tool`, or `Toolkit` classes |
| `knowledge` | LanceDB index (W09) | optional; enables agentic RAG (`search_knowledge=True`) |
| `output_schema` | `output_type` (W11) | Pydantic, same strictness idea |
| `session_id` / `db` | `SQLiteSession` | persistence via `SqliteDb`/`PostgresDb` |

The mapping is nearly 1:1 with the OpenAI Agents SDK — the differences
are packaging (models as fields, knowledge as a field) and the built-in
Team/Workflow layer (file 03's comparison).

## 2. Structured output, Agno edition

```python
from pydantic import BaseModel, Field

class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float = Field(ge=0, le=1)

agent = Agent(
    model=OpenAIResponses(id="gpt-5.2"),
    tools=[retrieve_tool],
    output_schema=Answer,          # response.content is an Answer instance
)
response = agent.run("Which chart shows Q3 margin?")
print(response.content.citations)  # typed — no parsing
```

Identical contract to W11's `output_type`: Pydantic model in, typed
object out. Your citation validator ports directly (same W9-04 logic,
same field names) — the audit logic is framework-independent.

## 3. The audit surface: show_tool_calls, debug_mode

```python
agent = Agent(..., show_tool_calls=True, debug_mode=True)
response = agent.run(query)
print(response.tools)        # tool calls made this run
print(response.metrics)      # token usage per run
```

| Field | W10 equivalent |
|---|---|
| `response.tools` | trajectory trace's tool entries |
| `response.metrics` | token ledger (fitter) |
| `debug_mode=True` | verbose logging during development |

The trajectory schema (W10 file 04) maps onto these response fields —
your harness survives a framework swap because the *schema*, not the
capture mechanism, was the contract.

## 4. Teams and roles — the preview of file 03

```python
from agno.team import Team

team = Team(
    name="Research Team",
    members=[news_agent, finance_agent],   # agents with `role` fields
    model=OpenAIResponses(id="gpt-5.4-mini"),
)
response = team.run("What are the trending AI stories?")
```

`Team.members` with per-agent `role` strings is Agno's delegation
topology — the manager-with-agents-as-tools pattern (W11 file 03) as a
first-class object. Full comparison in file 03.

## Exercises

1. Port your W10 agent to Agno's four fields; keep the same tools and
   constitution; run the battery — outcomes must match W10's.
2. Typed-answer port: `output_schema=Answer` with the citation validator;
   verify the phantom-citation case still fails.
3. Field-mapping freeze: write the W10→Agno table; mark SDK/manual per
   row (the fitter and gates remain manual — same as W11).

## Pitfalls

- Treating `knowledge=` as *automatically grounded* — the agent still
  chooses to search; the insufficiency battery (file 02) still applies.
- `instructions` as one long paragraph — the list-of-rules form is what
  Agno prompts best; split your constitution.
- Ignoring `show_tool_calls` in demos — the audit trail is one flag;
  turning it off hides the mechanism your reviewers grade.

## Resources

- Agno docs: Agent reference, structured output, Team (context7:
  `/agno-agi/docs`).
- [`../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/01-sdk-anatomy.md`](../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/01-sdk-anatomy.md)
  — the mapping habit this file repeats.