# Process Choice — Sequential vs Hierarchical, Measured

**What you'll learn:** the two CrewAI process modes, what hierarchical
adds (a manager LLM routing tasks), the cost of that manager, and the
measured decision for your workflow.

## 1. The two processes

```python
# sequential: tasks run in list order, context flows forward
crew_seq = Crew(agents=[researcher, writer, editor],
                tasks=[research_task, write_task, edit_task],
                process=Process.sequential)

# hierarchical: a manager LLM assigns tasks to agents dynamically
crew_hier = Crew(agents=[researcher, writer, editor],
                 tasks=[research_task, write_task, edit_task],
                 process=Process.hierarchical,
                 manager_llm="pinned-model-id")
```

| Property | Sequential | Hierarchical |
|---|---|---|
| Order | the list | the manager's plan |
| Overhead | none | one manager turn + delegation |
| Determinism | high | plan-dependent |
| Fits | known pipelines | unknown task mixes |

The mapping to W11: sequential ≈ your chain; hierarchical ≈ the manager
with agents-as-tools — the same three topologies, framework-shaped.

## 2. The manager's cost and failure surface

| Factor | Sequential | Hierarchical |
|---|---|---|
| model calls | n tasks | n tasks + manager plan/review turns |
| tokens | task-only | + plan, + per-task delegation context |
| latency | sum of tasks | + planning |
| failure mode | wrong order (yours) | bad plans, loops, skipped tasks |
| auditability | the list *is* the plan | plan in traces |

```python
def process_cost(n_tasks: int, plan_overhead: float = 0.25) -> float:
    return n_tasks * (1 + (plan_overhead if HIERARCHICAL else 0))
```

The manager tax is 20–40% in practice — worth it only when the *order*
is genuinely unknown at write time. Your W10 boundary rule, one more
level up: chains for known pipelines, a manager for the unknown.

## 3. The measurement protocol

| Metric | Sequential | Hierarchical |
|---|---|---|
| task completion rate | per task order | per plan |
| tokens | fixed sum | variable |
| end-to-end latency | sum | + planning |
| plan quality | n/a | did it delegate every task? |

```python
def plan_quality(plan, tasks) -> float:
    return len(set(plan) & set(tasks)) / len(tasks)   # coverage, no phantom
```

The hierarchical suite must assert *plan coverage* (every task was
delegated, none invented) — the phantom-task check is the CrewAI
edition of the phantom-citation gate.

## 4. The decision procedure

1. **Is the task order fixed and known?** Yes → sequential (determinism
   is a feature).
2. **Do tasks depend on runtime results for their ordering?** Yes →
   hierarchical (or your W11 chain with conditional edges).
3. **Can you afford the manager's token tax?** Check §2's formula.
4. **Is auditability a grading criterion?** Sequential plans are
   self-documenting.

For the GEF C7 capstone: sequential crews inside a `Flow` cover
research→write→edit pipelines; hierarchical earns its cost only when
task composition is genuinely open.

## 5. Flows — the explicit middle ground

`Flow` is CrewAI's answer to "sequential is too rigid, hierarchical is
too loose": explicit steps with listeners and a typed state object —
your W11 chain code with a state class:

```python
class ArticleState(BaseModel):
    topic: str = ""
    research: str = ""
    final_article: str = ""

class ArticleFlow(Flow[ArticleState]):
    @start()
    def run_research_crew(self): ...
    @listen(run_research_crew)
    def run_writing_crew(self, research_output): ...
```

The decision ladder, completed: sequential (known order) → Flow (known
stages, runtime data between) → hierarchical (unknown order). Each rung
costs tokens; each rung buys flexibility — §2's formula prices them.

## Exercises

1. Run your 3-task pipeline in both processes; produce the cost/latency
   table; note where hierarchical's plan helped (if anywhere).
2. Plan-coverage drill: run hierarchical on an ambiguous pipeline; assert
   every task delegated exactly once; count phantom tasks.
3. Flow drill: port the pipeline to a Flow with the typed state; verify
   artifacts move via state (no transcript stuffing).
4. Decision drill: write the process-choice paragraph with your numbers;
   the memo cites §2's formula result and the chosen ladder rung.

## Pitfalls

- Hierarchical "because it sounds smarter" — the manager is a token tax
  with a plan-quality risk; earn it with an unknown-order requirement.
- Sequential pipelines that secretly need runtime branching — the list
  order lies; move to hierarchical or a Flow with conditions.
- Manager plans unasserted — a skipped task is a silent missing
  deliverable; coverage assertions or it did not happen.