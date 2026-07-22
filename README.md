# pm-skills

**An evidence-first product decision engine.** It turns raw evidence — user interviews, surveys, meeting transcripts, briefs — into decision-forcing outputs: an evidence audit, an assumptions map, a test plan with kill gates, and an experiment-first AB Roadmap that hands off to a prototype. It is **not** a prototype generator and **not** a spec-writing tool.

> Thesis: **audit the evidence first, change the decision, then prototype fast.**

## Why this exists

The AI-native PM stack has two crowded categories that don't touch each other:

- **Prompt-to-app builders** (v0, Lovable, Bolt, Replit) — great at generating software, but they start from a prompt. No evidence layer: they never ask whether the problem is real or whether the assumption was tested. Treating a model's fluent output as evidence is the classic 2026 PM failure mode.
- **Spec-pipeline PM tools** — stage-gated document pipelines where AI fills in PRD/spec fields. Faster docs, but the "data & insights" section is a form a human fills in, and nobody audits whether that evidence is any good.

**pm-skills owns the layer above both:** making sure the input is real, audited evidence before you spend a prototype — and then producing an experiment-first roadmap instead of a 6-month spec.

## How it works

An orchestrator sequences modular skills, each running as a sub-agent with fresh context:

```
PHASE 1 (parallel)   01 decision-decomposition   +   02 data-quality-audit (verifier)
PHASE 2 (sequential) 03 assumption-extraction  (confidence ratings, deal-breakers)
PHASE 3 (sequential) 04 prioritized-test-plan  (kill gates + pre-committed thresholds)
PHASE 4 (output)     05 ab-roadmap  →  prototype handoff (Replit / v0 / Lovable)
CLOSE                log to the decision ledger (decision + real outcome)
```

Two ideas do the heavy lifting:

1. **Audit-first.** The data-quality audit (Skill 02) is a *verifier* that runs separately from the creator skills. It's the only step allowed to say "don't trust this evidence." Most tools skip it.
2. **Decision-forcing.** Every output closes with a pre-committed threshold that triggers a decision ("test X; if < Y, don't build"). An output that only informs is a mirror, not a lever.

## Repo contents

```
ORCHESTRATOR.md          the /pm-skills command that sequences the engine
skills/
  01-decision-decomposition.md
  02-data-quality-audit.md      ⭐ the verifier / differentiator
  03-assumption-extraction.md
  04-prioritized-test-plan.md
  05-ab-roadmap.md
EXIT_CRITERIA.md         verifiable gates per phase + shadow-test validation
DECISION_LEDGER.md       template for logging decisions + outcomes
templates/
  REPLIT_PROTOTYPE_PROMPT.md    generic paste-ready prompt to prototype an app
```

## Credits / lineage

Built on classic product discovery — Riskiest Assumption Testing (Cagan), Assumption Mapping (Bland & Osterwalder), "what must be true" (Roger Martin), Continuous Discovery (Torres), Amazon working-backwards — compressed with AI. The orchestrator + modular-skills + sub-agent pattern draws on AI-native PM practice (Maven cohort, incl. Caitlin Sullivan's data-to-decisions workflow; Gridley & Ahuja's experiment-first roadmaps).

## Status

Framework + methodology, in the open. The engine is designed to be portable across companies and consulting engagements. Contributions and forks welcome.

## License

MIT — see [LICENSE](./LICENSE).
