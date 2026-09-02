# 02 — Tools & Memory: The Agent's Hands and Notes

> Week 10 index: [README.md](README.md)

**Session 1 topics:** *Building Agents: Tools, Memory.*

---

## What you'll learn

- The function-calling protocol end to end: schema → model decision → your execution → observation
- Tool design rules that make agents reliable (naming, typing, idempotency, error contracts)
- Memory taxonomy: history, scratchpad, episodic/semantic — and what each is for
- Context-window budgeting across an agent run

## 1. Tool calling: the complete protocol

Function calling is a 4-step contract (file 01 implemented it; here's each step's engineering):

```text
1. SCHEMA    you send tool names + JSON schemas with every request
2. DECISION  the model replies with tool_calls[]: name + JSON arguments
3. EXECUTION you validate args, run the python function, catch errors
4. OBSERVATION you append a role:"tool" message; the model reads it next turn
```

The critical property: **the model never executes anything** — it emits a *proposal*. Your code is the executor; that's where validation and security live (the W3-02 privilege-separation rule, now concrete).

### A tool registry that validates

```python
import json, inspect
from jsonschema import validate as js_validate   # pip install jsonschema

class ToolRegistry:
    def __init__(self):
        self._fns, self._schemas = {}, {}

    def tool(self, schema: dict):
        def deco(fn):
            self._fns[schema["function"]["name"]] = fn
            self._schemas.setdefault("tools", []).append(schema)
            return fn
        return deco

    def execute(self, name: str, args_json: str) -> str:
        try:
            args = json.loads(args_json or "{}")
            entry = next(t for t in self._schemas["tools"]
                         if t["function"]["name"] == name)
            js_validate(args, entry["function"]["parameters"])     # 3. validate FIRST
            result = self._fns[name](**args)
            return json.dumps({"ok": True, "result": result}, default=str)[:2000]
        except Exception as e:                                     # errors become observations
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})

registry = ToolRegistry()

@registry.tool({"type": "function", "function": {
    "name": "sql_query", "description": "Read-only SELECT over capstone tables",
    "parameters": {"type": "object",
                   "properties": {"question": {"type": "string"}},
                   "required": ["question"]}}})
def sql_query(question: str) -> dict:
    return answer_structured(question)        # W6-03 (validates SQL again internally)
```

Three layers of defense now stack: prompt rules (W3-02) → this validator → the read-only DB user (W6-02). The agent can try anything; the walls hold.

### Tool design rules (each one prevents a failure class)

