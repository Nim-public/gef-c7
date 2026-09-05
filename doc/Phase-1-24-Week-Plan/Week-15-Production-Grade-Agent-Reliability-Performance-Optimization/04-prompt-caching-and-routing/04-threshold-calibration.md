# Threshold Calibration — Misroute Costs Both Ways

**What you'll learn:** calibrating the router's thresholds: the cost of
a strong→weak misroute (quality loss) vs a weak→strong misroute (cost
loss) — the threshold sits where the two curves cross.

## 1. The two misroute costs

| Misroute | Cost | Measured by |
|---|---|---|
| strong→weak (hard query to cheap model) | quality drop | eval-set delta |
| weak→strong (easy query to expensive model) | money | token price delta |

```python
def total_cost(p_weak: float, quality_loss_usd: float, price_delta: float) -> float:
    """p_weak = share routed to the weak model."""
    misroute_quality = (1 - p_weak) * 0.0   # strong handles its share fine
    quality_cost = (1 - p_weak) * quality_loss_usd   # hard queries on weak
    price_cost = p_weak * price_delta       # easy queries saved
    return quality_cost + price_cost
```

The asymmetry: a quality drop on a hard query usually costs more than
the tokens saved on an easy one — which is why the default-to-strong
rule exists. The calibration finds the *confidence band* where the weak
model demonstrably holds quality, and routes only that band to it.

## 2. The calibration procedure

```text
1. run the eval set on BOTH models (strong and weak)
2. per case: quality delta (strong − weak)
3. find the cases where delta ≈ 0  → the weak-safe band
4. characterize the band (length? class? keywords?)
5. set the router's threshold to the band's boundary
6. verify: routed-to-weak cases show no regression on re-run
```

| Step | Artifact |
|---|---|
| 1–2 | the per-case delta table |
| 3–4 | the band's description (features that predict weak-safety) |
| 5 | the threshold in the router config |
| 6 | the verification run |

The procedure is the W9-05 pattern-selection analysis applied to
*models*: the band is measured, the threshold is derived, and the
verification re-runs the eval.

## 3. The calibration table (the deliverable)

| Band | Cases | Δ quality | Route |
|---|---|---|---|
| short, factual, single-tool | 40 | 0.00 | weak |
| chart/numeric | 25 | +0.15 strong | strong |
| long-context synthesis | 15 | +0.40 strong | strong |
| chitchat | 20 | 0.00 | weak |

The table is the router's spec — bands, evidence, and the route. The
thresholds live in the router config with the same version discipline
as every policy artifact.

## 5. The calibration pin note (the threshold's record)

```markdown
# Routing thresholds (W15)
- weak-safe band: [characterization, e.g. short + single-tool + factual]
- threshold: [the band's boundary in the router config]
- evidence: delta table (N cases, both models), verification run
- revisit: on model change, or eval-set class drift
```

The pin note is the threshold's evidence record — the band, the
boundary, the table, and the verification. The same page format as
every calibrated artifact in the program (the W9 judge thresholds, the
W13 confidence gates).

## 6. The calibration drill record (the threshold's evidence)

```text
delta table: 100 cases, both models
weak-safe band: short, factual, single-tool (40 cases, Δ=0.00)
threshold: route weak iff len<80 tokens AND single-tool AND factual
verification: 20 weak-routed cases re-run — 0 regression
```

The drill record is the calibration's evidence — the delta table, the
band's characterization, the threshold, and the verification. The same
record format as every calibrated artifact since the W9 judge
thresholds.

## Exercises

1. Run the eval on both models; build the per-case delta table; find the
   weak-safe band.
2. Threshold drill: set the boundary; rerun the eval with routing on;
   verify weak-routed cases hold quality and strong-routed cases keep
   it.
3. Asymmetry drill: price the quality loss (what would a wrong number
   cost the demo?) vs the token saving; the default-to-strong rule's
   economics, made explicit.
4. Pin drill: write the note; the threshold change is a version bump.
5. Record drill: fill §6's record from your drills; the page joins the
   pin-note family.