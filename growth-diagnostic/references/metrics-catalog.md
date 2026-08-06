# Metrics catalog and possible pains

Run EVERYTHING applicable; explicitly declare what cannot be measured with the available data ("knowing what the dataset does NOT tell you is part of the analysis") and what instrumentation you would request. For each metric: value, monthly trend, exit state, and which of its pains appears.

## 0. Lifecycle definitions and metric taxonomy (know these cold before running anything)

**Customer lifecycle stages:**

- **Acquisition:** getting a new user to sign up or arrive at the product for the first time.
- **Activation:** getting that user to complete the first value action (e.g. their first order).
- **Frequency:** increasing how often the customer uses or buys.
- **Retention:** keeping the customer active after a given period.
- **Reactivation:** recovering inactive customers so they come back.

**Where does churn go?** Churn is not a managed stage: it is the exit state, and it can happen from any stage. A user can churn right after activation (one-and-done), from an established habit, or from a mature base. It is measured inside Retention (churn rate = 1 − retention rate) and its output, the inactive pool, is Reactivation's raw material. Track WHERE users churn from, not just how many: each origin has a different fix.

**Top metrics per stage (the short list that can never be skipped):**

- Acquisition: CAC, CTR, CPA, signup rate
- Activation: Time to First Order, First Order Rate, Activation Rate
- Frequency: Orders per User, Days Between Orders, Purchase Frequency
- Retention: Retention Rate, Churn Rate, Cohort Retention
- Reactivation: Reactivation Rate, Time to Reactivate
- Customer value: LTV, ARPU, AOV, Revenue per User

**Three lenses for reading any metric:**

- **Pass-through (Conversion Rate):** % of users completing a target action (visit → signup, signup → first purchase). Answers: is the funnel converting?
- **Intensity (Order Rate):** average orders per user in a period. Answers: are the people we have using it more?
- **Durability (Retention):** % of customers still active after a period. Answers: do they last?

Every diagnosis states which lens each reported metric belongs to. "Usage is up" only becomes actionable once you know whether more people converted, the same people used it more, or people lasted longer.

## 1. AARRR funnel, stage by stage (compute every one or declare not-computable)

| Stage | Metrics (all of them) | Possible pains to check |
|---|---|---|
| Acquisition | New users/month; CAC, CTR, CPA, signup rate (if marketing data exists; if not, declare it) | Bought growth over a broken funnel ("leaky bucket"); acquisition mix degrading cohort quality (new-cohort M1 falling) |
| Activation | Time to First Order; First Order Rate; Activation Rate (% with 2nd transaction at 14/30d, THE metric in frequency businesses) | The pain is rarely the 1st use (often same-day); it's the 2nd. First experiences landing in bad-service moments/zones killing conversion |
| Frequency | Orders per User; Days Between Orders; Purchase Frequency; % of actives above a high bar (4+); % scheduled/recurring behavior | Healthy frequency among actives but a rotating base (averages hide it); heavy users inflating means (use medians) |
| Retention | Retention Rate; Churn Rate; Cohort Retention (M1+ triangle); month-over-month base retention | Two simultaneous truths: mature-base retention improving while new cohorts enter worse (mix effect). Cut M1 by zone/time-slot/channel of first use |
| Reactivation | Reactivation Rate (% of inactive pool returning/month); monthly hazard P(return given d months inactive); Time to Reactivate | A closing rescue window (return probability can halve per inactive month); structurally expensive late win-back; organic reactivation as natural control |
| Customer value | LTV; ARPU; AOV; Revenue per User (by segment) | Growth 100% from user count and not unit value; revenue concentration (top 10%/20%) as both risk and lever |

## 2. Marketplace metrics (two-sided or three-sided)

- Liquidity: fulfillment rate, unfilled/not-found rate, by hour × day × zone.
- Service level: wait/delivery time (SEPARATE on-demand from scheduled: scheduled has "negative wait" and contaminates aggregates), % under an excellence bar.
- **Supply side (the analysis almost nobody runs, and it explains demand plateaus):** active providers/month, load per provider, supply concentration, supply churn. Compare demand growth vs supply growth.
- Failure funnel: decompose non-completed transactions by cause AND by circumstance reconstructed from timestamps (with/without assignment, time until cancel, before/after scheduled time). Never treat "cancellation" as one phenomenon.
- Geo: ~1km grid cells with volume, fulfillment, median margin; cross health × profitability ("money on the table": high-margin, badly served zones).
- Product mix/tiers: volume, economics, and service per tier; small pilots as internal evidence (small n = caveated anecdote, not proof).

**Three-sided marketplaces (e.g. delivery: consumers + couriers + merchants).** Everything above, plus:

