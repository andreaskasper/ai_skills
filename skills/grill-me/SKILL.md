---
name: grill-me
description: Interview the user relentlessly about a plan, decision or idea, one question at a time, until both sides share the same understanding. Use when the user wants to stress-test a plan, find gaps before building something, or says "grill me". Triggers include "grill me", "stress-test my plan", "poke holes in this", "challenge my idea", "play devil's advocate", "what am I missing", "grill mich", "löchere mich", "Stresstest für meinen Plan", "stell mir kritische Fragen", "hinterfrag meinen Plan", "spiel Advocatus Diaboli".
---

# Grill Me

Interview the user relentlessly about every aspect of their plan until you both have the same understanding of it. Walk down every branch of the decision tree and resolve the dependencies between decisions one after another. For every question, also give your recommended answer, so the user can simply confirm or correct it.

## Self-improvement
If a run deviates from this skill (an error or field not covered here, a changed UI, you had to improvise, the user corrects the result), finish the task first, then load the `skill-self-improvement` skill and propose an improvement. Don't edit the skill files directly: in Claude apps they are a read-only copy. Typical signals here: the user asks for fewer or more questions per message, rejects the recommendation format, says a question was answerable from the files, or wants a different summary at the end.

## How to ask

- **One question per message.** Wait for the answer before moving on. Several questions at once are confusing and get half-answered.
- **Order by dependency.** Ask first about decisions that others depend on (goal, audience, constraints, budget, deadline), then the details that follow from them.
- **Recommend.** Format: the question, then "My recommendation: …" with a one-line reason.
- **Look things up yourself.** If a fact can be found by exploring the environment (files, repo, tools, docs), find it instead of asking. The decisions, however, belong to the user: put each one to them and wait.
- **Push back** when an answer contradicts an earlier one, is vague, or hides a risk. Name the conflict and ask again.
- **Keep a running list** of what has been decided. Offer a short summary every 5–7 answers or when the user asks.

## When to stop

Stop when every open branch is resolved or explicitly parked. Then present:

1. Decisions made (one line each).
2. Parked questions and risks.
3. The next concrete step.

**Do not start implementing** until the user confirms that you share the same understanding.

Answer in the language the user writes in.
