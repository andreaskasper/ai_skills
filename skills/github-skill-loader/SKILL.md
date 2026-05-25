---
name: github-skill-loader
description: Load and install AI/Claude skills directly from the public GitHub repo `andreaskasper/ai_skills` (or any GitHub-hosted skills repo) using raw file content and the GitHub Contents/Trees API — no `git clone` required. Use this skill whenever someone wants to add, fetch, download, install, update, or "pull" a skill from GitHub, says things like "load the X skill from my repo", "get a skill from github", "install a skill", "give Claude a new skill quickly", or asks how to browse/list which skills are available in the ai_skills repository. Also use it when you (the AI) realize a needed capability already exists as a skill in this repo and you want to grab it on the fly.
---

# GitHub Skill Loader

This skill explains how to pull a single skill out of a public GitHub skills repository and drop it into the local skills folder so it becomes immediately usable — without cloning the whole repo.

The reference repository is **`andreaskasper/ai_skills`**, but the exact same steps work for any public GitHub repo that stores skills under a `skills/` directory.

## Why this works

Every skill in the repo lives in its own folder:

```
skills/
└── <skill-name>/
    ├── SKILL.md          (required)
    ├── scripts/          (optional)
    ├── references/       (optional)
    └── assets/           (optional)
```

Because the repo is **public**, every one of those files is reachable over plain HTTPS with no authentication. That means you can list what's available, read a skill before committing to it, and copy just the one folder you need. A full `git clone` is overkill when you only want one skill.

Two endpoints do all the work:

- **Raw file content:** `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`
- **GitHub API (listing/trees):** `https://api.github.com/repos/<owner>/<repo>/...`

For `andreaskasper/ai_skills` the branch is `main`.

## Step 1 — See which skills exist

List the folders under `skills/` via the Contents API:

```bash
curl -s https://api.github.com/repos/andreaskasper/ai_skills/contents/skills \
  | jq -r '.[] | select(.type=="dir") | .name'
```

If you don't have a shell, fetch that same URL with WebFetch — it returns JSON and you can read the directory names from the `name` fields.

## Step 2 — Inspect a skill before installing it

Read its `SKILL.md` to confirm it does what you want and to see its description/triggers:

```bash
curl -s https://raw.githubusercontent.com/andreaskasper/ai_skills/main/skills/<skill-name>/SKILL.md
```

This is cheap and avoids installing the wrong thing. Always read the `SKILL.md` first.

## Step 3 — Download the whole skill (including resources)

A skill is often more than just `SKILL.md` — it may bundle `scripts/`, `references/`, or `assets/`. Grabbing only `SKILL.md` would leave those behind. List every file in the skill folder recursively with the Git Trees API, then download each one while preserving its relative path.

```bash
OWNER=andreaskasper
REPO=ai_skills
BRANCH=main
SKILL=<skill-name>

# Install location: user-level for Claude Code / Cowork.
# Use ./.claude/skills/$SKILL instead for a project-local install.
DEST="$HOME/.claude/skills/$SKILL"
mkdir -p "$DEST"

curl -s "https://api.github.com/repos/$OWNER/$REPO/git/trees/$BRANCH?recursive=1" \
  | jq -r --arg p "skills/$SKILL/" \
      '.tree[] | select(.type=="blob" and (.path | startswith($p))) | .path' \
  | while read -r path; do
      rel="${path#skills/$SKILL/}"
      mkdir -p "$DEST/$(dirname "$rel")"
      curl -s "https://raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/$path" -o "$DEST/$rel"
      echo "fetched $rel"
    done

# Make any bundled scripts executable
find "$DEST" -type f \( -name '*.sh' -o -name '*.py' \) -exec chmod +x {} \;
```

After this runs, the skill sits at `~/.claude/skills/<skill-name>/` with its full structure intact.

## Step 4 — Where to put it (so the AI can actually use it)

- **User-level (available everywhere):** `~/.claude/skills/<skill-name>/`
- **Project-level (just this project):** `<project>/.claude/skills/<skill-name>/`

The skill becomes available the next time skills are loaded (typically a new session). The folder name and the `name:` field in the frontmatter should match.

## No shell available? (WebFetch / file-tools only)

If you can only fetch URLs and write files (no `curl`/`jq`):

1. WebFetch `https://api.github.com/repos/andreaskasper/ai_skills/contents/skills/<skill-name>?ref=main` to get the JSON list of files in the folder (each entry has a `path` and a `download_url`).
2. For nested folders (`scripts/`, etc.), fetch the same Contents API URL pointing at the subfolder to enumerate its files.
3. WebFetch each `download_url` to get the raw content, and Write it to the matching path under the local skills folder.

The Trees-API one-liner in Step 3 is the fast path; this is the fallback when you're in a restricted environment.

## Quick reference

| Need | URL |
|---|---|
| List all skills | `https://api.github.com/repos/andreaskasper/ai_skills/contents/skills` |
| Read one SKILL.md | `https://raw.githubusercontent.com/andreaskasper/ai_skills/main/skills/<name>/SKILL.md` |
| List every file in a skill | `https://api.github.com/repos/andreaskasper/ai_skills/git/trees/main?recursive=1` (filter paths starting with `skills/<name>/`) |
| Raw file | `https://raw.githubusercontent.com/andreaskasper/ai_skills/main/<path>` |

## Notes

- **Public repo → no token needed.** For a *private* repo, add `-H "Authorization: Bearer $GITHUB_TOKEN"` to the API calls and fetch raw content via the Contents API with the header `Accept: application/vnd.github.raw`.
- **Rate limits:** unauthenticated GitHub API calls are limited (~60/hour per IP). The few calls here stay well under that; add a token if you hit the limit.
- **Updating an existing skill:** just re-run Step 3 — it overwrites the local files with the latest version.
- **Pin a version:** replace `main` with a tag or commit SHA in any URL to fetch a specific revision instead of the latest.
