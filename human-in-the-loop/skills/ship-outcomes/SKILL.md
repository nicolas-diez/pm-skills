---
name: ship-outcomes
description: "Turns a feature request into an outcome you can test and measure, with four questions asked one at a time: what behavior changes, which assumption would kill it, what is the cheapest test, how will we measure it. Use when someone brings a request such as «we need a dashboard» and you want to think it through before writing a spec."
when_not_to_use: "Do not use when the outcome is already defined and tested, or to audit a product that already exists."
---

# Ship Outcomes

> A feature is a bet that some behavior will change. Name the behavior before you build the bet.

The four questions come from Nicolas Liatti's lesson "Use AI to Ship Outcomes, Not Features". This skill runs them as a conversation: the AI generates the options, and the person chooses and defends the choice. It ends in a one-page Outcome Brief that takes the place of the feature spec, and that page is the starting point of `miro-product-workshop`.

## How it behaves

- **One question per turn.** Generate the options, say which one you would pick and why, then stop and wait. Never run the four questions in one go.
- **The person's context decides.** The model ranks blind: it does not know the company or its strategy. Ask for that context before the person chooses, and do not choose for them.
- **Carry each answer forward.** The behavior chosen in question 1 is quoted word for word in questions 2, 3 and 4.
- **Nothing invented.** If you do not know who the stakeholder is or who the users are, write `[TBD]` and say who could fill it.
- **The request is never executed as written.** It always goes through question 1 first.

## The steps

**0. Capture the request, word for word.** If it already is a measurable outcome ("raise retention by a set amount"), say so and go straight to questions 3 and 4.

**1. What behavior is this betting on?** List five user behaviors the request assumes will change, from most to least likely, each with its risk. The same request is five different products depending on which one is true. Point at the core bet: the behavior without which the rest does not matter. Looking at something is not a behavior change; doing something different afterwards is. Ask which one the person wants, given their strategy.

**2. What has to be true?** Name the one assumption that, if false, makes the whole request useless. Then the reality check: ask the person to get, from whoever made the request, the last concrete time someone got something wrong because this was missing. A vague answer or "it would be nice to have" means the pain is not there. If nobody can name one instance, stop.

**3. What is the cheapest test?** Design three ways to learn, in two weeks or less and without building the feature, whether that behavior is reachable. Order them from cheapest to most expensive. They usually look like this:

- deliver the result by hand to a few target users and watch whether anyone acts on it;
- offer "early access" that is really a document you update by hand, and watch what people do after opening it;
- sit with a few users, show them what the feature would show, and ask them to walk you through what they would do next.

If people do not act when the result is handed to them, the feature will not fix it. Ask which test the person runs, and in how many days.

**4. What number says it worked?** Three horizons, all about behavior and none about feature adoption: a leading sign in week one, a metric at one month with its bar set before starting, and a lagging sign at ninety days. Logins, page views and "feature enabled" do not count. Confirm the three and the one-month bar.

**5. The Outcome Brief.** One page, titled with the original request:

1. The five behaviors, ranked, with the chosen bet marked.
2. The one assumption that has to be true, and the reality check.
3. The three tests by cost, and the one chosen with its timebox.
4. The three metrics and the one-month bar.

Give the page back to whoever made the request. Either they rethink it, or they say their bet was a different behavior, and now you agree on the outcome before anyone writes a spec.

## Into the workshop

The four answers pre-fill four frames of `miro-product-workshop`: the behavior goes to the goal, the assumption to the assumptions strip, the cheapest test and the metrics to the frame where the idea is chosen. The person still decides each of those frames.

## What it never does

- Pick the behavior for the person.
- Move to the next question without their answer.
- Accept a metric that counts usage instead of a change in what people do.
