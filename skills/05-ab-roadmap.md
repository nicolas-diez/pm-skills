# Skill 05 · AB Roadmap + Prototype Handoff (OUTPUT — experiment-first)

> Phase 4. The deliverable that spec-pipeline tools never produce. **It is NOT a product spec.** It's an executable, experiment-centric roadmap + the prototype handoff. If the final output is a spec, the differentiator fails.

## Input
`outputs/01`..`04` + `context/company.md`.

## What it produces (two artifacts)
### A) AB Roadmap (executable, not a 6-month doc)
Organized by **hypothesis to test**, not features to build. Each row:
```
Hypothesis · Experiment (A/B or cheap test) · Metric + threshold (from Skill 04) · Decision it triggers · Status
```
Replaces the PRD: instead of "full spec before building," it defines what gets tested, in what order, and what decision each result triggers. Fast, iterable.

### B) Prototype Handoff
Takes the proposed solution (validated against the evidence) and produces the prompt/PRD for an AI app builder (Replit, v0, Lovable, etc.) to stand up a responsive web prototype in minutes. Use `../templates/REPLIT_PROTOTYPE_PROMPT.md` as the format.

## Output → `outputs/05-ab-roadmap.md` + `outputs/05-prototype-handoff.md`

## Exit criterion
- Roadmap organized by hypothesis+experiment, not features. If it looks like a PRD → rewrite.
- Each hypothesis has metric + threshold inherited from Skill 04 (traceability).
- The prototype handoff is self-contained (someone pastes it and gets a prototype with no extra context).

## Rule
The prototype fires **only after** evidence + assumptions justify the solution. Prototyping first = generating garbage faster (the failure mode of prompt-to-app tools). The audit-first order is the point.

## Credits
Experiment-first roadmap over PRDs draws on AI-native PM collaboration practices (Maven cohort).
