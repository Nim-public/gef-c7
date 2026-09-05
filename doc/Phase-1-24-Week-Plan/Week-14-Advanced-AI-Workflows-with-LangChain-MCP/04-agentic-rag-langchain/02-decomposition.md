# Decomposition — Sub-Question Generation

**What you'll learn:** multi-hop questions answered by *decomposing*
them into sub-questions, each routed to its source — the W13 supervisor
pattern, LCEL-shaped.

## 1. The decomposer

```python
class SubQuestions(BaseModel):
    parts: list[str] = Field(description="2-4 self-contained sub-questions")

decomposer = model.with_structured_output(SubQuestions)

def decompose(state) -> dict:
    subs = decomposer.invoke(DECOMPOSE_PROMPT.invoke({"query": state["query"]}))
    return {"sub_questions": subs.parts}
```

| Query | Sub-questions |
|---|---|
| "Compare our Q3 margin to industry average" | (a) our Q3 margin (SQL); (b) industry average (web) |
| "Why did revenue rise and what does the corpus say?" | (a) revenue change (SQL); (b) corpus explanations (vector) |

The decomposer is the multi-hop case's answer: one question, multiple
sources, each sub-question routed independently. The typed output
bounds the fan-out (2–4 parts) — the bound from W13 file 01-03.

## 2. The map step (Send, or sequential)

```python
def fan_out(state) -> list[Send]:
    return [Send("answer_part", {"sub_q": s}) for s in state["sub_questions"]]
```

Each sub-question routes independently (the three-source logic per
part); results aggregate via a reducer — the W13 map-reduce pattern,
applied to retrieval.

| Step | Mechanism |
|---|---|
| decompose | typed model call |
| fan out | `Send` per part |
| answer each part | the three-source routing |
| synthesize | final answer cites all parts |

## 3. The synthesis contract

```python
class SynthesisResult(BaseModel):
    answer: str
    parts: list[PartResult]      # each sub-answer with its source
    citations: list[str]

def synthesize(state) -> dict:
    parts = "\n".join(f"- {p.sub_q}: {p.answer} [{p.source}]"
                      for p in state["part_results"])
    return {"final": llm_synth(state["query"], parts)}
```

The synthesis cites *per part* — the compound answer's provenance is
the union of its parts' provenances. The pairing audit (W14 file 02-04)
extends to parts: every number in the final answer traces to a part's
check.

## 4. The decomposition battery

| Query | Expected parts | Sources |
|---|---|---|
| simple lookup | 1 (or no decomposition) | — |
| two-source compare | 2 | SQL + web |
| corpus-only multi-hop | 2–3 | vector |
| un-decomposable opinion | 0 parts → refuse | — |

The battery asserts the *decomposition quality*: parts must be
self-contained (no pronouns referencing siblings), each part routes to
a defensible source, and the synthesis cites both.

## Exercises

1. Build the decomposer; run the multi-hop cases; verify sub-questions
   are self-contained (no "it"/"that" references).
2. Fan-out drill: route 3 parts through different sources; verify the
   synthesis cites per part.
3. Refusal drill: an un-decomposable opinion question; zero parts and an
   honest refusal — the empty-parts path is a graded case.

## Pitfalls

- Sub-questions that reference each other — "self-contained" is the
  schema description's job; test it with pronoun cases.
- Decomposing single-hop questions — the overhead without benefit; the
  routing rule: decompose only multi-source/multi-hop.
- Synthesis that drops a part's citation — the pairing audit extends to
  parts; every number traces.