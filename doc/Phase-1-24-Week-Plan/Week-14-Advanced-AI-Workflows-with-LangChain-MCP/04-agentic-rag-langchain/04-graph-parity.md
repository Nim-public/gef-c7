# Graph Parity — W13-01 Equivalence Testing

**What you'll learn:** the equivalence test between the W13 graph and
the W14 chains: same eval set, same outcomes, same tool sequences — the
port's contract, LangChain edition.

## 1. The parity design

| Element | Spec |
|---|---|
| implementations | W13 `StateGraph` agent vs W14 `create_agent` |
| cases | the 15-case set (W13 file 05-02) |
| runs | 3 per case, majority |
| assertions | outcome parity, tool-set parity, token ±10% |

```python
def test_framework_parity():
    for case in EVAL_SET_V2:
        g = run_graph_agent(case)          # W13
        c = run_chain_agent(case)          # W14
        assert g.outcome == c.outcome
        assert tool_set(g) <= tool_set(c) | set(EXTRA_OK)
```

The tool-set assertion is directional (`≤`): the LangChain agent may use
extra tools where its runtime differs, but it may not *skip* the core
tools. Outcome parity is absolute.

## 2. The comparison table (the fifth framework column)

| Case | W13 graph | W14 chain | Δ | Cause |
|---|---|---|---|---|
| 1–5 corpus QA | 5/5 | 5/5 | 0 | same tools, same rules |
| 6–10 analytics | 5/5 | 5/5 | 0 | same toolkits |
| 11 mixed | 3/4 | 3/4 | 0 | parity |
| 13–14 refusals | 2/2 | 2/2 | 0 | parity |
| tokens p50 | 4.3k | 4.2k | −2% | loop prompt |

The expected shape: parity everywhere, small token deltas from prompt
packing. Deltas >5% get the forensics treatment (W11 file 06-02's
drill): bisect to the differing turn.

## 3. What differs structurally (and why parity still holds)

| Concern | W13 graph | W14 chain/agent | Parity mechanism |
|---|---|---|---|
| routing | conditional edges | model tool choice | same priority instructions |
| state | reducers | messages + middleware | same budget rules |
| verification | verify node | verify in the chain | same policy |
| persistence | checkpointer | checkpointer (same) | identical |

The parity holds because the *policies* are shared artifacts
(instructions, validators, batteries) — the W12-W14 theme, one more
proof.

## 4. The comparison's verdict (the last framework word)

```markdown
## Framework parity (W14)
- W13 graph and W14 agent: outcome parity on 15/15 (3 runs each).
- Token delta −2% (LangChain's loop prompt).
- Both wrap the same toolkits, knowledge, and rules.
- Decision stands (W13): LangGraph graph for interactive flows,
  LCEL/agent for linear chains, shared everything else.
```

## Exercises

1. Run the 15-case parity test; document any outcome divergence with
   its bisected cause.
2. Tool-set drill: verify the directional assertion (chain ⊇ graph's
   core tools); an extra tool usage gets a named exception.
3. Token-drill: attribute the −2% (prompt packing? fewer routing
   turns?) — the delta ledger, one more row.
4. Memo drill: update the framework decision (W13 file 05-04) with the
   parity result; the standing architecture is confirmed or revised.