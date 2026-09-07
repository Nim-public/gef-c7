# Numeric-Hallucination Defenses — Verification Hooks and Policies

**What you'll learn:** the defense stack for the most damaging failure
class in analytics agents: confident wrong numbers. Four layers, each
with a detection test and an owner.

## 1. The four defense layers

| Layer | Mechanism | Catches |
|---|---|---|
| 1. Route | SQL-first instructions for numerics | estimated-from-prose answers |
| 2. Compute | tool-executed SQL only | mental arithmetic |
| 3. Verify | independent `verify_number` query | single-query errors |
| 4. Display | SQL + rows in the answer | unverifiable claims |

Layer 1 is prompting, 2–3 are tools, 4 is contract — the same
architecture/trust-ladder shape as W11 file 02, specialized to numbers.

## 2. The verification policy, encoded

```python
VERIFICATION_POLICY = {
    "always_verify": ["totals", "percentages", "comparisons"],
    "spot_check_rate": 0.2,           # for simple lookups
    "independence": "different aggregation path",
    "on_mismatch": "recompute; if still mismatched, report both + flag",
}

def needs_verification(result: AnalysisResult) -> bool:
    text = result.answer.lower()
    if any(w in text for w in VERIFICATION_POLICY["always_verify"]):
        return True
    return hash(result.run_id) % 10 < VERIFICATION_POLICY["spot_check_rate"] * 10
```

The policy is a committed artifact (like the gate policy, W10 file 04):
which claims always verify, which spot-check, and what a mismatch does.
The `on_mismatch` behavior is the honest one: report *both* numbers with
the flag — never silently pick one.

## 3. The mismatch drill (what a defense failure looks like)

```text
Q: total revenue Q3?
agent: 1.2M (query A)
verify: 1.18M (query B)         ← mismatch
correct behavior: answer "≈1.18M (verified); first query returned 1.2M
due to [reason]" + both SQL texts + flag
wrong behavior: silently answers 1.2M, or 1.18M without the flag
```

The drill's rubric: the *flag* is the deliverable. A mismatched number
without a flag is worse than no verification — it launders the error
through a trusted pipeline.

## 4. The unit/consistency checks (beyond verification)

| Check | Catch | Implementation |
|---|---|---|
| unit consistency | K vs M vs raw | normalize in SQL; state units |
| date-range sanity | "Q3 2030" | calendar bound in queries |
| cross-source agreement | warehouse vs knowledge conflicts | dual-pipeline citation of both |
| distribution sanity | 100% growth from 1 row | row-count + variance checks |

```python
def sanity_checks(df, col: str) -> list[str]:
    issues = []
    if df[col].isna().mean() > 0.3:
        issues.append(f"{col}: >30% missing")
    if df[col].nunique() == 1:
        issues.append(f"{col}: constant value — suspicious")
    return issues
```

Sanity checks run inside `run_sql_query` — the tool annotates results
with mechanical warnings, the agent relays them, the harness audits the
relay.

## 5. The defense test matrix (all four layers, drilled)

| Layer | Drill | Failure it must produce |
|---|---|---|
| 1 Route | numeric query with search-only context | refusal, no estimated number |
| 2 Compute | prompt the agent to "calculate mentally" | it must call the SQL tool |
| 3 Verify | planted mismatch | flag in user view |
| 4 Sanity | constant-column injection | annotation relayed |

One test per layer, each *forcing* the failure the layer exists to
catch — the mutation-test discipline applied to the defense stack. A
defense that has never failed a drill is a decoration; the matrix is
how you know yours is live.

## Exercises

1. Encode `VERIFICATION_POLICY`; wire `needs_verification` into the
   agent's flow; run 10 numeric queries; verify verify-fires per policy.
2. Mismatch drill: plant a query bug; produce a mismatch; grade the
   agent's response against §3's rubric (flag present? both SQLs shown?).
3. Sanity drill: run `sanity_checks` over 10 query results; inject one
   constant-column case; the annotation must appear in the answer.
4. Matrix drill: run the §5 table — all four layers forced, all four
   failures produced, all four caught by their defense.

## Pitfalls

- Verification theater — running verify_number but ignoring its verdict;
  the mismatch drill exists because silent override is the natural
  failure.
- Policies that verify *everything* — latency budget dies; the spot-
  check rate is the honest compromise.
- Sanity warnings computed and dropped — the tool annotates, the agent
  relays, the harness audits; a dropped annotation is a swallowed
  warning.