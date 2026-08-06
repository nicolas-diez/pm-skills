# growth-diagnostic

A Claude skill that turns a raw transactional dataset into a full growth diagnosis and a defensible strategy, with auditable deliverables: a formula-based Excel workbook, a chart-first slide deck, and a per-slide defense brief.

## Why an AI-native PM built this

As PMs we own growth outcomes. Across marketplaces, fintech, transactional products, pricing and monetization, I kept rebuilding the same work from scratch: weeks spent extracting data, applying best practices, building tables and charts before any strategy conversation could even start. So I encoded the method once. With AI it now runs in a one or two hour session and delivers a clear diagnosis of the business's problems and pains plus a growth and monetization strategy, with a human in the loop validating every step of the process.

Part of [pm-skills](../../), my open collection of AI-native product management skills.

## What it does

1. **Data quality and schema inference:** units, timezones, edge cases, documented assumptions.
2. **Chronology first:** every metric monthly (weekly when volume allows) before any aggregate. What already got fixed during the period becomes an observation, never an initiative.
3. **Exhaustive metric sweep:** every metric in the catalog is computed or explicitly declared not-computable. The output is a classified inventory from which the North Star, KPI tree, and guardrails emerge (instead of being picked by intuition).
4. **Benchmark and company history:** what competitors do, and what the company itself already tried and killed.
5. **Strategy:** NSM + tree with real baselines, 3-4 prioritized levers with quantified criteria, explicit no-gos backed by data, one deep experiment with statistical power sizing, incrementality-based budget with caps.
6. **Deliverables:** pre-analysis doc, formula-based Excel (raw data + auditable calculations + assumptions sheet), chart-first deck with action titles and per-slide sources, and a defense brief.

## What you get

- An exhaustive diagnosis of the dataset and the business: health read metric by metric, with trend and exit state.
- Context and the top problems, prioritized: what is broken, what is already fixed, and where the money is bleeding.
- The top initiatives to attack those problems, prioritized by impact (incremental LTV per dollar, pool size, time to impact), each with the data that backs it and the no-gos made explicit.
- An A/B test plan designed to land a first win and learn: numeric hypothesis, test/control, sample size by statistical power, guardrails, kill/scale criteria.
- A competitor benchmark with sources, plus the company's own history of attempts.
- Full chart support and every analysis backed by specified formulas over the raw data, so a human can validate any number in minutes.
- Statistical discipline built in: nothing assumed or invented, correlation never sold as causation, assumptions tagged for validation, and a consolidated list of every external source used.

## Human in the loop

The skill stops at five gates: field interpretation, diagnosis verdicts, initiative selection, number validation against the Excel, and final copy (always the human's voice).

## Install

Download `growth-diagnostic.skill` (or copy the folder) and add it to your Claude skills. Works in Claude Code and Cowork.

## Credits and influences

The storytelling structure borrows from CFO-style narratives (unit economics → customer lifetime value → where the next unit of budget goes), with a strong focus on problem solving: headline-first slides where every claim carries its number and one message per chart. The metric checklists draw on public frameworks by Andreessen Horowitz (a16z, 13 marketplace metrics), Jonathan Hsu at Social Capital (the growth accounting framework), Lenny Rachitsky (marketplace metrics), and Reforge (cohort analysis).
