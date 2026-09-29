---
name: secret-scan
description: Find leaked credentials (API keys, tokens, passwords, private keys, connection strings) in a repository's files AND its full git history, then guide rotation and clean-up. Use before making a repo public, after an accidental commit of a .env file, when auditing old projects, or whenever someone asks whether secrets are in their code. Triggers include "scan for secrets", "did I commit my API key", "check repo for passwords", "before I make this public", "Secrets im Repo", "hab ich Zugangsdaten eingecheckt", "Repo auf Passwörter prüfen". Reports values masked; never prints, stores or transmits found secrets.
---

# Secret Scan

Goal: know whether credentials ever entered a repository, and if so, make them useless. **Deleting a secret from the latest commit does not remove it**: it stays in the history, in forks, in clones and possibly in caches. The only real fix is rotation.

## 1. Scan

```bash
python3 scripts/secret_scan.py <repo_dir>                # working tree + entire history (all branches)
python3 scripts/secret_scan.py <repo_dir> --no-history   # quick check of current files
python3 scripts/secret_scan.py <repo_dir> --json
```

Covers private keys, GitHub/AWS/Slack/Stripe/Google/OpenAI/Anthropic-style tokens, JWTs, URLs with embedded passwords, and `password=`/`api_key:` assignments with high-entropy values. Output is masked (`abcd…(40 chars)`). Exit code 1 on findings, so it works in CI.

If available, also run a dedicated scanner for broader coverage: `gitleaks detect --source <dir>` or `trufflehog git file://<dir>`. For repos only reachable via a GitHub connector, check GitHub's secret-scanning alerts or clone read-only first.

Also look at what regexes miss: committed `.env`, `config.php`, `wp-config.php`, `*.pem`, `id_rsa`, `credentials.json`, database dumps, and secrets in `SKILL.md`/docs written as plain prose.

## 2. Triage

For every finding decide: real secret, test/placeholder value, or public identifier (e.g. publishable keys, Pushover *user* keys are less critical than app tokens but still personal). When unsure, treat it as real.

**Never** print the full value in chat, paste it into another tool, or "verify" it by calling the service with it.

## 3. Respond (in this order)

1. **Rotate/revoke** each real secret at its provider (new key, delete old). This is the actual fix. Do it first, especially if the repo is or was public.
2. **Remove from the code**: move values to environment variables or a secret manager; add `.env.example` with placeholders; add the files to `.gitignore`.
3. **Optionally rewrite history** (`git filter-repo --replace-text`, or BFG) and force-push. Warn: this rewrites all commit hashes, breaks open PRs and existing clones, and does not reach forks. Confirm with the user before any force-push.
4. **Prevent recurrence**: pre-commit hook or CI job running the scanner; GitHub push protection if available.

## 4. Report

List findings as a table (location, type, masked value, verdict), then the concrete rotation checklist per provider. Keep it factual; a clean result is "no findings with these rules", never "the repo is guaranteed clean".
