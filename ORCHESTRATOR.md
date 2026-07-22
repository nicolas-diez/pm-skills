# pm-skills · ORCHESTRATOR (`/pm-skills`)

> The command file that coordinates the engine: evidence → decision → AB Roadmap / prototype handoff. It does no work itself — it **sequences** the skills and enforces the gates. Pattern: orchestrator + modular skills + sub-agents.
>
> **Core principle (audit-first):** no build decision is proposed without passing the data-quality audit. Evidence is **audited, not assumed** — that's where document-centric PM tools fail.
> **Human-in-the-loop:** the engine proposes; the final decision is the PM's. Every AI output is reviewed.

## Expected input (initiative workspace)
```
<initiative>/
├── context/
│   └── company.md            → company/client context (multi-workspace)
├── data/
│   ├── interviews/           → raw transcripts (.txt/.md)
│   ├── surveys/              → responses
│   ├── meetings/            → meeting transcripts (stakeholders, tech, partners)
│   └── brief.md             → problem / idea / PRD / notes
├── analysis-inputs/          → PRE-analysis (interview synthesis, survey analysis) — do this FIRST
└── outputs/                  → EMPTY at start; the engine writes here
```
**GIGO rule:** convert everything to Markdown + pre-analyze before running. Better input → better output.

## Sequence (sub-agents, fresh context per step)
```
PHASE 0 · ENTRY GATE
  └─ Is there real evidence? Is the initiative pre-commitment (authority wedge)?
     If the roadmap is already "sold," flag authority risk (output likely a mirror, not a lever).

PHASE 1 · (PARALLEL — 2 sub-agents)
  ├─ skills/01-decision-decomposition   → "what must be true" (falsifiable conditions)
  └─ skills/02-data-quality-audit       → VERIFIER: how reliable is the evidence? gaps

PHASE 2 · (SEQUENTIAL — depends on P1)
  └─ skills/03-assumption-extraction    → assumptions vs evidence, confidence rating, deal-breakers

PHASE 3 · (SEQUENTIAL — decision-forcing)
  └─ skills/04-prioritized-test-plan    → test riskiest assumptions + KILL GATES with thresholds

PHASE 4 · (OUTPUT — experiment-first, not a spec)
  ├─ skills/05-ab-roadmap               → executable AB Roadmap (NOT a product spec)
  └─ handoff → templates/REPLIT_PROTOTYPE_PROMPT.md → prototype input

CLOSE
  └─ log to DECISION_LEDGER.md: decision, flagged assumptions, threshold, outcome→fill
```

## Orchestration rules
- **Parallel the independent, sequential the dependent.** P1 runs in parallel; P2–P4 in series.
- **Traceability:** each skill writes its file to `outputs/NN-*.md`. Auditable where it failed.
- **Creator ⟂ Verifier:** the producer (decomposition, assumptions) is never the verifier (data-quality audit). Separate sub-agents.
- **Math in Python**, not prose (sizing, price sensitivity, etc.).
- **Decision-forcing, not informative:** every test plan closes with a pre-committed kill gate + threshold. No threshold → it's a mirror.

## Why modular skills + sub-agents (not one mega-prompt)
1. **Quality:** complex insight workflows must be decomposed; a giant prompt fails.
2. **Modularity:** run the full workflow or any skill standalone; recombine like puzzle pieces.
3. **Traceability:** each step writes its output file → audit where it broke.
4. **Fresh context:** each sub-agent starts with a clean window (avoids degradation).

## Credits / lineage
Built on classic product discovery — Riskiest Assumption Testing (Cagan), Assumption Mapping (Bland & Osterwalder), "what must be true" (Roger Martin), Continuous Discovery (Torres), Amazon working-backwards — compressed with AI. Sub-agent workflow pattern inspired by AI-native PM practice (Maven cohort, incl. Caitlin Sullivan's data-to-decisions workflow).

## Exit criteria
See `EXIT_CRITERIA.md`. The engine does not "finish" a phase until its verifiable exit criterion is met.
