# Spoke: this week's open slots (invented example)

**Status:** ready for engineering. 2 open questions.

## The problem, and for whom

A rider with a broken bike cannot tell which shop can fix it this week or what it will cost. Today she calls two or three shops, or rides to the nearest one and waits.

The daily commuter. We assume commuters are 60% of repair demand, and they are the only group that needs the bike back the same day.

## The test that comes first

- **Hypothesis:** If commuters see this week's open slots, the share of started bookings that complete goes from 40% to 55% in six weeks.
- **Cheapest test:** Three shops update a shared sheet every morning, and the app shows those slots by hand. No calendar is built for this.
- **Threshold:** At least 55% of started bookings complete across the three shops.
- **If we miss it:** We do not build the calendar. We go back to the board and take the next failure, the unknown price.

## Goals

- More riders complete a first repair booking.
- A commuter can see, before leaving home, which shop takes the bike today.

**Not a goal:**

- Growing app downloads. Shops pay when a repair gets booked, not when the app is installed.

## What we build

An open-slot calendar: each shop marks its free slots for the week, and a rider books one. It removes the first reason a booking does not start.

| Alternative we discarded | Why |
|---|---|
| Fixed-price menu | It answers the second failure. It comes after the calendar proves that visible slots move bookings. |
| Loaner bike | A bold bet with stock and insurance behind it. Not before the calendar test. |
| Office pickup | Added in the workshop for the commuter who cannot reach the shop. It needs logistics we do not have yet. |

## Requirements

| Id | Priority | Requirement | Done when | Answers |
|---|---|---|---|---|
| R1 | P0 | A shop can mark its free slots for the week in under a minute a day. | Each pilot shop updates its week on every working day of the first week, without help. | Failure: No visible slots |
| R2 | P0 | A rider sees today's and this week's free slots for the shops near her route. | A rider who opens the app sees at least one bookable slot, or is told that there is none this week. | Failure: No visible slots |
| R3 | P0 | A rider books a slot and both sides get a confirmation. | After a booking, the rider and the shop each hold the same day, time and repair, and the slot is no longer offered. | The goal |
| R4 | P1 | A slot that the shop has not confirmed that morning is shown as unconfirmed, not as free. | No booking can be made on a slot the shop has not confirmed that day. | Failure: No visible slots |
| R5 | P2 | The rider sees when the bike will be ready. | Every confirmed booking shows a ready-by day that the shop entered. | Failure: A day without the bike |

## Edge cases and errors

- **Two riders take the same slot:** The first confirmed booking keeps it. The second rider is told at once and offered the next free slot.
- **The shop did not update its slots today:** Its slots show as unconfirmed and cannot be booked until the shop confirms.
- **The rider does not show up:** The shop marks a no-show. The slot is not reopened for that day.

## How we measure it

- **North star:** First bookings completed per week
- **Primary:** Share of started bookings that complete
- **Secondary:** Time from opening the app to a confirmed slot
- **Guardrails:** Shop no-shows and cancellations do not rise

## Phases, and what is left out

1. Three shops, by hand
2. One neighborhood, calendar in the app
3. The city, with the price menu

**Left out:**

- Payments in the app. The rider pays at the shop, as today. Not needed to learn whether visible slots move bookings.
- Prices. That is the next failure on the board, and it has its own test.

## Open questions

| Question | Owner | Due | Status |
|---|---|---|---|
| Do shops accept updating their slots every morning for six weeks? | Product | Before the pilot starts | open |
| How far from her route does a commuter accept a shop? | Design | End of the first pilot week | open |
