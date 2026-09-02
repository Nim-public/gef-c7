# 02 — Grammar-Constrained Decoding (Outlines)

> E6 index: [README.md](README.md)

**Core topic:** *Outlines — schema-as-grammar decoding that guarantees valid JSON/regex/enum outputs.*

---

## What you'll learn

- How grammar-constrained decoding works (masking invalid tokens at every step)
- Outlines: Pydantic models, enums, regex, JSON-schema grammars — with local and vLLM models
- Guaranteed-valid vs prompt-hoped-valid: the measured difference
- The quality question: what constrained decoding can still get wrong

## 1. The mechanism (why it's a guarantee)

W1-07's sampling picks from the model's next-token distribution. Grammar-constrained decoding **masks every token that would violate the grammar** before sampling — at *every* step. A JSON string can never break mid-way because the only continuations offered are grammar-valid ones.

Compare the three generations of structured output you've used:

| Generation | Mechanism | Failure mode |
|---|---|---|
| W3-01 prompt hope | "return JSON only" | malformed JSON, hallucinated keys |
| W11/W14 `output_type` / `with_structured_output` | parse + **retry** on failure | latency spikes, occasional final failure |
| **Grammar-constrained** (Outlines/vLLM guided) | token masking | syntactically *always* valid — content quality is the only open risk |

## 2. Outlines in practice

```powershell
pip install outlines
```

```python
import outlines
from transformers import AutoModelForCausalLM, AutoTokenizer
from pydantic import BaseModel
from typing import Literal

class Route(BaseModel):
    category: Literal["billing", "technical", "account"]
    confidence: float
    needs_human: bool

model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct"),
    AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct"),
)

result = model(
    "Classify this ticket: 'I was charged twice this month.'",
    output_type=Route, max_new_tokens=80,
)
print(Route.model_validate_json(result))
# Route(category='billing', confidence=0.9, needs_human=False) — parse guaranteed
```

Grammar types Outlines supports: **Pydantic models, TypedDict, enums, Literal types, regex strings, JSON Schema, and plain types** (`int`, `list[str]`). The grammar compiles to a token-mask FSM over the model's vocabulary.

Serving engines: vLLM exposes guided decoding (`guided_json`/Outlines integration — file 15-03's server gains the guarantee), and llama.cpp/Ollama support GBNF grammars — the same guarantee across your serving tiers.

## 3. Where guarantees change your architecture

| Before (parse+retry) | After (grammar) |
|---|---|
| retry loops + fallback chains (W14-01) | delete the retry for *syntax* — keep for *content* |
| `"return JSON only"` prompt lines | replaced by the grammar (shorter prompts) |
| schema-drift bugs (W16-01 versioning) | schema is the grammar — single source of truth |
| enum drift (categories renamed in prompts) | `Literal` types — compile-time-checked |

The W13 ticket router's classification node (W13-03's `Classification`), the W12-04 analytics extraction (file 04), and every tool-call argument can become grammar-guaranteed. What remains your job: **the *content*** — a valid-JSON answer can still cite wrong documents or invent numbers. The W5-04/W12-04 verification stack stays.

## 4. The quality question (guaranteed ≠ correct)

Grammar guarantees syntax. It can still produce:

- **Valid JSON with wrong values** — hallucinated numbers, mislabels (W12-04's checks stay)
- **Grammar-valid but semantically empty** — all-null fields (add min-properties/required constraints, and verify)
- **Over-constrained loops** — a grammar demanding data the model doesn't have can push it into degenerate repetition (raise `max_new_tokens`, loosen the schema)
- **Speed changes** — masking adds per-step overhead; on small models it's negligible, measure on yours (file 04's lab)

## Exercises

1. Convert W13-03's `Classification` node to Outlines; run the 20-ticket routing eval — parse-failure rate before (prompt+retry) vs after (grammar). Should be 0 vs some%.
2. Enum-drift test: rename a category in the Pydantic model and rerun old prompts — what happens at generation time vs what happened with prompt-based enums?
3. Regex grammar: force an order-id output as `[A-Z]{2}-\d{4}` — generate 20, verify all match. Then ask for an impossible pattern (10-digit) — what does the model do under a grammar it can't satisfy?
4. Speed benchmark: constrained vs free decoding tokens/s on a 0.5B model, 200-token outputs. Overhead acceptable for guaranteed validity?
5. Content-quality check: grammar-guaranteed extraction (file 02-03's invoice contract) with the W12-04 `numbers_supported` verification — still needed? (Yes — demonstrate with one planted hallucination.)

## Pitfalls

- **Grammar as truth serum** — guaranteed JSON of guaranteed *garbage*; content verification layers stay (W5-04/W12-04)
- **Over-constrained schemas** — required fields the model can't see in context → repetition loops; make optional fields optional
- **Big vocabularies, big masks** — FSM compilation cost grows with schema complexity; cache compiled grammars
- **Provider mismatch** — grammar support varies (vLLM guided, llama.cpp GBNF, API-side structured outputs); test on *your* serving path (W15-03)
- **Forgetting the model still needs the information** — a grammar can't extract what isn't in the prompt/context (W4-01's insufficiency rule, restated)

## Resources

- [Outlines docs](https://dottxt.github.io/outlines/) — models, output types, vLLM integration (this file's source)
- Willard & Louf, *Efficient Guided Generation for LLMs* — the FSM/masking paper
- vLLM [structured outputs](https://docs.vllm.ai/en/latest/features/structured_outputs.html) · llama.cpp [GBNF grammars](https://github.com/ggerganov/llama.cpp/blob/master/grammars/README.md)
- W14-01 (structured output before grammars), W12-04 (content verification) — the before/after
