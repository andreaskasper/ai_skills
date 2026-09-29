# Working on ai_skills

Rules for anyone (human or agent) adding or changing skills in this repo.

## Hard rules

- **No secrets, ever.** No API keys, tokens, passwords, bot passwords, private keys, cookies or personal data (names, addresses, phone numbers of real people) in any file. Skills read credentials from environment variables and document them in a "Setup" section with placeholders like `YOUR_API_KEY`.
- Run `python3 scripts/validate_skills.py` before every commit. It checks frontmatter, the README listing and scans for secrets. Also run `python3 skills/secret-scan/scripts/secret_scan.py .` (with history, inside a git checkout) before pushing.
- Never force-push or rewrite history without the owner's explicit OK.

## Skill conventions

- One folder per skill: `skills/<name>/SKILL.md`, optional `scripts/`, `references/`, `assets/`. Folder name = `name:` in the frontmatter, lowercase with hyphens.
- `description`: what the skill does **and** when to use it, with trigger phrases in English and German. Max 1024 characters. If it contains `: ` quote the whole value.
- Language: English, except skills that only make sense for German (German law, German writing style), which are written in German (e.g. `vermenschlichen`, `rechnung-pruefen`).
- Scripts: Python 3 standard library only unless unavoidable; `--json` output option; clear error messages; no network calls at import time; send a descriptive `User-Agent`.
- Test every script against the real API or a fixture before committing, and note verified behaviour with a month/year ("verified 09/2026").
- Prefer public, keyless APIs. If a key is needed, say so in the README "Needs" column.
- Add a row to the *Available Skills* table in `README.md`.
- Destructive actions (delete, force-push, send messages, spend money) must be gated behind an explicit confirmation step in the skill text.

## Backlog

Open skill ideas with short specs: [`docs/SKILL_BACKLOG.md`](docs/SKILL_BACKLOG.md). Move an item to "Done" when its skill is merged.
