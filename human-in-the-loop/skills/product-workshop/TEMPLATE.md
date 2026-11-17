# The board template

One row, read left to right. The order is the method: it is not rearranged. Every box below is a field in the decision log (`workshop_log.py`), so the board and the log always say the same thing. Labels are given in English and Spanish; use the person's language on the board.

## Rules of the board

- **Frames, not loose sticky notes.** Each frame has fixed boxes. A box that cannot be filled says `[TBD]` and goes to the assumptions strip with an owner and a suggested next step.
- **Assumptions are red.** Any number without a source is written as an assumption, in red, and listed in the strip.
- **A status stamp on every frame:** `Draft` (the AI wrote it), `Open` (being discussed), `Decided` (kept as drafted) or `Changed` (the person changed it).
- **No solution before frame 5.** Frames 1 to 4 describe the goal, the people and the problem. If a product idea shows up there, it moves to frame 5.
- **The original template is never edited.** Work on a copy.

## Rules of the log

- Frames 0 and E have no question: their draft carries only `fields`.
- A box the case needs and the template does not name is allowed. Give it an English `snake_case` name and keep it in the frame where it belongs (for example `left_out` in frame 7).
- A number is written on the board exactly as it is registered with `number` ("3.2%", "1,761"). `chosen_why_numbers` in frame 2 lists those same values.
- Durations ("in 90 days") and times of day are not figures and need no source.
- When a brief asks for a fixed count (a top three, five risks), follow the brief: `top` in frame 4 takes as many as it asks for.

## Design row: build or improve a product

| # | Frame · Marco | Boxes (field · English label · etiqueta en español) | The question for the person · La pregunta | Done when |
|---|---|---|---|---|
| 0 | Start here · Empezá acá | `decision` · What we are deciding · Qué se decide<br>`how_to_read` · How to read this board · Cómo se lee<br>A two-column table: what the AI drafted, what it asks you | None | The table lists every question frame |
| 1 | Goal · Objetivo | `business_goal` · Business goal · Objetivo de negocio<br>`user_problem` · The problem it solves for the user · Qué problema le resuelve al usuario<br>`metric` · How the business keeps score · Métrica del negocio<br>`why_now` · Why now · Por qué ahora<br>`brief_and_givens` · The brief and what is fixed · Consigna y lo que viene fijo | Is this the goal, or is there one above it? · ¿Es este el objetivo o hay uno más arriba? | Goal, user problem and metric are filled, with no solution inside |
| 2 | Customer · El cliente | `segments` · Two or three segments, each with `role`: pays, uses or lives with it · Dos o tres segmentos: ¿paga, usa o convive?<br>`chosen` · The one we pick · El elegido<br>`chosen_why` and `chosen_why_numbers` · Why, with a sized assumption or a source · Por qué, con un número de supuesto o una fuente | Why this one and not the other? · ¿Por qué este y no el otro? | The choice cites at least one registered number. A personal story is not a reason |
| 3 | Their moment · Su momento y para qué lo usa | `persona` · A person with a name · Una persona con nombre<br>`moment` · When, and what is happening · Cuándo y qué le pasa<br>`deeper_want` · What they want underneath · Lo que quiere de fondo<br>`use_cases` and `prioritized_use_case` · Use cases, one marked · Casos de uso, uno marcado | Is this scene real? · ¿La escena es real? | One use case is marked as the priority |
| 4 | Where it fails today · Dónde falla hoy | `failures`, each with `cause` and `alternative_today` · Weak point, cause, and how they solve it today · Punto débil, causa y cómo lo resuelve hoy (la alternativa)<br>`ranking_criterion` · The criterion, said before ranking · El criterio, dicho antes de ordenar<br>`top` · The top ones, two unless the brief asks for more · Las primeras, dos salvo que la consigna pida más | These, or is one missing? · ¿Estas o falta una? | Every failure names the alternative, and the criterion is written |
| 5 | Ideas · Ideas | `ideas`, each with `size` (small, habit, bold) and `attacks` (a failure from frame 4) · Una chica, una que cambia un hábito, una ambiciosa; cada una dice qué falla ataca<br>Optional 1 to 5 scoring table (skip it in a live case) | Which one would you add? · ¿Cuál agregarías? | Three ideas or more, one small and one bold, each tied to a failure |
| 6 | Choose, hypothesis and metrics · Elegir, hipótesis y métricas | `chosen_idea` and `why_vs_goal` · The pick, against the goal · La elegida, contra el objetivo<br>`hypothesis`: `statement`, `baseline`, `target`, `timeframe` · La frase, base, meta y plazo<br>`metrics`: `north_star`, `primary`, `secondary`, `guardrails` · Norte, primaria, secundarias, lo que no se puede romper<br>`cheap_test` and `weak_spot` · How I test it cheaply, and what is weak about it · Cómo lo pruebo barato y qué tiene de flojo | Is it the one that moves the goal most, and is this how we would know? · ¿Es la que más mueve el objetivo, y es así como lo sabríamos? | Baseline, target and timeframe are written, and the four metric levels are filled |
| 7 | Growth and vision · Crecer y visión | `growth` · How it brings more users · Cómo trae más usuarios<br>`phases` · Phase 1 and 2 · Fase 1 y 2<br>`company_strategy_fit` · How it fits the company's strategy · Cómo encaja en la estrategia de la empresa<br>`dilemma_principle` · The principle that settles trade-offs · El principio que decide los dilemas<br>`one_sentence_summary` · Customer, failure, idea, how we measure it, in one sentence · Resumen en una frase | What is left out? · ¿Qué queda afuera? | The summary is one sentence |
| A | Assumptions strip · Franja de supuestos | `assumptions` · Everything we do not know, in sight · Todo lo que no se sabe, a la vista<br>`most_worrying` · The one that worries most · El que más preocupa | Which one worries you most? · ¿Cuál te preocupa más? | Every `[TBD]` on the board is listed here |
| E | Evidence · Evidencia | `items`, each with `type` (screenshot, quote, number, source), `ref` and `source` · Capturas, citas y números, cada uno con su fuente | None | Every item has a source. No screenshot shows personal data |

## Diagnosis row: a metric moved and we need to know why

Use this row instead of the design row when the question is "sales dropped, why?". It keeps frames 0, A and E.

| # | Frame · Marco | Boxes | The question for the person | Done when |
|---|---|---|---|---|
| D1 | Isolate · Aislar | `metric` · The metric that moved · La métrica que se movió<br>`tree` · The metric tree, two branches or more · El árbol de la métrica<br>`branch_that_moved` · The branch that moved · La rama que se movió | Is this the branch, or is it upstream? · ¿Es esta la rama o viene de más arriba? | The tree has two branches or more and one is marked |
| D2 | Diagnose · Diagnosticar | `cuts`, each with `cut` and `finding` (region, product line, season, new against returning) · Cortes, cada uno con lo que mostró<br>`cause_hypothesis` · Our hypothesis of the cause · La hipótesis de la causa | Which cut would you add before believing this? · ¿Qué corte sumarías antes de creerlo? | Two cuts or more, each with a finding |
| D3 | Resolve · Resolver | `goal` · The goal we resolve against · El objetivo contra el que se resuelve<br>`options` · Two options or more · Dos opciones o más<br>`chosen` and `how_measured` · The pick and how we will know · La elegida y cómo se mide | Does this fix the cause or the symptom? · ¿Arregla la causa o el síntoma? | No option is named before this frame |

## Strategy or launch questions

They use the design row. The two levels the question needs live in frame 7: whether people want it and how it makes money go in `growth`, and how it fits the company's vision goes in `company_strategy_fit`. The rollout goes in `phases`.
