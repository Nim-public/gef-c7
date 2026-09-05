# Prompt Templates — Versioned, Validated, File-Loaded

**What you'll learn:** prompts as artifacts: `ChatPromptTemplate` with
typed variables, version-pinned loading from files, and the validation
that catches missing variables at import time instead of at 2 a.m.

## 1. The template, with its contract

```python
from langchain_core.prompts import ChatPromptTemplate

GROUNDING_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You answer ONLY from the provided context.\n"
     "Context:\n{context}\n"
     "If the context is insufficient, say: 'The corpus does not contain "
     "this.' Never use outside knowledge. Cite [unit_id] per claim."),
    ("user", "{query}"),
])

prompt = GROUNDING_PROMPT.invoke({
    "context": "[u042] margins rose...", "query": "Why did margin drop?"
})
# prompt.to_messages() → [SystemMessage, HumanMessage]
```

| Property | Enforced by |
|---|---|
| variables declared in braces | template compile: missing var → error at invoke |
| no undeclared extras | `invoke` with unknown keys → error |
| version | the constant name + your pin note (`pv3`) |

The W10 constitution pattern, as a template: the rules live in the
system message, the variable slots are explicit, and *both* fail loudly
when misused — template errors move from runtime to import time when the
template is loaded from a file and validated at startup.

## 2. File-loaded, version-pinned

```python
# prompts/grounding_pv3.yaml
# system: |
#   You answer ONLY from the provided context...
#   Context:
#   {context}
# user: "{query}"

import yaml
from langchain_core.prompts import load_prompt

def load_versioned(name: str, version: int) -> ChatPromptTemplate:
    path = f"prompts/{name}_pv{version}.yaml"
    return ChatPromptTemplate.from_messages([
        ("system", yaml.safe_load(open(path, encoding="utf-8"))["system"]),
        ("user", yaml.safe_load(open(path, encoding="utf-8"))["user"]),
    ])

prompt = load_versioned("grounding", 3)
```

| Rule | Why |
|---|---|
| prompt files carry `pvN` in the name | the settings-version discipline |
| templates validated at startup | missing variables fail before the demo |
| template changes bump the version | W10's constitution-version rule |

The startup validation:

```python
def validate_template(t: ChatPromptTemplate, sample: dict) -> None:
    t.invoke(sample)      # raises on missing/extra variables — at import
validate_template(GROUNDING_PROMPT, {"context": "x", "query": "y"})
```

## 3. Few-shot and partial variables

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"q": "total revenue Q3?", "a": "Use the SQL tool: numbers come from "
     "tables, never from memory."},
    {"q": "what does the chart say?", "a": "Use retrieve, then get_unit_text."},
]
few_shot = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([
        ("human", "{q}"), ("ai", "{a}")]),
    examples=examples,
)
full = ChatPromptTemplate.from_messages([
    ("system", "You are a corpus agent. Learn from these examples."),
    few_shot,
    ("user", "{query}"),
])
```

Few-shot examples are the W9 router's calibration data, promoted into
the prompt — the same rows that trained your regex, now teaching the
model. Keep them versioned with the template (`pvN` includes examples).

## 4. The prompt inventory (the pin note's page)

| Prompt | Version | Variables | Battery case |
|---|---|---|---|
| grounding | pv3 | context, query | absent-fact refusal |
| classifier | pv2 | ticket | urgency inflation |
| repair note | pv1 | failure, attempt | loop-break drill |

The W10 prompt-architecture diagram (file 05-07), one table — every
prompt you own, versioned, with its battery case. The pin note grows one
row per template.

## Exercises

1. Port your W10 constitution into a versioned `ChatPromptTemplate`;
   validate at startup; run the insufficiency battery against it.
2. Few-shot drill: add two routing examples; re-run the route battery;
   report the delta (or the tie).
3. Version drill: bump the grounding prompt to pv4 (one wording change);
   the battery must still pass; the trajectory rows stamp pv4.

## Pitfalls

- Templates loaded without startup validation — the missing-variable
  error fires mid-demo instead of at import.
- Few-shot examples that contradict the constitution — the model follows
  the *examples* over the rules when they conflict; keep them consistent.
- Prompt versions unstamped in trajectories — the W10 version discipline
  applies to prompts exactly like hints and rubrics.