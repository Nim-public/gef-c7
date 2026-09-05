# Exercises — CSV Analyzer

Expanded set with worked approaches. The deliverable: the three-tool
surface with guards, a probe-tested sandbox, four working features, and
numeric grounding audited end to end.

## 1. Tool surface (from 01-tool-surface)

**Task:** build the three tools with guards; enforce profiler-before-
pandas via the constitution; verify the trace order on 5 queries.

**Worked approach:** the trace-order check is the profiler rule's
evidence — instructions request the order, the trace proves it. The
guard battery (six patterns) runs as the tool's contract test.

**Pass criterion:** profiler-before-pandas on 5/5; guard refusals carry
hints; charts repo-relative and cited.

## 2. Sandbox probes (from 02-sandbox-discipline)

**Task:** build the restricted environment; run the five probes; add one
probe of your own (an escape you would try); all contained.

**Worked approach:** the sixth probe is the drill's teeth — your own
attack idea tests whether the wall generalizes beyond the list. The
timeout and size caps complete the containment.

**Pass criterion:** 6/6 probes contained; timeout fires at 10 s; the
50-row cap with the true count reported.

## 3. The four features (from 03-four-features)

**Task:** implement the four prompt variants; run the feature eval set
(12 cases); verify chat-mode grounding (the floor rule) and analyze
mode's numeric gate.

**Worked approach:** the feature column extends the eval set — one
battery per feature assertion. The chat-grounding drill is the skip-
detection rule applied to a new surface.

**Pass criterion:** 12/12 feature cases; chat-mode profiler floor holds;
analyze passes the W12 numeric gate.

## 4. Numeric grounding audit (from 04-numeric-grounding)

**Task:** implement the pairing audit; run 5 numeric queries; every
number paired to a check; delete one check on purpose and confirm the
audit flags it.

**Worked approach:** the deletion drill proves the audit works — the
pairing property, tested by its violation, wired into the harness gate
as a permanent check.

**Pass criterion:** 5/5 numeric answers fully paired; the deletion
drill's flag fires in the harness gate.

## 5. Self-review rubric

| Criterion | Evidence | Points |
|---|---|---|
| Profiler ordering enforced | trace checks | 3 |
| Guards: 6/6 patterns refused | guard tests | 3 |
| Sandbox: 6/6 probes + caps | drill results | 4 |
| Four features, eval green | feature battery | 3 |
| Numeric pairing audited | audit tests | 3 |

**Pass bar:** 14/17 to proceed to file 03 (the code review agent). The
sandbox (4-pointer) is the CSV project's non-negotiable — user data plus
model code is the program's sharpest edge.

## 6. The CSV pin note (the project's version manifest)

**Task:** extend `reports/sdk-versions.md` with the CSV project's full
stack: tool schemas date, sandbox level, feature prompt variants, and
the grounding-audit command — the four exercises' pins, one page.

**Worked approach:** the CSV project touches the sharpest edges; the
manifest records every layer's verification date so the demo's claims
are auditable.

**Pass criterion:** the manifest lists all four layers with green drill
commands as recorded.

## Pitfalls recap

- `pd.read_csv` inside generated code — the `df` binding is the only
  data source; the pattern list enforces it.
- Chat mode treated as ungrounded — data questions arrive in chat; the
  floor rule keeps the profiler in the loop.
- Numbers without their checks — the pairing audit makes provenance
  structural, not aspirational.