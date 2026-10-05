---
name: skill-self-improvement
description: "Turns what went wrong or differently in a skill run into a clean, tested improvement of that skill and hands it over for approval. Use when another skill says to (its Self-improvement block), or when the user says \"learn from this\", \"remember this for the skill\", \"update/optimize the skill\", \"skill review\", \"lern daraus\", \"merk dir das für den Skill\", \"optimier den Skill\", \"Selbstoptimierer\", \"das war falsch, nächstes Mal so\". Also runs a batch review of parked skill learnings."
---

# Skill self-improvement

A skill gets better only when a real run shows a gap, and only if the fix is folded into the rule it refines. Appending dated "learnings" makes a skill longer and contradictory; that is the failure this skill exists to prevent.

## Ground rules

- **The skill files you can see are a read-only copy.** In Claude apps, skills are synced into the session; editing them there changes nothing and is lost on the next sync. Changes reach the user only through a hand-over (see Step 6). Never edit the copy and report it as done.
- **Finish the user's task first.** Improvement happens after the work, as one combined change per skill per session, never mid-task.
- **Evidence, not speculation.** A change needs an API response, an error, official docs, or the user's own statement. Your guess about what might be nicer is not evidence.
- **No secrets.** Credentials never go into a skill. Skills name the credential source (proxy target or environment variable), not the value. If the current skill contains a secret, remove it as part of the change and tell the user to rotate it.
- **Approval stays with the user.** You propose; the user saves. Behaviour changes to a workflow that still works (different defaults, removed steps) need an explicit OK first.

## Workflow

Copy this checklist and tick it off:

```text
Self-improvement:
- [ ] 1 Evidence written down
- [ ] 2 Bar checked: change the skill, or park the learning
- [ ] 3 Current skill read in full
- [ ] 4 Principle found, lines rewritten, redundancy deleted
- [ ] 5 Checks passed
- [ ] 6 Handed over
```

**1. Evidence.** One line per observation: which skill, what happened, the proof (quoted error, response field, the user's words). Done when every observation has proof attached.

**2. Bar.** Change the skill when the observation will recur: the API or UI really behaves differently, a documented step fails, the user states a standing preference ("always…", "never…", "from now on…"), or you had to improvise a step the skill should have covered. A one-off ("this time use red") is not a skill change. If a knowledge-base tool is connected (for example the SecondBrain MCP), park weak or unclear signals there as an inbox note tagged `#skill-learning` with skill name and proof, tell the user in one line, and stop. Done when each observation is either "change" or "parked".

**3. Read.** Read the skill's SKILL.md and every file the change touches, in full. If the skill also lives in a git repo (for example a public skills repo), compare both copies and build on the newer one. Done when you can say where the rule you are about to change currently lives.

**4. Rewrite.** Name the principle behind the evidence in one sentence; if you cannot, go back to Step 1. Then, in a working copy:
- Change the existing rule the principle refines. Add a new rule only if none exists, placed where a reader looks for it, with its reason in half a sentence.
- Delete what the change makes redundant, and any copy of the same rule elsewhere in the skill.
- No dates, no changelog, no "Learnings" section, no "previously / fixed / corrected" history. The skill states what is true now.
- Contradiction between a shipped result and an old rule: the shipped result wins; say so in the hand-over.

Done when the diff shows only the rewritten rule and the removed redundancy.

**5. Check.** Run all of these on the working copy:
- The skill validator, if available: `python3 <skill-creator-plus>/scripts/validate_skill.py <folder>`. No new error or warning.
- A secret scan, e.g. `grep -nE '(api[_-]?key|token|passw|secret)[^\n]{0,8}[:=]' -i -r <folder>` and a look at every hit.
- Length: SKILL.md must not have grown by more than the new rule itself. If it did, find what the new rule made redundant.
- For a risky skill (money, sending, deleting, production data) or a large rewrite: let a fresh subagent read the old and new version and list behaviour that changed unintentionally.

If any check fails, return to Step 4. Done when all pass.

**6. Hand over.** Pick the channel:
- **Only SKILL.md changed:** propose it with `propose_skills` (kind `improvement`, target = skill name, the complete new SKILL.md, description unchanged unless the triggers changed). One card per skill; max three per call.
- **Reference files or scripts changed too:** the card carries only SKILL.md. Zip the whole skill folder (`<name>/SKILL.md` at the archive root's first level), write it to the outputs folder and tell the user to upload it in the skill settings, replacing the old one.
- **The skill lives in a git repo:** additionally commit on a new branch and open a pull request, after the repo's own validator and secret scan pass. Never push to the default branch or force-push.

Tell the user in two lines at most: what changed, why (the evidence), and how to apply it. Done when the user has the card, the zip, or the PR link.

## Batch review

Triggered by "skill review", "go through the skill learnings" or similar. Search the knowledge base for `#skill-learning` notes, group them by skill, and run Steps 2 to 6 per skill with all its notes together. Afterwards mark the processed notes as done (or move them out of the inbox) so they are not picked up twice. Done when no unprocessed `#skill-learning` note is left or the user has deferred the rest.

## What this skill does not do

- Ask "is there anything I should do differently?" after every run. It reacts to evidence.
- Restructure a skill that works because a newer style exists. That is an audit (use skill-creator-plus).
- Touch built-in or plugin skills. Those cannot be updated from a card; say so and offer a separately named custom skill instead.
