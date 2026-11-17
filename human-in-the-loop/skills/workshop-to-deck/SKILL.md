---
name: workshop-to-deck
description: "Turns a discussed workshop board into a deck. It starts from the decision log, writes a slide script the person approves slide by slide, and only then spends one generation; every number on a slide traces back to the board or to a named source. Use when the user says «pasemos el tablero a un deck», «armá la presentación del taller» or «make the deck from the board»."
when_not_to_use: "Do not use without a discussed board or decision log (run miro-product-workshop first), to restyle a deck that already exists, or to send or share the deck: that is the person's call."
---

# Workshop to Deck

> The deck says what the board decided, and every number can be walked back to it.

A deck written from a blank page drifts from what was agreed. This skill starts from the decision log of the workshop: the goal, the customer, the failure, the chosen idea and the metric are already there, with what the person changed. The slides only have to tell it in order.

## What is in this folder

| File | What it is |
|---|---|
| `deck_script.py` | Checks the slide script and gates the one generation |
| `examples/bike-repair-deck-script.json` | The script of an invented case, built from the workshop example |
| `LOCAL.md` | Optional. This workspace's deck tool, brand notes and lessons. If it exists, read it first |

## How it runs

1. **Read the decision log and the brief.** If there is a brief (a request from a stakeholder, a client's question), write the table "what the brief asks, which slide answers it". If there is none, the brief is the question the board set out to decide.
2. **Write the slide script** as a JSON file (see the example). The arc of the deck is the arc of the case: goal, user, failure, ideas, the chosen one and why, how it is measured, phases, and a close with the one-sentence summary from frame 7. Slides outside the arc (a benchmark, an appendix) are tagged `other`.
    - **The title is the claim**, with the number inside when there is one. "The problem" is a label; "Today she calls three shops to find a slot" is a claim.
    - **Every number carries its trace:** `log:<frame>` when it comes from the board, `evidence:<item>` or `source:<url or document>` otherwise, and the source goes in the slide footer.
    - **Images are your own** (rendered from your data or captured by the person), each one checked for personal data.
3. **Run `deck_script.py check`** and fix what it finds.
4. **Show the script to the person, slide by slide.** One slide per turn when the deck is short; in groups of the arc when it is long. Mark each slide `approved` only with their yes.
5. **Run `deck_script.py gate`.** It opens only when every check passes, every slide is approved and nothing was generated yet. Then ask the person before generating: it spends credits.
6. **Generate once**, with the brand style the person named, keeping the text of the script as written. Record it with `deck_script.py record`.
7. **Fix by editing, never by generating again.** Then export the PDF if the person wants one.

## What it does alone, what it asks, what it never does

- **Alone:** read the log, write and check the script, prepare the images, apply edits after the generation.
- **Asks:** the approval of each slide; the go to generate; the brand style when it is not obvious; opening access to the deck.
- **Never:**
    - generate before the gate opens, or a second time;
    - put a number on a slide that is not on the board or in a named source;
    - change a decision the person made on the board to make the story neater;
    - send or share the deck.

## Checks the script has to pass

1. Every point of the brief has a slide that answers it.
2. Every title is a claim, and every number traces to the board or to a source.
3. The slide cap holds, slides with numbers carry their source in the footer, and no image was left unchecked for personal data.
4. One generation per deck.
5. The deck follows the arc of the case and closes with one sentence.
6. The text has no em dashes and passes your plain-language edit (`no-ai-slop` if it is installed).

## Commands

```
deck_script.py check  <deck.json>
deck_script.py gate   <deck.json>
deck_script.py record <deck.json> --id <generation id or url>
```

Tests: `python3 test_deck_script.py`.

## Where the rules come from

The arc of the case and the one-sentence close: McDowell and Bavaro, *Cracking the PM Interview*. How to open, how to close and what a slide is for: Patrick Winston, "How to Speak". The title as a claim with the number inside, and the source in the footer: lessons from decks built with this workflow.
