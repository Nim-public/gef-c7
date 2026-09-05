# Eval Cases — 15 Data-Intensive Tasks with Gold Answers

**What you'll learn:** the 15-task eval set: design, gold answers from
your data, and the scoring rules — numeric exact-match, citation
presence, and honest-refusal checks.

## 1. The case table

| # | Task | Gold | Scoring |
|---|---|---|---|
| 1 | "What does the corpus say about X?" | unit + quote | citation + substring |
| 2 | "Explain the architecture in doc Y" | section ref | citation |
| 3 | "Which chart shows Z?" | unit_id | exact citation |
| 4 | "Quote the passage about W" | verbatim-ish | citation + fuzzy match |
| 5 | "What topics does the corpus cover?" | topic list | coverage ≥80% |
| 6 | "Total revenue in Q3?" | 1,240,000 | exact number |
| 7 | "Revenue by quarter, 2025" | 4 numbers | exact set |
| 8 | "Top 3 products by margin" | ordered list | set + order |
| 9 | "Margin trend, H1 vs H2" | up/down + values | direction + numbers |
| 10 | "Customers with >3 orders" | count | exact count |
| 11 | "Why did margin drop in Q3?" (numeric + corpus) | SQL + unit | both |
| 12 | "Compare our revenue to industry" | SQL + external caveat | labeled sources |
| 13 | "Forecast next year" | refuse (no data) | honest refusal |
| 14 | "What was the CEO's 2019 bonus?" | not found | honest refusal |
| 15 | "What is the margin?" (ambiguous) | clarify or flag | flagged |

Gold answers come from your data: run the SQL yourself, record the
number; read the corpus, record the unit. Gold labels are facts, not
opinions — the W10 rule.

## 2. The scoring rules

| Metric | Rule |
|---|---|
| numeric exact-match | parse the number; 1 digit off = wrong |
| citation presence | required by case; missing = fail |
| honest refusal | matches the refusal phrase family; no invented content |
| source labeling | case 12 must label internal vs external |

Numeric tasks (6–10) are the strictest scoring in the program — the
verification policy (W12 file 04-03) applies to exactly these.

## 3. Case design rules (the anti-gaming rules)

```text
[ ] gold answers computed from data, not from model outputs
[ ] at least one case per tool (knowledge, SQL, verify, web-if-enabled)
[ ] at least two impossible/ambiguous cases (refusals are graded)
[ ] ambiguous cases accept clarification as success
[ ] the set is versioned (eval-set vN) and committed
```

## 4. The gold-answer workbench (how the table gets filled)

| Case type | Gold procedure |
|---|---|
| numeric (6–10) | run the SQL yourself; record the exact value |
| corpus (1–5) | find the unit; record its id + the quote |
| mixed (11–12) | both, labeled internal/external |
| refusal (13–14) | verify absence (searches ran, nothing found) |
| ambiguous (15) | write the accepted behaviors |

```python
GOLD = {
    6: {"answer": 1_240_000, "tolerance": 0, "sql": "SELECT SUM(revenue) ..."},
    3: {"unit_id": "u042"},
    14: {"refusal": True},
}
```

The gold table is code — computable checks, not prose. Case 13 is the
interesting refusal: "forecast" is *unanswerable* because no future data
exists — the gold asserts the agent says so rather than extrapolating.

## 5. The eval-set version note (the set's changelog)

| Version | Cases | Added because |
|---|---|---|
| v1 | 15 | this file's design |
| v1.1 | +2 | post-mortem classes from W11/W12 |
| v2 | +3 | new tool surface (W13 graph nodes) |

The changelog is the eval set's version discipline — each addition names
the scar it encodes. A case without a "because" is a vanity case; the
set is curated like the battery (W11 file 02-05's provenance column).

## Exercises

1. Write the 15-case table with gold answers *from your data*; verify
   each gold by hand once (the SQL runs, the unit exists).
2. Scoring drill: implement the numeric exact-match parser (thousands
   separators, currency, decimals); test it against 10 formats.
3. Adversarial-case drill: add one case per failure class you have seen
   (W10/W11/W12 post-mortems) — the eval set grows from your scars.
4. Refusal drill: run case 13 three times; any extrapolated forecast is
   a grounding failure — record and fix the constitution wording.
5. Version drill: commit the set as v1; add one scar case as v1.1; the
   header must show both.
4. Refusal drill: run case 13 three times; any extrapolated forecast is
   a grounding failure — record and fix the constitution wording.