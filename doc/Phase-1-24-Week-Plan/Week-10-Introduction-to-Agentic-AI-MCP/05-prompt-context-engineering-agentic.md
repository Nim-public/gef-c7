# 05 — Prompt & Context Engineering for Agents

> Week 10 index: [README.md](README.md)

**Session 1 topic:** *Prompt & Context Engineering.*

---

## What you'll learn

- "Prompt engineering" vs "context engineering" — why agents need the second discipline
- The agentic system constitution: tool rules, stopping conditions, escalation
- Observation formatting: tool outputs are prompts too
- Context budget management across a run (the agent-specific version of W1-07)

## 1. Two terms, one discipline

- **Prompt engineering** (W3): crafting the *instructions* — static text you wrote
- **Context engineering**: curating *everything in the window at every step* — system + goal + schemas + history + tool observations, most of which is *generated at runtime*

Agents make the distinction necessary because the context is now a *stream you program*: every tool result you append is an act of context design. The model can only reason over what's in the window, formatted readably, under budget.

## 2. The agentic system constitution

Week 3's system prompt, extended for the loop:

```text
# Role
You are the capstone assistant. You answer using tools only.

# Tools
- search_knowledge(query, k): prose/documents. Use for "what/how/why" questions.
- sql_query(question): counts/sums/comparisons over tables. Use for "how many/top/average".
- save_note / read_notes: persist findings between steps.

# Rules
1. ONE tool call per step. Wait for its result before deciding anything.
2. Never guess values you can look up. Never invent columns, ids, or policy text.
3. If two tools could answer, prefer search_knowledge for meaning, sql_query for numbers.
4. An observation with "error" — fix the args or switch tools; NEVER retry the identical call.
5. An observation with no relevant hits means the info does not exist in my systems:
   answer "I don't have that information." Do NOT answer from general knowledge.
6. When the answer is complete, respond starting with "FINAL:".
7. Cite evidence: [doc:<id>] for documents, the SQL for numbers.

# Stopping
- Stop as soon as the goal is met. Do not add unrequested analysis.
- Hard limit: {max_steps} steps. If not converged by then, give your best
  supported partial answer and state what is missing.
```

Load-bearing parts (each traceable to a failure you've seen):

| Rule | Failure it prevents |
|---|---|
| 1 (one call/step) | parallel-call races, arg soup |
| 4 (no identical retries) | infinite retry loops (W10-04) |
| 5 (insufficiency escape) | hallucinated policies on no-match (W4-01) |
| 6/7 (FINAL + citations) | runaways, uncited claims |
| stopping block | unbounded trajectories |

## 3. Observation formatting: tool outputs are prompts

The model reads tool results as *text in its context* — you are the editor of that text:

```python
def format_observation(result: dict, limit_chars: int = 1500) -> str:
    if not result.get("ok"):
        return f"TOOL ERROR: {result['error']} — fix the arguments or choose another tool."
    hits = result.get("result", {}).get("hits", [])
    if not hits:
        return "NO MATCHES. The knowledge base has nothing relevant; do not guess."
    lines = [f"[{h['id']}] ({h['source']}) {h['text'][:300]}" for h in hits]
    return "MATCHES:\n" + "\n".join(lines)          # ids included = citable observations
```

Rules:

- **Delimit** — `<observation>…</observation>` or `TOOL ERROR:` markers; the model must never confuse data with instructions (W3-02, and tool results are third-party injection surface: W9-03's text-in-images, W6-03's cell values)
- **Truncate with intent** — keep the *head* of ranked lists, note omitted counts ("+ 7 more hits")
- **Structure over prose** — JSON/rows with ids beat paragraphs; the model cites what it can point at
- **Errors are prompts** — "unknown column; did you mean 'revenue'?" teaches the next step; "Error" teaches nothing

## 4. Context budgeting across a run

Agent runs *grow*: system (fixed) + schemas (fixed) + history (grows per step). Manage it like W1-07, with agent-specific cuts:

```python
def fit_context(messages, budget_tokens=12000, enc=None):
    enc = enc or tiktoken.get_encoding("o200k_base")
    total = lambda: sum(len(enc.encode(str(m))) for m in messages)

    while total() > budget_tokens and len(messages) > 3:
        # 1) shrink the oldest tool observation to a one-line summary
        for i, m in enumerate(messages):
            if m.get("role") == "tool" and len(str(m["content"])) > 400:
                messages[i] = {**m, "content": f"[earlier result summarized: {str(m['content'])[:120]}…]"}
                break
        else:
            messages.pop(1)                       # drop oldest non-system turn entirely
    return messages
```

Priorities when cutting (rarely stated, always load-bearing): keep the system constitution verbatim; keep the *latest* observation verbatim; summarize/keep *findings* (the scratchpad exists for this, W10-02); sacrifice old raw observations first.

Tool schemas are a fixed tax (~300–800 tokens for two tools) — per-task registries ("this agent only gets search_knowledge") beat one god-registry.

## 5. Failure phrasing (the softest skill, the biggest lever)

The words you put around failures and refusals change agent behavior measurably:

| Situation | Weak observation | Strong observation |
|---|---|---|
| tool error | `{"error": "Exception"}` | `TOOL ERROR: unknown column 'revnue' — available: revenue, price. Fix args or call another tool.` |
| empty retrieval | `[]` | `NO MATCHES for 'xq14 policy'. The corpus likely lacks this. Recommend FINAL with "not available".` |
| low confidence | score 0.2 | `MATCHES (weak, best score 0.21). Treat as inconclusive.` |
| denied action | `denied` | `DENIED by human reviewer. Do not retry; proceed without this action or ask the user.` |

Test phrasings like prompts — same 10-task suite, swap the phrasing layer, compare trajectories (W10-04's harness is the referee).

## Exercises

1. Rewrite your file 01 `SYSTEM` with the 7-rule constitution; run the 3 demos from file 01 — which rules demonstrably fired?
2. Implement `format_observation` + `fit_context`; run an 8-step trajectory and print the context report before/after fitting.
3. Phrasing A/B: take 3 failing trajectories; redesign only the observation strings; rerun. Report the delta in steps and success.
4. Context stress test: a tool that returns a 20k-char page — run the loop with and without `fit_context`; find where the model's behavior degrades (wrong tool picks? lost instructions?).
5. Write your capstone agent's constitution (all 7 sections + stopping rules) as `prompts/agent.system.md` — file 06's practice imports it.

## Pitfalls

- **Prompts that grow per step** — re-stating the goal/plan every turn; the context fills with *your* scaffolding, not data
- **Observations pasted raw** — 20k-char HTML in the window is a context bomb and an injection vector (W3-02) in one
- **No stopping conditions** — "be helpful" has no termination semantics; FINAL + max_steps are the contract
- **Instructions the budget silently evicts** — long constitutions get truncated by your own fitter; keep the constitution ≤ ~400 tokens or mark it untouchable
- **Phrasing cargo-culting** — copy Anthropic's strings without your harness; measure or don't ship

## Resources

- Anthropic, *Building effective agents* + *Prompt engineering* docs (the constitution patterns)
- OpenAI, *Function calling best practices* — observation/arg guidance
- W3-01/02 + W1-07 — the foundations this file composes
- LangChain hub agent prompts — production constitutions to critique (§3's study-of-prompts exercise, agentic edition)
