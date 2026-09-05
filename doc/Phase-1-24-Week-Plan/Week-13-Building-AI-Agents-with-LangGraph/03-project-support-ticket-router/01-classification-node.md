# Classification Node — Structured Outputs, Reasoning

**What you'll learn:** the classification node: a Pydantic-typed label +
urgency + reason, the reasoning field that makes it auditable, and the
confidence threshold that routes the uncertain to humans.

## 1. The node

```python
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Classification(BaseModel):
    category: str = Field(description="billing|technical|account|other")
    urgency: int = Field(ge=1, le=5, description="5 = customer blocked")
    reason: str = Field(description="one sentence: why this category")

class RouterState(TypedDict):
    ticket: str
    classification: dict
    resolution: str
    escalated: bool

classify_node = Agent(
    name="Ticket classifier",
    instructions="Classify the ticket. urgency 5 only if the customer "
                 "cannot work at all. Always give a reason.",
    output_schema=Classification,          # Agno-style typed output
)
```

The typed output is the W11 structured-output pattern, node-shaped:
`category` routes, `urgency` gates, `reason` audits. Three fields —
every one consumed downstream.

## 2. The reason field is the audit trail

| Field | Consumer | Rule |
|---|---|---|
| `category` | the edge function | must be one of the enum values |
| `urgency` | escalation edge (file 02) | 5 escalates before anything else |
| `reason` | reviewer + trajectory store | one sentence, specific |

The reason is what makes misclassifications debuggable: a ticket routed
to billing with reason "mentions invoice" is legible; one with reason
"seems right" is a guess. The eval set grades reasons, not just labels
(sampled hand-checks, the W10 judge discipline).

## 3. Confidence gating (the uncertain path)

```python
class Classification(BaseModel):
    category: str
    urgency: int
    reason: str
    confidence: float = Field(ge=0, le=1)

def route(state: RouterState) -> str:
    c = state["classification"]
    if c["urgency"] >= 5:
        return "escalate"            # file 02: dangerous path first
    if c["confidence"] < 0.7:
        return "human_review"        # the uncertain path
    return "resolve"
```

| Confidence | Route | Rationale |
|---|---|---|
| ≥ 0.7 + urgency < 5 | auto-resolve | the hot path |
| < 0.7 | human review | cheap safety |
| urgency = 5 | escalate | always, regardless of confidence |

The threshold is set from your calibration data (the W9 judge
protocol's method): find the confidence below which accuracy collapses,
gate there, and re-measure monthly.

## 4. The eval additions

| Case | Gold |
|---|---|
| obvious technical ticket | category=technical, conf ≥0.8 |
| ambiguous multi-category | conf <0.7 → human |
| urgency inflation ("URGENT!!" for a question) | urgency ≤2 |
| true blocker | urgency=5 → escalate |

Urgency inflation is the classic classification failure — the battery
case keeps the model honest about *blockage*, not *punctuation*.

## 5. The classification calibration table (the threshold's evidence)

| Confidence bucket | n | auto-accuracy | action |
|---|---|---|---|
| ≥0.9 | 40 | 0.95 | auto |
| 0.8–0.9 | 30 | 0.85 | auto |
| 0.7–0.8 | 20 | 0.70 | gate here |
| <0.7 | 10 | 0.40 | human |

The calibration table is the threshold's evidence: bucket the eval runs
by reported confidence, measure accuracy per bucket, and place the gate
where accuracy drops below your bar. Model confidence is not calibrated
by default — this table is what makes the number meaningful.

## Exercises

1. Build the classification node with the typed output; run 10 tickets;
   hand-check 5 reasons against the labels (the judge discipline).
2. Threshold drill: sweep the confidence gate 0.5→0.9; plot auto-rate vs
   accuracy; pick the knee and record it.
3. Inflation drill: run the urgency-inflation case; the model must rank
   a polite blocker above a punctuated question.
4. Calibration drill: build §5's table from 100 runs (or your eval set
   × repeats); re-place the gate; document the move.

## Pitfalls

- Reasons that restate the category — "technical because it is
  technical" is not a reason; the battery rejects them.
- Confidence from the model treated as calibrated — it is not; the
  threshold comes from measured accuracy, not the float.
- Urgency gates *after* resolution — escalation first (file 02); the
  edge order is the safety order.