# Four Features — Chat, Summary, Analyze, Visualize

**What you'll learn:** the four user-facing features as one agent with
routed modes: free chat, data summary, guided analysis, visualization —
one tool surface, four system-prompt variants, one eval set.

## 1. The feature table

| Feature | Prompt variant | Tools used | Output |
|---|---|---|---|
| chat | conversational, still grounded | none (or profiler) | free answer |
| summary | "describe this dataset" | profiler | structured summary |
| analyze | full analytics loop | profiler + pandas | `AnalysisResult` |
| visualize | chart-first | pandas + render | chart path + caption |

```python
FEATURE_PROMPTS = {
    "chat": CHAT_PROMPT,            # pv1: helpful, cites nothing
    "summary": SUMMARY_PROMPT,      # pv1: profile → describe
    "analyze": ANALYZE_PROMPT,      # pv1: numeric grounding rules
    "visualize": VIZ_PROMPT,        # pv1: chart-first
}

agent = create_agent(model=..., tools=[profile_csv, run_pandas, render_chart],
                     response_format=AnalysisResult)
# mode enters as the system prompt variant + the state's mode field
```

One tool surface, four prompt variants — the W9 pattern-selection table
(user-facing edition): the *mode* is the route, chosen by the UI, not
by the model.

## 2. Chat mode's grounding subtlety

| Query | Chat mode behavior | Why |
|---|---|---|
| "what's in this file?" | profiler, then describe | data question in chat clothing |
| "hello, how are you?" | free answer, no tools | chitchat skip |
| "is this data good?" | profiler + caveats | quality question |

Chat is *not* ungrounded — it is grounded-with-optional-tools. The
W12 skip-detection instrumentation applies: data-flavored questions must
fire the profiler even in chat mode (the floor rule, one more surface).

## 3. Analyze mode's contract

```python
class AnalysisResult(BaseModel):
    answer: str
    numbers_supported: list[str]   # the checks that back each number
    charts: list[str] = []
    caveats: list[str] = []
```

Analyze mode inherits the full W12 defense stack (route, compute,
verify, display) — the `numbers_supported` field names the checks (file
04). The four features share the typed output; the *prompt variant*
changes what fills it.

## 4. The feature eval set

| Feature | Case | Assert |
|---|---|---|
| chat | "what is this file about?" | profiler fired, free answer |
| summary | "summarize the data" | rows/cols/nulls all present |
| analyze | "average margin by quarter" | numbers_supported present |
| visualize | "show margin by quarter" | chart path in answer |

The eval set (W13 file 05-02's pattern) gains the feature column — 12
cases, 3 per feature, one battery per assertion.

## Exercises

1. Build the four prompt variants; wire the mode switch; run the feature
   eval set.
2. Chat-grounding drill: ask a data question in chat mode; the profiler
   must fire (the floor rule); record it.
3. Feature-parity drill: the analyze feature's outputs must pass the W12
   numeric gate verbatim — same validation, new skin.

## 5. The feature-mode pin note

**Task:** extend `reports/sdk-versions.md` with the feature matrix: the
four prompt variants (pvN each), the mode-switch mechanism, and the
feature-battery command.

**Worked approach:** the four features share one tool surface — the pin
note records which prompt variant each mode loads, so a variant edit
and the battery re-run stay paired.

**Pass criterion:** note committed; the feature battery green at the
recorded variant versions.

## Pitfalls

- Chat mode as ungrounded mode — data questions arrive in chat; the
  floor rule keeps the profiler honest.
- Four agents instead of four prompts — one tool surface, prompt
  variants; four agents quadruple the surface to secure.
- Visualize mode that answers in text — the chart tool is the feature;
  the eval asserts the artifact.