- **One health read per side, never a merged "supply":** couriers and merchants are different populations with different economics, churn dynamics, and concentration. Run actives/month, load, concentration, and churn separately for each.
- **Find the binding constraint by slot and zone:** at any given hour the bottleneck is ONE side (no couriers online, merchant closed or out of stock, or no demand). Incentives aimed at the wrong side are pure waste. Build the failure funnel with per-side attribution: every failed order labeled by which side caused it (courier not found, merchant rejected/out of stock, consumer canceled).
- **Cross-side balance metrics:** orders per active courier per hour, orders per active merchant, courier utilization (time on task vs online), merchant fill/acceptance rate, and prep time vs delivery time split (which side makes the customer wait?).
- **Unit economics split across sides:** the take comes from several pockets (merchant commission, delivery fee, service fee, ads/monetization). Report contribution per order with its composition, and margin per side: a growth lever that improves one side's economics can quietly destroy another's.
- **Lifecycle runs per side too:** merchants and couriers have their own acquisition, activation, retention, and reactivation. The AARRR sweep of section 1 applies to each side the dataset covers; declare which sides the data lets you see.

## 3. Growth accounting (Hsu / Social Capital)

MAU decomposed as new + retained + resurrected − churned; quick ratio = (new+resurrected)/churned (consumer: >1 typical, 1.5+ strong); same accounting on revenue if data allows. Detects "growing, but the engine is losing efficiency".

## 4. Unit economics (CFO frame, see frameworks.md)

Contribution margin per transaction (median, not mean: cost outliers) and its distribution by zone/slot/segment/tier; LTV per segment; LTV/CAC as the yardstick to compare initiatives AGAINST EACH OTHER; payback. Absolute margin may depend on field interpretation (`[VALIDATE]`); relative comparisons stay robust.

## 5. Behavioral risk signals

Measurable churn-associated factors: self-cancellation rate (master symptom of waiting), failed last experience before leaving, hourly/zonal profile, service gradient by segment (are the ones leaving the worst served?). All as associations → they feed CRM triggers and experiments.

## 6. Minimum mandatory statistics

- Medians for amounts/times (outliers); document when you use means and why.
- Last-period censoring: cohorts without a full window are excluded or flagged.
- Experiment sample size: n = (z_α/2·√(2p̄q̄) + z_β·√(p1q1+p2q2))² / Δ²; minimum detectable effect defined BEFORE launch.
- Weekly cuts only if n/week supports them (declare the noise); otherwise monthly, and say so.
- Distinct counts and percentiles: verify your tool computes them correctly.
- Correlation is never causation: associative findings are labeled as such and resolved through experiments, not rollouts.
- Mix effects (Simpson's paradox): an aggregate can improve while every segment worsens, or vice versa. Always check whether a trend survives segmentation before reporting it.
- Survivorship bias: metrics computed only on users who stayed (e.g. frequency of actives) say nothing about the ones who left. Name the population every metric describes.
- No assumptions sold as facts: anything inferred (units, field meanings, causes) is tagged `[VALIDATE]` and listed as an open question.

## Source discipline (mandatory)

Every figure that does not come from the dataset carries its source and date, inline where it is used. Benchmarks report ranges and the proxy type (survey, downloads, filings), never invented precision. Each run's deliverables include a **consolidated source list** (in the pre-analysis doc and the Excel benchmark sheet) so anyone can retrace every external claim.

## 7. Classifying the inventory: how the NSM, tree, and guardrails emerge

After the sweep, every computed metric gets ONE role:

| Role | Criteria |
|---|---|
| **North Star Metric** (pick 1) | Behavioral and countable (counted, not modeled or debated) · leading (moves week to week) · captures the business's value-creation moment (the "aha") · links acquisition to habit · a CFO reads it as an LTV factory |
| **Tree KPI** (1-2 per stage) | Best explains its lifecycle stage AND has a measurable baseline · if two compete, the one with the bigger pain or the more direct lever wins |
| **Guardrail** | What growth initiatives can silently break: service level, margin, incentive spend %, cohort quality · also: ALREADY-SOLVED metrics that must be protected (the fixed gets defended, not re-proposed) |
| **Diagnosis only** | Context or hypothesis-killing, not operated · goes to the annex, not the tree |
| **Discarded as a lever** | The metric is HEALTHY and stable: document the data-backed why. An argued "no", not an omission |
| **Not computable** | The data doesn't allow it: declared, and converted into a day-1 instrumentation request |

## 8. The discard registry (saying no, with the data)

Every diagnosis ships a **discard registry**: an explicit table of what you are NOT doing and why, each row backed by a number. Prioritization is judged as much by the no-gos as by the yeses; a discard argued with data scores, an omission does not.

Format: what was discarded | the data-backed why | where it's auditable (sheet/source).

The recurring discard categories (check all of them):
- **Healthy metric:** the lever targets something stable and fine (e.g. frequency of actives). Show the flat series.
- **Already solved:** the time series shows it got fixed during the period. Proposing it would be proposing the past.
- **No data:** the dataset has no attributes to measure it. Out of scope as an initiative; in scope as an instrumentation request.
- **Too late by design:** the window already closed (e.g. win-back at 90+ days when return probability collapsed). Show the decay.
- **Structurally lost game:** a war the company cannot fund (e.g. price war against subsidized rivals). Show the economics, and internal evidence if a past pilot exists.
- **Someone else's scope:** real opportunity, wrong owner. Name it, hand it off, don't absorb it.

Anti-pattern this prevents: picking the NSM first and hunting for numbers to justify it. The right order is sweep → inventory → pain/value per stage → the NSM emerges. If two NSM candidates survive, present both to the user (G2) with the trade-off.