| Rule | Why |
|---|---|
| verb-y names, one capability each (`search_knowledge`, not `do_stuff`) | the model picks tools by *name+description* |
| docstring/description = the LLM's only manual — write for it | bad description = wrong selection |
| typed args with constraints (`k: int, minimum 1, maximum 20`) | validator can catch nonsense |
| **idempotent where possible** (same call → same effect) | agent retries shouldn't double-charge |
| structured return (`{"ok", "result", "caveat"}`) | the model can branch on failure |
| error messages that say what to *do* ("unknown column 'revnue'; did you mean 'revenue'?") | enables self-repair (W6-03's loop, generalized) |

## 2. Memory — the taxonomy

| Memory | Holds | Lifetime | Implementation |
|---|---|---|---|
| **History** | the conversation turns | the session | messages list (W1-07) |
| **Scratchpad** | the agent's plan/notes within one task | one run | a `notes` tool or scratchpad message |
| **Episodic** | past runs/outcomes ("last time X failed") | across sessions | JSONL → retrieval (W4) |
| **Semantic** | distilled knowledge from episodes | across sessions | summarized facts, re-embedded |
| **User profile** | stable preferences | across sessions | key-value store, loaded in system prompt |

Framework mapping (you'll see these names again in W11/W13): SDK *sessions* = history; LangGraph *checkpoints* = scratchpad + episodic; every "agent memory" product is one of these rows.

### Scratchpad that works

```python
@registry.tool({"type": "function", "function": {
    "name": "save_note", "description": "Persist an intermediate finding for later steps",
    "parameters": {"type": "object",
                   "properties": {"note": {"type": "string"}}, "required": ["note"]}}})
def save_note(note: str) -> str:
    scratchpad.append(note)
    return f"saved ({len(scratchpad)} notes)"

@registry.tool({"type": "function", "function": {
    "name": "read_notes", "description": "Read all saved notes",
    "parameters": {"type": "object", "properties": {}}}})
def read_notes() -> str:
    return "\n".join(f"- {n}" for n in scratchpad) or "(empty)"
```

Why it matters: long trajectories exceed what the model reliably "remembers" from step 3 — explicit notes beat hoping. (Context decay across turns is the phenomenon; the scratchpad is the fix.)

### Episodic memory from your logs

Week 4's habit of logging everything to JSONL becomes memory:

```python
def remember_run(goal, steps, outcome):                 # call in run_agent's finally block
    with open("data/agent_memory.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"goal": goal, "n_steps": len(steps),
                            "outcome": outcome}) + "\n")

def recall_similar(goal, k=3):                          # semantic memory = vector search
    emb = encode([goal])[0]
    return top_k_over_jsonl("data/agent_memory.jsonl", emb, k)
```

Inject `recall_similar(goal)` into the first system message: "Previously similar tasks: … lessons: …". Cheap, and genuinely useful once >50 runs exist.

## 3. Context budgeting for agent runs

Every loop iteration *re-appends the full history* (W1-07's truth, now multiplied): system + schemas + goal + N×(call + observation). Budget per layer:

```python
def context_report(messages, enc):
    rows = [(m["role"] if m.get("role") else "assistant",
             len(enc.encode(str(m.get("content", "") or m.get("function", "")))))
            for m in messages]
    return sorted(rows, key=lambda r: -r[1])[:5]        # biggest consumers first
```

Rules:

- **Truncate observations** at write time (`[:2000]` above) — old, huge tool results are the usual context killers
- **Compress the middle**: after 6+ steps, summarize earlier observations into the scratchpad, drop the raw turns
- **Schemas are fixed cost** (~300–800 tokens) — more tools = less room for everything else; keep the registry lean per task
- **Cap and fail loudly** at a token ceiling (`MaxTurnsExceeded`'s cousin)

## Exercises

1. Refactor file 01's loop to use `ToolRegistry`. Add `jsonschema` validation; feed it a wrong-typed call and log the observation the model receives.
2. Give the agent the scratchpad tools; give it a 3-source question ("compare X in docs, count Y in DB, note both, then answer"). Trace when it uses `save_note`.
3. Build `context_report`; run a 6-step trajectory and print the top-5 consumers. Then halve observation truncation and re-measure.
4. Write `remember_run` + `recall_similar`; run 15 trajectories, then one *repeat* goal — does the recalled lesson change the trajectory (fewer steps)?
5. Error-contract drill: make three tools raise distinct errors (bad column, empty result, timeout) — rewrite each error message into "what to do next" form and measure: does the agent recover in the next step?

## Pitfalls

- **Descriptions written for humans, not the model** — "Queries the DB" tells the model nothing about *when* to choose it
- **Mutable global state in tools** — two parallel runs share a scratchpad; scope state per run
- **Trusting `tool_calls` args as typed** — JSON in, JSON out; validate or the DB validates *for you*, rudely
- **Memory that never forgets** — unbounded history/scratchpad = context explosion; every memory needs an eviction policy
- **Secrets reachable as tools** — a `run_shell` tool is an injection目标 (W3-02); expose the *minimal* verbs, read-only first

## Resources

- OpenAI, [Function calling guide](https://platform.openai.com/docs/guides/function-calling) — the protocol reference
- Anthropic, *Building effective agents* — the memory/tool design sections
- Wu et al., *Memory in LLM Agents* survey (arXiv 2404.13501) — the taxonomy formalized
- LangGraph [persistence docs](https://langchain-ai.github.io/langgraph/concepts/persistence/) — checkpoint = scratchpad+episodic, for the vocabulary
