# Skill 01 · Decision Decomposition (CREATOR)

> Phase 1 (parallel). Turns a fuzzy decision into **falsifiable conditions**. Basis: "what must be true" (Roger Martin, *Playing to Win*) + Amazon working-backwards.

## Input
`data/brief.md` + `context/company.md`.

## What it does
1. **Bound the decision (bounded choice):** not "should we build X?" but "X vs. the real alternatives for solving the same problem" (software, pricing, onboarding, do-nothing).
2. **`## What must be true`** — a numbered list of conditions that MUST be true for this to be the right decision, in categories: *Customer demand · Market context · Technical feasibility · Business viability · User behavior · Strategic alignment*. Every condition must be **falsifiable** (testable), not an opinion.
3. **`## What "wrong" looks like`** — failure scenarios in BOTH directions: build-and-wrong (wasted resources, poor attach rate, brand confusion) and don't-build-and-wrong (opportunity cost).

## Output → `outputs/01-decision-decomposition.md`
Sections A (bounded choice), B (what must be true, numbered), C (what wrong looks like).

## Exit criterion
≥1 condition per category, all falsifiable. If a condition can't be tested, rewrite it or drop it.

## Does not do
Does not evaluate evidence (Skill 02). Does not propose tests (Skill 04). Only decomposes.
