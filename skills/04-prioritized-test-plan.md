# Skill 04 · Prioritized Test Plan (DECISION-FORCING)

> Phase 3 (sequential). Turns risky assumptions into a **cheap validation plan with kill gates**. This is what makes the engine a lever and not a mirror: without a pre-committed threshold, it's just a nice doc.

## Input
`outputs/03-assumption-extraction.md`.

## What it does
1. Takes the **unknown/contradicted deal-breakers** (riskiest, least evidence).
2. For each: cheapest test method, a **numeric** success criterion, and a **decision gate**.
3. Orders into phases with a **hard kill gate after Phase 1** (kill early, cheap).
4. Defines the **pre-committed threshold**: the number that, if not met, kills the project. E.g. "if current-user purchase intent < 15% → kill."

## Output → `outputs/04-test-plan.md`
Table: assumption · method · success criterion (number) · gate/kill. + phased timeline + the main kill gate bolded at the top.

## Exit criterion
Every risky deal-breaker has a test with a **pre-committed numeric threshold**. If a test closes without a number → rewrite. Human-in-the-loop is mandatory: **AI-generated test plans always need human correction**. Mark `[review]` where the PM must adjust.

## Decision-forcing rule (anti-mirror)
The output does not say "consider testing X." It says: "**test X; if the number < Y, do not build.**" The threshold is agreed BEFORE seeing the result. That gives the PM political cover (the authority wedge).
