# Team vs Single — The Measured A/B

**What you'll learn:** the honest experiment: the same tasks through a
single bounded agent (W10 architecture) and through the supervisor team
— measured on success, tokens, latency, and *repair* — with the verdict
written per task class.

## 1. The protocol

| Element | Spec |
|---|---|
| tasks | 10 codegen + 5 analysis tasks |
| single | W10 agent, max_steps 6 |
| team | supervisor + 2 workers, turn cap 6 |
| runs | 3 per task, majority |
| metrics | success, tokens p50, latency p50, repairs |

Same protocol as every comparison since W9: one variable (architecture),
shared everything else, 3 runs, majority.

## 2. The expected table (and what deltas mean)

| Task class | Single success | Team success | Tokens Δ | Reading |
|---|---|---|---|---|
| single-step codegen | 0.80 | 0.80 | +25% (supervisor overhead) | single wins |
| multi-stage analysis | 0.55 | 0.80 | +15% | team wins |
| repair-heavy tasks | 0.60 | 0.75 | +30% | team wins (specialized debug) |
| chitchat | 1.00 | 1.00 | +40% | single, obviously |

The team wins where *specialization* matters (different tools, different
instructions per stage) and loses where one context suffices. The
supervisor overhead is real — ~1 extra call per turn — and it is the
price of dynamic routing.

## 3. The verdict structure (per class, not global)

```markdown
## Team vs single verdict (W13)
- single-step tasks: single agent (team overhead unjustified)
- multi-stage analysis: team (specialization pays: +25 pts)
- repair-heavy: team with the self-repair cycle (file 01)
- global rule: task = single if one context suffices; team if two or
  more *different* tool/instruction sets are needed.
```

The W10 boundary statement, now with numbers at the task-class level —
and the same "revisit trigger" discipline (a class that drifts toward
multi-stage re-enters the A/B).

## 4. The repair-loop connection

The self-repair graph (file 01) *is* a two-agent team (coder + tester)
with a repair cycle. The A/B's repair-heavy row is where it earns its
keep: the specialized test/repair nodes beat one agent grading its own
homework. The measured number is the argument; write it down.

## Exercises

1. Run the protocol; produce the class-level table with ranges (3 runs);
   write the per-class verdict.
2. Overhead drill: isolate the supervisor's token cost (team total −
   worker-attributable); report the pure routing overhead.
3. Crossover drill: find the task complexity where team starts winning
   (the crossover point); state it as a rule ("≥3 distinct stages →
   team").

## Pitfalls

- A global winner declared from a class-split table — the split *is*
  the verdict; aggregates hide the crossover.
- Team tasks that are single tasks with extra workers — the A/B must
  use tasks that genuinely need specialization, or it measures noise.
- Repair cycles counted as failures — attempt 2 success is a *repair
  win*; score outcomes, not attempts.