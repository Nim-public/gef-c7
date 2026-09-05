# Grounding Rules — Instructions and the Insufficiency Battery

**What you'll learn:** grounding in an agentic-RAG world is not "retrieve
then answer" — the model can *skip* retrieval. The rules and the battery
must therefore test the skip case, not just the wrong-answer case.

## 1. The grounding constitution (knowledge edition)

```python
instructions=[
    "Answer ONLY from search_knowledge results. The knowledge base is "
    "your only source.",
    "If search returns nothing or is insufficient, say exactly: "
    "'The corpus does not contain this.' Never use outside knowledge.",
    "Cite unit_ids from search results for every factual claim.",
    "If the answer requires numbers not present in results, refuse "
    "the numeric claim — do not estimate.",
    "Multiple searches are allowed, but stop when results repeat.",
]
```

| Rule | Failure it prevents | Battery case |
|---|---|---|
| corpus-only | outside knowledge leaking | absent-fact query |
| insufficiency phrasing | confident wrong answers | 0-hit + near-miss cases |
| citation discipline | unverifiable claims | phantom-citation probe |
| numeric refusal | estimated figures | compute-from-prose probe |
| search stop | retrieval spirals | repeated-search detection |

The constitution is the W10 file 05 pattern, re-targeted: with agentic
RAG, the *decision to search* is part of the contract.

## 2. The insufficiency battery (new cases the skip-option creates)

| Case | Query | Required behavior |
|---|---|---|
| 0 hits | absent fact | "not found" phrasing, no citations |
| near-miss | related topic exists, exact fact doesn't | partial answer + explicit gap |
| partial hits | some numbers present | answer only what's cited |
| stale knowledge | answer exists but pre-dates a date | refuse with reason |
| skippable | chitchat / meta question | no search call at all |

```python
INSUFFICIENCY = [
    ("What was the CEO's 2019 bonus?", "not found", 0),
    ("What's in the corpus about budgets?", "partial+gap", "any"),
    ("What are the margins for FY2030?", "refuse", 0),
    ("Hello, who are you?", "no_search", 0),
]

@pytest.mark.parametrize("query,expected,ncites", INSUFFICIENCY)
def test_insufficiency(query, expected, ncites, agent): ...
```

The battery's new dimension: *the model's choice to not search* is
itself graded (case 4) — a chitchat query that fires retrieval is a
routing bug, not just a cost leak.

## 3. Grounding under agentic RAG: the new failure surface

| Failure | W9 fixed-RAG | W12 agentic-RAG |
|---|---|---|
| no retrieval | impossible (always runs) | **model skips the tool** |
| partial retrieval | fixed k | model stops early |
| query drift | your query rewriting | the model's search terms |

Each agentic failure has a rule (§1) and a trace signature (0 tool calls
on a factual query; search with k=2 and stop). The constitution rules
and the battery must evolve together — that is this file's point.

## 4. The grounding test loop

```text
1. battery red → identify broken rule (phrase it as a rule number)
2. reword the instruction → rerun THAT case + neighbors
3. full battery green → bump constitution version (cvN)
4. regression suite (W11 file 05) runs in CI
```

The maintenance loop is identical to W10's hint A/B: the instruction is
the artifact, the battery is the arbiter, the version stamp keeps trends
comparable.

## Exercises

1. Write your grounding constitution; run the insufficiency battery;
   produce the rule→case→result table.
2. Skip-detection drill: instrument search-call counts per query; verify
   chitchat fires 0 searches and absent-facts fire ≥1 — the routing
   behavior, measured.
3. Near-miss drill: craft 3 near-miss queries; verify partial answers
   carry an explicit gap statement — the hardest grounding case, graded.

## Pitfalls

- Batteries that test only wrong answers — the skip and partial cases
  are the new surface; the table above is the minimum.
- Grounding rules without version stamps — instruction edits become
  unattributable; `cvN` in every trajectory row.
- "Insufficient" answers that still hallucinate numbers — rule 4 exists
  for the exact moment the model *found* related prose and improvised a
  figure.

## Resources

- [`../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/01-agentic-constitution.md`](../../Week-10-Introduction-to-Agentic-AI-MCP/05-prompt-context-engineering-agentic/01-agentic-constitution.md)
  — the constitution pattern; file 02 here for the battery format.
- Your W9 grounding rules (the fixed-RAG version).