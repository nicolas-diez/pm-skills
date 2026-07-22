# Skill 03 · Assumption Extraction (CREATOR)

> Phase 2 (sequential — depends on 01 + 02). The heart of the system. Extracts assumptions from the brief, cross-references them against evidence + quality flags, rates confidence, and marks deal-breakers. Basis: Riskiest Assumption Testing (Cagan) + Assumption Mapping (Bland/Osterwalder).

## Input
`data/brief.md` + `outputs/01-decision-decomposition.md` + `outputs/02-data-quality-audit.md`.

## What it does
Extracts each assumption and maps it. Per-block format (reusable as-is):
```
Assumption N: [statement]
  source:            [brief] section / [Decomposition] must-be-true #X
  evidence-for:      [what supports it]
  evidence-against:  [what contradicts it]
  quality-flag:      [from Skill 02: strength of that evidence]
  confidence-rating: supported / partially-supported / unknown / contradicted
  deal-breaker?:     yes/no (if false, does the decision die?)
```
Closes with a **dashboard of the highest-risk assumptions** (high impact x low evidence).

## Output → `outputs/03-assumption-extraction.md`
All assumptions + counts (supported/partial/unknown/contradicted) + top deal-breakers.

## Exit criterion
Every assumption has a confidence rating anchored to real, citable evidence (not invented). Deal-breakers identified. If an assumption comes out "supported" without citable evidence from Skill 02 → downgrade to "unknown". **Do not invent evidence** (hard anti-hallucination rule).

## Anti-mirror note
A deal-breaker that is "unknown" but the team will ignore anyway due to political pressure → flag the authority risk. The engine names it; it can't grant the PM authority, but the kill gate in Skill 04 gives cover.
