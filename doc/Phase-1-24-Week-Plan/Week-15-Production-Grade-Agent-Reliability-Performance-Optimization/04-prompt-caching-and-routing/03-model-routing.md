# Model Routing — Rules → Classifier → RouteLLM

**What you'll learn:** the routing ladder: regex rules for the obvious
cases, a small classifier for the rest, and RouteLLM-style learned
routers when the volume justifies it — each rung measured before
promotion.

## 1. The ladder

```python
# Rung 1: rules (deterministic, free, instant)
def route_rules(query: str) -> str | None:
    if re.search(r"SELECT|SUM\(|GROUP BY", query, re.I):
        return "strong"                    # code-ish → strong model
    if re.search(r"^(hi|hello|thanks)\b", query, re.I):
        return "weak"                      # chitchat → weak model
    return None                            # fall through to rung 2

# Rung 2: classifier (small model, structured output)
def route_classifier(query: str) -> str:
    result = classifier_llm.invoke(ROUTE_PROMPT.format(query=query))
    return result.recommended_model        # "strong" | "weak"

# Rung 3: RouteLLM (learned router, matrix factorization / BERT)
# from routellm.controller import Controller
# router = Controller(...)  ; router.route(query) → model
```

| Rung | Latency | Cost | Accuracy profile |
|---|---|---|---|
| rules | ~0 µs | free | rigid, high precision on known patterns |
| classifier | ~200 ms | ~200 tok | handles phrasing variance |
| RouteLLM | ~10–50 ms | model load | learned, needs training data |

The ladder is the W10 boundary discipline applied to *cost*: route the
easy cases to the cheap model, escalate the hard ones. Each rung
promotes to the next when measured accuracy demands it.

## 2. The integration (routing inside the agent)

```python
def pick_model(query: str) -> str:
    if (r := route_rules(query)):
        return r
    if ROUTER_CONFIDENT(query):
        return route_classifier(query)
    return "strong"                        # default: the safe choice

agent = Agent(model=pick_model(query), ...)
```

| Rule | Why |
|---|---|
| default to strong | misrouting a hard query costs quality; misrouting easy costs pennies |
| the classifier only sees rung-1 fall-throughs | the classifier's job is the borderline band |
| every decision logged | the calibration data (file 04) |

The default-to-strong rule is the asymmetry principle from W10 file 04:
misrouting costs are asymmetric, so the uncertain case goes to the
expensive-but-correct path.

## 3. The routing battery (the three-way table)

| Query | Rung | Expected model | Quality check |
|---|---|---|---|
| "SELECT totals..." | rules | strong | the code runs |
| "hello" | rules | weak | fine |
| "why did margin drop?" | classifier | strong | quality holds |
| "what's 2+2" | classifier | weak | quality holds |
| novel phrasing | default | strong | no regression |

The battery asserts model choice *and* answer quality — a weak-model
answer that drops quality is a misroute, whatever the rung. The eval
set gains a `model` column; the cost/quality table (file 04) reads it.

## 5. The routing pin note (the ladder's manifest)

```markdown
# Model routing (W15)
- rung 1: rules (patterns listed, versioned)
- rung 2: classifier (model, prompt pvN, accuracy measured)
- rung 3: RouteLLM — deferred until volume justifies
- default: strong (the asymmetry principle)
- battery: routing table (model choice + quality per case)
```

The manifest records the ladder's rungs and the promotion state — the
same format as the tool-surface policy. Rung 3's deferral is a
*decision with a trigger* (volume), not an omission.

## Exercises

1. Implement rung 1; run the battery; the rules' precision on known
   patterns verified.
2. Classifier drill: train/prompt rung 2 on 20 labeled queries; measure
   its accuracy on the borderline band.
3. Ladder drill: measure cost and quality per rung on the eval set; the
   promotion decision (when to move from rules to classifier) is data.
4. Pin drill: write the manifest; the promotion trigger named.