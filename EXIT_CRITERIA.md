# EXIT CRITERIA — pm-skills engine

> Verifiable exit criteria per phase. The engine does not advance a phase until the previous one is met. Inspired by ship-gate / kill-gate practices in AI-native product evals.

## Per phase
| Phase | Skill | Exit criterion (verifiable) |
|---|---|---|
| 0 · Entry gate | orchestrator | Real evidence loaded + initiative classified as pre-commitment (wedge) or roadmap-committed (authority risk). |
| 1 · Decomposition | 01 | ≥1 falsifiable condition per category. |
| 1 · Data-quality audit | 02 | Every category mapped to a strength (strong/medium/weak) + most dangerous gap named. |
| 2 · Assumption extraction | 03 | Each assumption has a confidence rating anchored to citable evidence; deal-breakers flagged; none "supported" without a source. |
| 3 · Test plan | 04 | Every risky deal-breaker has a test + **pre-committed numeric threshold** + kill gate. |
| 4 · AB Roadmap + handoff | 05 | Roadmap by hypothesis (not a spec); prototype handoff self-contained. |

## Hard project gates
1. **Anti-hallucination:** no invented data. No source → `[VALIDATE]` or "unknown."
2. **Human-in-the-loop:** the final decision is NEVER made by the engine. Every test plan marked `[review]`.
3. **Decision-forcing:** every output closes with a threshold that triggers a decision. A purely informative output = failure (a mirror).
4. **Experiment-first:** if the final deliverable is a product spec instead of an AB Roadmap + prototype → the differentiator fails.
5. **Creator ⟂ Verifier:** the data-quality audit is run by a different sub-agent than the one that generated the assumptions.

## Project-level validation (shadow test)
Before trusting the engine at scale: run it on ~10 live initiatives (outcome unknown), deliver outputs to a senior PM panel, ask one question — "would you change something important after reading this?" If **fewer than 3 of 10** change a real decision, the engine produces better documents, not better decisions → rethink or kill.
