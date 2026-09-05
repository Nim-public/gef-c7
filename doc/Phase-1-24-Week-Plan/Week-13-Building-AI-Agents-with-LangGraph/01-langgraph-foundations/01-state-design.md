# State Design — TypedDict, Pydantic, Reducers

**What you'll learn:** the state schema as the graph's contract: what
TypedDict gives you, when Pydantic earns its validation, and reducers —
the merge policy for concurrent updates.

## 1. The two schema styles

```python
from typing_extensions import TypedDict, Annotated
import operator
from pydantic import BaseModel

class GraphState(TypedDict):
    query: str
    retrieved: Annotated[list[str], operator.add]   # reducer: append
    answer: str                                     # default: overwrite

class PydState(BaseModel):
    query: str
    retrieved: list[str] = []
    answer: str = ""
```

| Style | Validation | Reducers | Use |
|---|---|---|---|
| TypedDict + Annotated | none (trust) | explicit, per-field | default; fast |
| Pydantic model | full | via `Annotated` too | when node outputs need validation |

The reducer is the state's merge policy: when a node returns
`{"retrieved": [...]}`, the annotated field *appends*; unannotated
fields *overwrite*. Choosing reducers is designing the state's algebra —
and `operator.add` on lists covers most agent needs (accumulate
retrievals, errors, citations).

## 2. Nodes return partial state

```python
def retrieve(state: GraphState) -> dict:
    hits = hybrid_retrieve(state["query"])
    return {"retrieved": [h.unit_id for h in hits]}   # partial update only

def answer(state: GraphState) -> dict:
    ctx = "\n".join(state["retrieved"])
    return {"answer": llm_answer(state["query"], ctx)}
```

Nodes return *only what they changed* — the framework merges via the
reducers. This is the W11 typed-output seam, generalized: every node's
return type is a contract, and the reducers define how contracts
compose.

## 3. Designing the state (the W10 memory rules, graph edition)

| Field | Reducer | Why |
|---|---|---|
| `query` | overwrite | single source |
| `retrieved` | append | accumulate across hops |
| `errors` | append | the loop detector's substrate |
| `attempt_count` | overwrite (or custom) | bounded cycles (file 03) |
| `answer` | overwrite | last writer wins |

The fitter's rules apply between nodes: state grows, context shrinks —
the W10 budget discipline survives inside LangGraph as a *node* (a
trim node between heavy steps).

## 4. When Pydantic state earns its cost

| Signal | Choose |
|---|---|
| nodes return untrusted/LLM-shaped data | Pydantic (validation at merge) |
| state fields feed guardrails | Pydantic (validators run) |
| internal bookkeeping only | TypedDict |

```python
from pydantic import BaseModel, field_validator

class VerifiedState(BaseModel):
    answer: str
    citations: list[str] = []

    @field_validator("citations")
    @classmethod
    def citations_known(cls, v, info):
        known = info.context.get("retrieved", set()) if info.context else set()
        bad = [c for c in v if c not in known]
        if bad:
            raise ValueError(f"phantom citations {bad}")
        return v
```

## Exercises

1. Build the W10 agent's state as TypedDict with three reducers; run one
   multi-hop query; verify `retrieved` accumulates and `answer`
   overwrites.
2. Pydantic drill: port the citation validator into the state; feed a
   phantom citation; the merge must raise.
3. Reducer drill: write a custom `bounded_add` (append, cap at 20) —
   the fitter's cap, expressed as a reducer.

## Pitfalls

- Forgetting the reducer and losing accumulated lists — the default is
  overwrite; the classic silent state bug.
- Pydantic state without context wiring — validators need the known-ids
  set; `info.context` is not magic.
- State fields that duplicate each other (`retrieved` vs `hits`) — one
  field, one meaning; the W10 memory-tier rule.

## Resources

- LangGraph graph API: state schemas, reducers (context7:
  `/websites/langchain_oss_python_langgraph`).
- [`../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/03-structured-output.md`](../../Week-11-Building-AI-Agents-with-OpenAI-Agents-SDK/01-agents-sdk-quickstart/03-structured-output.md)
  — the typed-output discipline this generalizes.