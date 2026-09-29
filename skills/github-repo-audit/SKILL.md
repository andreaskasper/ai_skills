---
name: github-repo-audit
description: Audit all GitHub repositories of a user or organisation and sort them into "archive candidates", "needs description/README/license", "worth working on" and "fine". Use whenever someone asks which repos they haven't touched in a while, which ones are dead or empty, which need a README, what to clean up on their GitHub, or what to work on next. Triggers include "audit my repos", "GitHub cleanup", "which repos are stale", "what should I work on", "welche Repos habe ich lange nicht angefasst", "GitHub aufräumen", "welche Repos brauchen ein README", "woran können wir arbeiten". Read-only; never archives or deletes anything without explicit confirmation.
---

# GitHub Repo Audit

Answer "which of my repositories are dead, which need documentation, and which deserve work?" in one pass, then propose concrete next steps.

## 1. Collect the repo list

Use whatever access is available, in this order:

1. **A GitHub MCP connector / tool** (e.g. `search_repositories` with `user:<login> fork:true sort:updated`, or a list-repos tool). Call a "get me" tool first to learn the login.
2. **`scripts/audit.py`** when bash and network are available:
   ```bash
   python3 scripts/audit.py <owner>                  # markdown report
   python3 scripts/audit.py <owner> --check-readme   # also detects missing READMEs
   python3 scripts/audit.py <owner> --json           # for further processing
   ```
   Without `GITHUB_TOKEN` only public repos are listed and the limit is 60 requests/hour, which shared sandboxes often exhaust (HTTP 403). With a token for the owner's own account, private repos are included.
3. **`gh` CLI**: `gh repo list <owner> --limit 500 --json name,description,pushedAt,isArchived,isFork,isPrivate,diskUsage,stargazerCount,licenseInfo`.

Search APIs return at most 100 items per page. If `total_count` is larger than what you received, fetch the next page or say which slice you looked at.

## 2. Read the signals correctly

These are the traps that make audits wrong:

- **`pushed_at` is code activity; `updated_at` is not.** `updated_at` also changes when someone stars the repo or edits the description. Prefer `pushed_at`. If only `updated_at` is available (some search tools), say so in the answer.
- **`size == 0`, or `created_at` ≈ `updated_at` to the second** → the repo was created and never filled. Safe archive/delete candidate.
- **`open_issues_count` includes pull requests.** Say "issues/PRs" unless you checked.
- **Forks** with no pushes after creation carry no own work. List them separately.
- **Archived repos** are already handled; skip them.
- **Missing description** is visible from the listing. **Missing README** needs one request per repo (`GET /repos/{owner}/{repo}/readme` → 404). Don't claim a README is missing or outdated unless you actually checked or read it; otherwise say the judgement is based on metadata.
- **Stars on a repo without description or license** are a signal: strangers find it and can't use it. Rank those first in the docs group.
- **Dead external services** (an API wrapper for a service that no longer exists) are archive candidates even if the code is fine. Mention them only when you actually know the service is gone.

## 3. Classify

| Group | Rule of thumb |
|---|---|
| Archive candidates | no push for ≥ 3 years and no open issues; empty repos; forks without own commits; wrappers for defunct services |
| Needs docs | alive or public, but missing description, README or (for public repos) a license |
| Worth working on | open issues/PRs, stars, or recent pushes on a repo that matters to the owner |
| Fine | nothing to do; don't list individually |

Use the owner's context if you have it (which projects are their main products). A repo belonging to an active product is never an archive candidate just because it's old.

## 4. Present the result

Keep it scannable; the user usually wants a decision list, not a table dump.

- Group by the categories above, most actionable first.
- Per repo: name, one short reason (e.g. "last push 2016", "17 open issues", "2 stars, no description").
- Collapse long tails ("seven client-project repos from 2017–2021") instead of listing each.
- State the data basis in one sentence (e.g. "based on metadata; READMEs not opened").
- End with **one** concrete proposal for what to do next (e.g. triage the issues of the top repo, or draft READMEs for the three most visible repos). The `readme-refresh` skill handles README work.

## 5. Acting on the audit

Everything above is read-only. Before any write action, ask:

- **Archiving** is reversible but hides the repo from active lists: confirm the exact list first.
- **Deleting** is irreversible: never do it in bulk; confirm repo by repo, and suggest archiving instead.
- **Changing visibility** (private ↔ public) can expose secrets in history: warn and confirm.
- Editing descriptions/topics is low risk but still confirm the wording once for the whole batch.
