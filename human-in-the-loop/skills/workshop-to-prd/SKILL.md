---
name: workshop-to-prd
description: "Turns a discussed workshop board into a short, test-first PRD. It starts from the decision log, puts the cheapest test and its threshold before any requirement, and makes every requirement say which failure from the board it answers. The person decides the scope of the first version, what is left out and the edge cases. Use when the user says «pasemos el tablero a un PRD», «armá el PRD del taller» or «write the PRD from the board»."
when_not_to_use: "Do not use without a discussed board or decision log (run miro-product-workshop first), to write a full product spec before anything has been tested, or to create tickets in an engineering tool."
---

# Workshop to PRD

> A short PRD that starts from the test. Every requirement answers a failure you already discussed.

A spec written before anything was tested is a guess with a table of contents. This skill writes the other kind: the document engineering needs for the piece that a test justifies building. It opens with the hypothesis, the cheapest test, the threshold and what gets decided if the threshold is missed. The requirements come after, and each one points back to a failure on the board.

## What is in this folder

| File | What it is |
|---|---|
| `prd_check.py` | Checks the PRD, gates "ready for engineering" and renders the Markdown view |
| `examples/bike-repair-prd.json` | The PRD of an invented case, built from the workshop example |
| `LOCAL.md` | Optional. This workspace's conventions and lessons. If it exists, read it first |

## How it runs

1. **Read what is already written.** The decision log first, then anything else the person points to: a strategy note, earlier documents, the repository. Do not ask for what you can find.
2. **Draft what the workshop already decided,** as a JSON file (see the example). Do not ask about these again:
    - the problem and for whom, from frames 1 to 4;
    - the test that comes first, from frame 6: the hypothesis with its baseline and target, and the cheapest test. The board gives a target, not a threshold: propose the target as the threshold, write `[TBD]` next to it and ask;
    - what we build, the metrics and the phases, from frames 6 and 7;
    - the alternatives we discarded: every idea from frame 5 that was not chosen, each with the reason the board gives. If the board gives none, write `[TBD]` and ask; do not make one up.
3. **Ask what only the person can decide,** one question per turn, the one that weighs most first, each with two or three options and your recommendation first:
    - what the first version includes;
    - what is left out, and why;
    - the edge cases, and what happens when something fails;
    - what gets decided if the test misses its threshold.

    Record their words in `person_answers` (`scope_v1`, `out_of_scope`, `edge_cases`, each a string with what they said). Then write the structured lists from those words: `out_of_scope` as items with `text` and `reason`, `edge_cases` as items with `case` and `behavior`. Do not fill any of this in for them, not even as a draft to correct. Until they answer, `decision_if_missed` says `[TBD]` and has its open question.
4. **Write the requirements.** Each one has an id, a priority (P0, P1, P2), how we will know it is met (`acceptance`: one sentence someone can check, not a restatement of the requirement) and what it answers: `failure:<name from frame 4>` or `goal`. A requirement that answers nothing does not belong in this PRD. An idea the workshop discarded comes back only if the person reopens it, in their words.
5. **What you do not know is an open question.** Mark it `[TBD]` and add it to the open questions. Suggest an owner (product, engineering, design, legal, data); the person confirms the owner and gives the date, in plain words ("before the pilot starts"). Until they do, leave both empty: the gate will say the PRD is not ready. Never fill a gap with a plausible default.
6. **Run `prd_check.py check`** and fix what it finds.
7. **Run `prd_check.py gate`.** The PRD is ready for engineering when the three sections that belong to the person carry their answers and every open question has an owner and a date. The first line of the document says so, with the count of open questions.
8. **Render it** with `prd_check.py render` and hand the Markdown to the person. Sending it to anyone is their call.

## The file

The PRD is one JSON file. `prd_check.py` reads these fields:

| Field | What goes in it |
|---|---|
| `title`, `log` | The title, and the path to the workshop's decision log |
| `problem`, `for_whom`, `what_we_build` | One short paragraph each |
| `test_first` | `hypothesis`, `test`, `threshold`, `decision_if_missed` |
| `goals`, `non_goals` | A list of sentences; non-goals are items with `text` and `reason` |
| `discarded` | Items with `idea` and `reason` |
| `requirements` | Items with `id`, `priority`, `text`, `acceptance`, `answers`, and `reopened_by` when a discarded idea comes back |
| `edge_cases`, `out_of_scope` | Items with `case` and `behavior`; items with `text` and `reason` |
| `metrics`, `phases` | Copied from the board |
| `open_questions` | Items with `question`, `owner`, `due`, `status` (`open` or `closed`) |
| `person_answers` | `scope_v1`, `out_of_scope`, `edge_cases`: the person's own words |
| `sources` | Items with `value` and `source`, for any number that is not on the board |

## Coming back to a PRD that exists

Say which of the three you are doing, and do only that:

- **Continue:** write the sections that are still empty.
- **Review:** check it against the board and the rules, without adding scope.
- **Find evidence:** look for what supports or contradicts a requirement, and say what you found.

## What it does alone, what it asks, what it never does

- **Alone:** read the log and what is already written, draft the sections that come from the board, run the checks, render the view.
- **Asks:** the scope of the first version, what is left out, the edge cases, the decision if the test misses, the owner of each open question.
- **Never:**
    - decide the scope for the person;
    - write a requirement that answers no failure and no goal;
    - bring in a number that is not on the board or in a named source;
    - change a decision made on the board so the document reads better;
    - create tickets, or send the PRD to anyone.

## The sections

1. Status: ready or not, and how many open questions.
2. The problem, and for whom.
3. The test that comes first: hypothesis, cheapest test, threshold, what we decide if we miss it.
4. Goals, and what is not a goal.
5. What we build, and the alternatives we discarded.
6. Requirements by priority, each with how we know it is met and the failure it answers.
7. Edge cases and errors.
8. How we measure it.
9. Phases, and what is left out with its reason.
10. Open questions: question, owner, date, status.

When the person asks for the long version, add user stories by priority, requirements that are not about function (performance, security), dependencies and a launch plan with the criteria to roll back.

## Commands

```
prd_check.py check  <prd.json>
prd_check.py gate   <prd.json>
prd_check.py render <prd.json>
```

Tests: `python3 test_prd_check.py`.

## Where the rules come from

The test before the spec, with a threshold that triggers a decision: experiment-first roadmaps as practiced in AI-native product teams, and the riskiest-assumption tradition of Marty Cagan and of David Bland and Alex Osterwalder. Reading what is written before asking, marking unknowns with an owner, listing what is left out with its reason and the alternatives discarded: the way Productboard Spark builds its specs. One question per turn with the recommended option first: Dean Peters, `workshop-facilitation`. The trace from each requirement to a failure the person discussed is this kit's own.
