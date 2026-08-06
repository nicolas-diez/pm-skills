---
name: growth-diagnostic
description: End-to-end growth diagnosis from a raw dataset to a defensible strategy, with auditable deliverables (formula-based Excel, chart-first deck, defense brief). Use when you receive a business dataset to diagnose (interview business case, your own company, or a side project) and need to read business health from data, segment the customer lifecycle, find where to invest, prioritize initiatives by LTV/CAC, and present it with CFO-style storytelling. Triggers: "/growth-diagnostic", "analyze this dataset", "growth diagnosis", "business case with data".
---

# Growth Diagnostic

Turns a raw dataset into a complete growth diagnosis and a defensible strategy. One golden rule orders everything: **chronology first, averages never alone**.

Explain every analytical decision in one line (why median and not mean, why series and not snapshot) so every run is also a learning session for the user.

## Non-negotiable principles

1. **Chronology first.** Every metric runs month by month (and weekly if volume allows: >500 events/week) BEFORE reporting aggregates. Every figure is communicated with its trend and exit state. Anything already fixed during the period is an observation, never an initiative. (Period averages routinely report problems that the time series shows were already solved by the end, and premiums that a mid-period pricing change erased. Both are embarrassing to propose fixing.)
2. **Nothing invented.** Every number comes from the dataset or cites an explicit external source. What can't be measured is discarded as an initiative. Assumptions are always tagged `[VALIDATE]` and brought to the presentation as open questions (that adds seniority, it does not subtract it).
3. **Human in the loop at 5 gates.** The skill does NOT advance without the user at: (G1) field and unit interpretation; (G2) diagnosis verdicts before strategy design; (G3) initiative selection and no-gos; (G4) deck numbers validated against the Excel; (G5) final copy and headlines (offer options, never impose).
4. **Everything auditable.** The core deliverable is the Excel built from raw data with formulas: if a number in the deck can't be traced there, it doesn't go in the deck.
5. **Correlation is not causation.** Associative findings (e.g. "worse wait times correlate with churn") are declared as associations and lead to experiments, never rollouts.

## Phases

### Phase 0 — Intake (with the user)
Capture: case context (company/role/brief or real problem), required deliverables, deadline, constraints, and which frameworks apply (read `references/frameworks.md`). If it's an interview case: read the evaluation rubric and map each phase to what scores.

### Phase 1 — Data quality and schema inference
Before any conclusion: id uniqueness, duplicates, nulls, inverted timestamps, zero/impossible values, out-of-range coordinates, units (validate with orders of magnitude), timezone (ALWAYS convert to local before hourly analysis). Produce the edge-case table with the treatment of each. **G1: validate interpretation of every ambiguous field with the user.**

### Phase 2 — Chronology
Monthly series of ALL core metrics (see `references/metrics-catalog.md`) plus weekly for the last quarter to detect inflections. Classify each problem: ALREADY SOLVED (observation), IMPROVING BUT FRAGILE (guardrail), STRUCTURAL WITH NO TREND (initiative candidate), WORSENING (priority candidate). Watch for: censoring in the last period (cohorts without a full window), mix effects when aggregating (e.g. scheduled vs on-demand wait times), regime changes mid-period (pricing, product).

### Phase 3 — Exhaustive metric sweep
**Exhaustiveness rule: every metric in the catalog is computed or declared not-computable with this data. Never silently skipped.** Run the full catalog (AARRR stage by stage + marketplace + unit economics + supply side + growth accounting). For each metric the catalog lists the possible pains: mark which appear in THIS data and how severe.

The output is the **Classified Metric Inventory**: one table with ALL funnel metrics, each with value, trend, exit state, detected pain, and assigned role (NSM candidate / tree KPI / guardrail / diagnosis-only / not computable, with its instrumentation request). The North Star, the tree, and the guardrails EMERGE from that inventory: they are not picked by intuition, they are picked because the sweep showed where the pain and the value live (classification criteria in the catalog). The inventory ships as an Excel sheet. **G2.**

### Phase 4 — Benchmark and company history
Research: (a) competitors and their playbooks (with sources, ranges, and proxy type: never invented precision); (b) **the company's own history**: what it tried before and what it killed. Proposing "a membership program" when the company already buried one reads junior; proposing to evolve the live asset with that history cited reads senior. External data ALWAYS isolated and cited.

### Phase 5 — Strategy
With the CFO framework (`references/frameworks.md`): behavioral NSM + tree per stage with real baselines; 3-4 levers prioritized with an explicit quantified criterion (incremental LTV per dollar × pool size × independence from constraints × time to impact), each card with its budget weight; **the no-gos backed by data** (as important as the yeses); ONE deep experiment with a numeric hypothesis, mechanics, test/control, sample size by statistical power (two-proportion formula, documented), guardrails, and kill/scale criteria; incrementality-based budget with benchmarked caps (% of GMV) and a cut rule. **G3.**

### Phase 6 — Deliverables
In this order (full specs in `references/deliverables-spec.md`): pre-analysis doc (md, the living backup of the defense) → auditable Excel (**G4**) → chart-first deck (12-15 slides, action titles, 1-2 charts per slide validating its thesis, per-slide source footer) → defense brief (thesis, ordered points, likely question + short answer per slide). **G5: final copy is the user's.**

## Definition of done

- [ ] Every figure in the deck traces to an Excel sheet or a cited external source.
- [ ] Every metric reported with trend and exit state, not just the average.
- [ ] At least one data-backed discard per proposed initiative.
- [ ] Assumptions in one place; `[VALIDATE]` items listed as open questions.
- [ ] Experiment sized by statistical power, not gut feel.
- [ ] The 5 human gates actually happened.

## Unacceptable outputs (kill before shipping)

Descriptive report with no recommendation · full-period averages as diagnosis · an initiative proposing to fix what the series shows already fixed · numbers without sources · benchmarks with invented precision · a deck without charts validating its theses · causality claimed from correlation.
