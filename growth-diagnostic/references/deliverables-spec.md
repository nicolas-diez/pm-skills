# Spec of the 4 deliverables

## 1. Pre-analysis doc (md, the living document)

Where the thinking happens. Sections: the real brief (reread the original ask, not a summary) · findings with numbers per run · competitive context with sources · benchmark · alternative proposals with pros/cons and ONE recommended · answers to every user question in dated sections · chronological audit of every number (table: figure, full period, exit state, verdict) · final proposal with the discard registry · pending items. Every claim cites its run. This doc IS the defense backup; never deleted, only versioned.

## 2. Auditable Excel (the trust deliverable)

- `Data` sheet: the COMPLETE raw dataset as received (credibility of working on the real data) + row-wise helper columns. With >20k rows: live formula in row 2, rest pasted as values, documented (standard performance practice).
- Entity sheets (customers, providers): one row per entity, all COUNTIFS/SUMIFS/MINIFS/MAXIFS over Data; segmentation with parameters in EDITABLE BLUE CELLS (change the threshold, everything recalculates); monthly activity matrix per entity (enables growth accounting and reactivation hazard via SUMPRODUCT).
- Numbered analysis sheets (monthly, segments, zones, day/slot, failures, reactivation, tiers): 100% formulas. Conditional medians: array MEDIAN(IF(...)).
- `README` sheet: how to read the file, color convention (blue=input, black=formula), assumptions, edge cases, recalculation note.
- Benchmark sheet: the ONLY one with external data, every row sourced.
- `Charts` sheet: native charts referencing the tables.
- **Proven technical workarounds:** headless LibreOffice cannot recalculate workbooks with many array formulas over 20k+ rows (hangs). Fix: (1) bake helpers except row 2; (2) validate array semantics in an isolated mini-file against pandas; (3) set `fullCalcOnLoad = True`; (4) warn "recalculates on open in Excel/Sheets, 1-2 min". AGGREGATE(16,6,...) does NOT work in LO for conditional medians (#DIV/0!): use CSE MEDIAN(IF). MINIFS/MAXIFS need the `_xlfn.` prefix.
- Mandatory verification: Excel outputs compared against the pandas run BEFORE delivering.

## 3. Deck (10-15 slides + annexes)

- Structure: cover · recommendation with anchor numbers · context/stage · business health · service level · segments/retention · NSM + tree with baselines · prioritized levers (cards with budget weight in the footer) + no-gos · deep experiment · budget · constrained scenario (if applies) · declared risks and assumptions · close with 30/60/90 · Annex A benchmark · Annex B Excel index ("how to audit every number").
- **Every content slide: 1-2 charts validating that slide's thesis.** Chart type by message: line = evolution/trend; horizontal bar = segment comparison (the value gap); vertical bar = decay/stages; pie/donut only for composition of a total; table when the detail IS the message. Native charts, never images.
- **Source footer on every slide:** "Source: [dataset]. Auditable in Excel annex: sheet X" or the external source. This is what builds trust with audiences that don't know you.
- Action-title headlines (claim + number). No AI tells in shipped text. Final copy belongs to the user (G5): offer title options for the hook slide.
- Proven tooling: pptxgenjs (full control, exact numbers) → PDF via LibreOffice. Gamma caps generations at 10 cards: useless for 13+.

## 4. Defense brief (md)

Per slide: **Thesis** (the opening line, spoken not read) · **Points** in order (each with its number and Excel sheet in parentheses) · **If they ask** (most likely follow-up + short answer). Plus: technical questions appendix (sample size derivation, why the NSM is not LTV, where the budget cap comes from) · opening guide (30 seconds of framing before the cover) · a closing question to ask the panel · **10 pocket numbers** to memorize. The winning live move: questioned number → open the Excel → sheet → formula → raw data.
