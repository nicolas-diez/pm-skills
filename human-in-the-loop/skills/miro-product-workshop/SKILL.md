---
name: miro-product-workshop
description: "Product workshop on a Miro board with the person in the loop. The AI drafts every frame (goal, customer, moment, failures, ideas, choice and metrics, growth) and the person decides them one at a time; nothing advances without their answer. Use before writing a product document or a deck, starting from a brief, a one-pager or an own idea, when the user says «armemos el taller», «pasemos esto por Miro», «validemos la idea» or «workshop this»."
when_not_to_use: "Do not use when the request is still a feature with no goal (run ship-outcomes first), for a dataset diagnosis that already has its own skill (growth-diagnostic), to draw architecture or flow diagrams, or to produce a finished board with nobody to discuss it with."
---

# Miro Product Workshop

> The AI drafts the board. You change its mind, one frame at a time.

A product case usually goes wrong before the first slide: the solution is written into the goal, the customer is chosen from a hunch, nothing is compared with what people do today. This skill puts a board between the request and the deliverable. The AI fills it with a first draft, and then the person discusses it frame by frame. The record of what they changed is the output that matters.

## What is in this folder

| File | What it is |
|---|---|
| `TEMPLATE.md` | The frames, their boxes and the question each one asks. Two rows: design (seven frames) and diagnosis (three) |
| `workshop_log.py` | The decision log and its gates. It refuses to open a frame before the previous answer |
| `board_svg.py` | Draws the board, empty or filled from the log, as SVG for Miro's connector |
| `examples/bike-repair-workshop-log.json` | A complete log of an invented case, with four decisions changed |
| `examples/chrome-workshop-log.json` | A classic exercise, "improve Chrome". The draft follows a public walkthrough and the review is a reconstruction; its title says so |
| `LOCAL.md` | Optional. This workspace's boards, sources, paths and lessons. If it exists, read it first |

## How it runs

1. **Read first, ask later.** Read everything the person gave you (the one-pager, the brief, the evidence). Sort what you found into four piles: known, assumed, missing, in conflict. Do not ask for anything you can find.
2. **Pick the row and say why in one line.** Building or improving a product, a strategy or a launch: the design row. A metric that moved: the diagnosis row. If what you got is a solution with no goal behind it, stop and run an outcome pass first (`ship-outcomes` if it is installed).
3. **Start the log and draft every frame.** `workshop_log.py new`, then one `draft` per frame with the fields from `TEMPLATE.md`, the question for the person and your proposed answer with its reason. Register every number with `number`: a source, or `"assumption": true`. What is missing is written `[TBD]` and listed in the assumptions strip with an owner and a suggested next step. Never fill a gap with an invented fact.
4. **Check your own draft before showing it.** `workshop_log.py check --draft` looks at your draft of every frame. If it finds a solution before frame 5, a number with no source, or a frame missing what the template asks for, fix the draft. A sized assumption is welcome as long as it is marked as one and says how you got to it: it is exactly what the person will want to challenge.
5. **Build the board.** Copy the template to a new board and fill the boxes from the log. Frame 0 carries a two-column table: what the AI drafted, what it will ask you. Stamp every frame `Draft`.
6. **One frame at a time.** For each question frame:
    - `workshop_log.py open <frame>`. If it says "not yet", go back: you skipped an answer.
    - Tell the person where they are ("Frame 3 of 8"), what the draft says in five lines or fewer, and the question.
    - Give two or three options with the one you recommend first and why. Then wait.
    - Record their answer in their own words with `decide`: `kept` or `changed`, and what changed and why.
    - Update the frame on the board and its stamp (`Decided` or `Changed`). If the change touches later frames, redraft those before opening them and say which ones you redrafted.
7. **Close.** `workshop_log.py check --close`, then `summary`. Show the table "what the draft said, what you changed". The workshop is done when no frame is waiting and no check fails. Ask where it ends: the board as the deliverable, a document, or a deck (`workshop-to-deck`).

## Writing on the board

- **Use the Miro connector (Miro's MCP server) when it is authorized.** It reads and writes a board as an SVG document.
    - `board_svg.py template` draws the empty template and `board_svg.py from-log <log.json>` draws a board filled from the decision log. Both escape the text for you. Send the output with the connector's create call, to a board of your own.
    - Load the connector's composing guide once per session before the first write; it is the authority on the SVG grammar and it changes.
    - There is no tool to duplicate a board. Create a new board and draw the template on it.
    - To change a frame after a decision, send an update with the ids the create call returned: only the boxes that changed, plus the status stamp.
    - The connector can delete items. Never send a deletion on a board you did not create in this workshop.
    - After writing, read the board's overview back and check the frame count.
- **If there is no connector, use the browser** in a tab of your own, never the one the person is looking at, and verify each box after writing it.
- **If there is no Miro at all, run the workshop in chat** with the same log and gates, and build the board afterwards from the log.
- Either way: the person's template board is copied, never edited, and you never change who can see a board.

## What it does alone, what it asks, what it never does

- **Alone:** read the sources, draft the frames, build and update the board, keep the log, run the checks.
- **Asks:** the decision of every frame; anything that leaves the person's Miro (sharing a link); where the workshop ends.
- **Never:**
    - open a frame without the answer to the previous one;
    - present a frame as text to approve instead of a question;
    - write a solution before frame 5;
    - use a personal anecdote as evidence, or an unsized hunch as the reason to pick a customer;
    - put a screenshot with the person's personal data on the board;
    - record an answer the person did not give, or reword it into agreement.

## When the board is for a live case

This applies only when the board itself is what gets presented. If the person will present the board live (a review or a case with a time limit), add three things while drafting: the hypothesis in frame 6 has to be written before three quarters of the time is gone, every frame ends with a question to the room, and the scoring table in frame 5 is skipped. Classic frameworks (SWOT, five forces) are not drawn on the board; the frames are the structure.

## How we know it works

The number to watch is how many decisions the person changed against the first draft. `summary` prints it. If it is zero three workshops in a row, the workshop is ceremony: cut it down to the frames that did change in earlier runs.

## Commands

```
workshop_log.py new     <log.json> --case "..." [--type design|diagnosis] [--lang en] [--board URL]
workshop_log.py draft   <log.json> <frame> --from <payload.json>
workshop_log.py number  <log.json> --from <payload.json>
workshop_log.py open    <log.json> <frame>
workshop_log.py decide  <log.json> <frame> --from <payload.json>
workshop_log.py check   <log.json> [--draft | --close]
workshop_log.py summary <log.json>
```

`check --draft` is for step 4, plain `check` looks only at decided frames, and `check --close` also fails while a frame is waiting.

```
board_svg.py template [--row design|diagnosis|both] [--lang en|es|both]
board_svg.py from-log <log.json> [--lang en|es|both]
```

Payloads are JSON files, never inline. Tests: `python3 test_workshop_log.py`.

## Where the method comes from

Goal and user before ideas, and the walk from user to use case to failure to idea: Gayle Laakmann McDowell and Jackie Bavaro, *Cracking the PM Interview* (the chapters on product and case questions), and Jackie Bavaro's later writing on product sense and strategy. Request to outcome: Nicolas Liatti, "Use AI to Ship Outcomes, Not Features". One question per turn with the recommended option first: Dean Peters, `workshop-facilitation`. Marking gaps instead of inventing, and showing a change as before and after: the way Productboard Spark presents AI drafts. The person decides and the AI proposes: Peter Yang's document review loop.
