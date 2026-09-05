# Self-Improving Loops — Logs to Eval Sets

**What you'll learn:** the eval set that grows from your own failures:
failure logs → case mining → gold labeling → the eval set's changelog —
the post-mortem discipline (W11 file 06-03), systematized.

## 1. The loop

```text
runs → trajectory store → failure log (classified, file 03-02 of W13)
     → mine: new failure classes → eval cases (gold-labeled)
     → eval set vN+1 → regression gate updated
```

| Step | Artifact |
|---|---|
| classify failures | the W13 taxonomy |
| mine new classes | a class with ≥3 instances |
| gold-label | facts from your data |
| add to set | version bump + changelog row |

The loop is the W10 post-mortem's output, formalized: every added case
cites the failures that motivated it — the eval set grows from scars,
never from imagination.

## 2. The mining query

```python
def mine_new_classes(store, min_instances: int = 3) -> pd.DataFrame:
    df = store.recent(days=30)
    failures = df[df.outcome.isin(["failed", "degraded"])]
    grouped = (failures.groupby(["failure_class", "modal_tools"])
               .size().reset_index(name="n"))
    return grouped[grouped.n >= min_instances]
```

| Field | Why it matters |
|---|---|
| `failure_class` | the W13 taxonomy label |
| `modal_tools` | which tools the failures used |
| `n` | the evidence count |

Three instances make a class real; one is an anecdote. The mined table
is the eval set's roadmap — the class with the highest n is the next
case family.

## 3. Case construction from a failure cluster

```python
def case_from_failure(failure_row, gold) -> dict:
    return {
        "query": failure_row.query,
        "expected_tools": failure_row.modal_tools,
        "gold": gold,                          # from your data
        "source": f"mined:{failure_row.run_id}",
        "since": failure_row.date,
    }
```

| Field | Rule |
|---|---|
| `query` | the *original* failing query (or a paraphrase family) |
| `gold` | facts from your data (anti-retro-labeling) |
| `source` | the run that motivated the case |
| `since` | the version the case entered |

The `source` field is the provenance that keeps the eval set honest —
every case traces to a real failure or a designed scenario, never to
"seems useful".

## 4. The improvement metric (is the loop working?)

| Metric | Definition | Healthy |
|---|---|---|
| new-class rate | classes mined / month | declining |
| regression rate | old cases failing | <5% |
| set growth | cases added | slowing |
| fix latency | class mined → case green | <2 weeks |

A healthy self-improving loop shows *declining* new-class discovery —
the same failures stop recurring, the taxonomy saturates. A rising rate
means the fixes aren't landing (or the tool surface is changing faster
than the eval).

## Exercises

1. Run the mining over your full trajectory store; produce the class
   table (n ≥3); pick the top class.
2. Case drill: construct 3 cases from the top cluster; gold-label from
   your data; add as eval-set v+1 with the changelog.
3. Saturation drill: plot new-class rate by month; the curve tells you
   whether the system is converging or churning.

## Pitfalls

- Mining failures without the taxonomy — unclassified failures group
  badly; the W13 labels are the loop's input.
- Cases added without regression-gate wiring — a mined case that never
  runs again is decoration.
- Gold labels from the *fixed* model's outputs — facts from data; the
  anti-retro-labeling rule survives every automation.