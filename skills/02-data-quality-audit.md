# Skill 02 · Data Quality Audit (VERIFIER) ⭐

> Phase 1 (parallel). **The differentiator.** Document-centric PM tools assume the evidence is good; this step **audits** it. Runs as a sub-agent separate from the creator (Skill 01/03).

## Input
Full `data/` (interviews, surveys, meetings) + `analysis-inputs/`.

## What it does — audits the STRENGTH of the evidence, not its existence
1. **Source & sample:** who does each data point come from? sample size? correct population (e.g. current users vs. churned)? Flags: single-data-point, proxy-complaints, self-report.
2. **Biases:** selection, recency, wishful thinking, evidence that confirms what was already wanted.
3. **Critical gaps:** what was NOT asked and should have been? (e.g. segment sizing, billing/finance dependencies, real willingness-to-pay).
4. **Ranking by reliability:** flag the **weakest** evidence category (often price/WTP and sizing).
5. **Math in Python:** sizing and sensitivity computed in code, not prose.

## Output → `outputs/02-data-quality-audit.md`
Table: evidence category · source · strength (strong/medium/weak) · gap. + "The weakest evidence is ___ → any decision depending on it is high-risk."

## Exit criterion
Every category from `01` mapped to a strength level. At least the most dangerous gap named explicitly. If global evidence is all "weak" → alert: the engine is only as good as the input (GIGO).

## Why it's the verifier
It's the only step that can say "don't trust this." Without it, the rest of the engine produces unjustified confidence. Never run by the same agent that generated the assumptions.
