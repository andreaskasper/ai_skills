---
name: readme-refresh
description: Check a repository's README against what the code actually contains and rewrite or create it so it is accurate, complete and useful: what the project is, how to install and run it, configuration, status and license. Use whenever someone wants to update, improve, fix, write or modernise a README, asks whether a README is outdated, or wants documentation for a repo that has none. Triggers include "update the README", "README refresh", "write a README", "is my README still correct", "README aktualisieren", "README überarbeiten", "schreib mir ein README", "Readme für das Repo". Works on a local checkout, a GitHub connector, or pasted text. Never invents features.
---

# README Refresh

A good README answers five questions in the first screen: **What is this? Who is it for? How do I get it running? What's the status? Under what license?** Everything else is secondary. This skill checks the existing README against the repository, then rewrites it without inventing anything.

## 1. Gather facts before writing a single line

The repository is the source of truth; the old README is only a hint.

**Local checkout (bash available):**
```bash
python3 scripts/readme_check.py <repo_dir>          # human-readable report
python3 scripts/readme_check.py <repo_dir> --json   # for further processing
```
It lists the stack (manifests like `package.json`, `composer.json`, `pyproject.toml`, `Dockerfile`, `go.mod` …), CI workflows, license files and top-level layout, and flags broken relative links, paths mentioned in code that don't exist, badges pointing at another repo, and placeholders like `TODO`.

**Via a GitHub connector:** read the root directory listing, the README, the main manifest, `Dockerfile`/`docker-compose.yml`, `.github/workflows/`, `LICENSE`, and an `.env.example` if present. Look at the latest commits (messages, dates) to judge the project status.

Then read the actual entry points (main script, `index.php`, `cmd/`, `src/main.*`) far enough to state correctly what the project does. For install/run commands, prefer what the manifest scripts, `Makefile` or `Dockerfile` actually define.

## 2. Diagnose the old README

List the concrete problems, each tied to evidence:

- Claims that are no longer true (commands, file paths, env vars, ports, versions, features that were removed).
- Missing essentials from the five questions above.
- Broken links/images and badges pointing to the wrong repo (see script output).
- Things that belong elsewhere (changelogs → `CHANGELOG.md`, long API docs → `docs/`).
- Secrets or internal hostnames that should not be in a public README; flag these prominently.

If the README is already accurate, say so and only propose small improvements. Don't rewrite for the sake of it.

## 3. Rewrite

**Preserve the author's voice and conventions.** If the owner's other repos share a structure (same badge row, "Features" checklist, "Support" section), reuse it. Keep the language the README is written in unless asked otherwise.

Default structure; drop sections that would be empty instead of padding them:

```markdown
# Project name

One or two sentences: what it does and for whom.

<!-- optional: badges that actually resolve for THIS repo -->

## Features            (only real, implemented ones; checklists for roadmap items are fine)
## Quick start         (the shortest path from zero to running, copy-pasteable)
## Configuration       (env vars / config file keys with defaults; table if more than 3)
## Usage               (1–3 realistic examples)
## Development         (tests, build, lint; only if contributors are expected)
## Status / Roadmap    (maintained? experimental? archived? be honest)
## License
```

Rules:
- **Never invent** features, commands, env vars, benchmarks, compatibility claims or contributors. If something is unclear, leave it out or mark it `<!-- TODO: confirm -->` and list it in your reply.
- Every command must be runnable as written from the repo root. Prefer commands defined by the project (`npm run dev`, `make up`, `docker compose up`).
- Use placeholders for secrets (`YOUR_API_KEY`), never real values.
- Badges only if they resolve for this exact `owner/repo`; a broken badge is worse than none.
- If no LICENSE file exists, don't claim one. Point out the gap and ask which license to add.
- Link to further docs rather than duplicating them.

## 4. Deliver

1. Short summary of what was wrong (bullets, with evidence).
2. The new README (full text), or a diff for small changes.
3. Open questions (unclear facts, missing license decision).

Only commit/push when the user asked for it. When committing, use a clear message such as `docs: refresh README (install steps, config table, license)` and fetch the current file SHA first so you don't overwrite concurrent edits.

## Batch mode

For several repos (e.g. after `github-repo-audit`), start with the ones where a README matters most: public repos with stars, repos linked from websites, active products. For small or throwaway repos, a one-line description plus a three-line README is enough; say so instead of producing boilerplate.
