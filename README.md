# 🧠 AI Skills

> A collection of **skills for AIs like Claude** — reusable, self-contained capabilities you can drop into Claude Code, Cowork, or any agent that supports the open Skill format. Each skill is just a folder with a `SKILL.md` and optional scripts, so they're easy to read, share, and load on demand straight from GitHub.

### Stats

![Last Commit](https://img.shields.io/github/last-commit/andreaskasper/ai_skills.svg)
![Commit Activity](https://img.shields.io/github/commit-activity/m/andreaskasper/ai_skills.svg)
![GitHub Issues](https://img.shields.io/github/issues/andreaskasper/ai_skills.svg)
![Repo Stars](https://img.shields.io/github/stars/andreaskasper/ai_skills.svg)
![License](https://img.shields.io/github/license/andreaskasper/ai_skills.svg)

---

### What is a "skill"?

A skill is a small, model-agnostic package that teaches an AI how to do one thing well. It follows Anthropic's open [Agent Skills](https://www.anthropic.com/news/skills) format:

```
skills/
└── <skill-name>/
    ├── SKILL.md          # required — YAML frontmatter (name, description) + instructions
    ├── scripts/          # optional — executable helpers for deterministic steps
    ├── references/       # optional — docs loaded into context only when needed
    └── assets/           # optional — templates, icons, fonts used in output
```

The AI reads the `name` + `description` at all times, pulls the full `SKILL.md` into context only when the skill is relevant, and runs bundled scripts without loading them — so skills stay cheap until they're actually used.

---

### Features

- [x] 📦 **Self-contained skills** — every skill lives in its own folder under [`skills/`](skills/)
- [x] 🤖 **Model-agnostic** — works with Claude Code, Cowork, the Claude Agent SDK, and any agent that supports the Skill format
- [x] ⚡ **Load on demand from GitHub** — grab a single skill over plain HTTPS, no `git clone` needed (see the [`github-skill-loader`](skills/github-skill-loader/) skill)
- [x] 🛠️ **Built with skill-creator** — authored and iterated using Anthropic's official skill-creator workflow
- [x] 🔓 **Public & MIT-friendly** — read, fork, and reuse freely

---

### Quick Start — load a skill into Claude

Because this repo is public, you can install any skill directly from GitHub without cloning. Pick a skill name and run:

```bash
OWNER=andreaskasper REPO=ai_skills BRANCH=main SKILL=github-skill-loader
DEST="$HOME/.claude/skills/$SKILL"
mkdir -p "$DEST"

curl -s "https://api.github.com/repos/$OWNER/$REPO/git/trees/$BRANCH?recursive=1" \
  | jq -r --arg p "skills/$SKILL/" \
      '.tree[] | select(.type=="blob" and (.path|startswith($p))) | .path' \
  | while read -r path; do
      rel="${path#skills/$SKILL/}"
      mkdir -p "$DEST/$(dirname "$rel")"
      curl -s "https://raw.githubusercontent.com/$OWNER/$REPO/$BRANCH/$path" -o "$DEST/$rel"
    done
```

Or just tell Claude: *"Load the `<skill-name>` skill from my `ai_skills` repo on GitHub."* — the [`github-skill-loader`](skills/github-skill-loader/) skill teaches it exactly how to browse this repo and pull a single skill into `~/.claude/skills/`.

**List what's available:**

```bash
curl -s https://api.github.com/repos/andreaskasper/ai_skills/contents/skills | jq -r '.[].name'
```

---

### Available Skills

| Skill | Description |
|---|---|
| [`github-skill-loader`](skills/github-skill-loader/) | Browse this repo and load/install a single skill from GitHub via raw content + the Contents/Trees API — no clone required. |

> More skills are added over time. Run the listing command above for the live list.

---

### Adding a new skill

New skills are authored with Anthropic's **skill-creator** (draft → test → iterate). The convention for this repo:

1. Create a new folder under `skills/<skill-name>/`.
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and clear, imperative instructions.
3. Make the `description` specific about **what** the skill does **and when** to trigger it — that field is the primary triggering mechanism.
4. Bundle any helpers under `scripts/`, `references/`, or `assets/`.
5. Add a row to the *Available Skills* table above.

---

### Installation locations

| Scope | Path |
|---|---|
| User-level (available everywhere) | `~/.claude/skills/<skill-name>/` |
| Project-level (one project only) | `<project>/.claude/skills/<skill-name>/` |

---

### Roadmap

- [x] Repository structure (`skills/`)
- [x] `github-skill-loader` — load skills straight from GitHub
- [ ] More general-purpose skills (research, formatting, automation)
- [ ] Optional `install.sh` one-liner installer
- [ ] CI check that validates every `SKILL.md` frontmatter
- [ ] A small index/manifest file for faster skill discovery

---

### Links

- [📖 Anthropic — Agent Skills](https://www.anthropic.com/news/skills)
- [🧰 Claude Code](https://docs.claude.com/en/docs/claude-code)

---

### Support the project 🛠️

[![donate via Patreon](https://img.shields.io/badge/Donate-Patreon-green.svg)](https://www.patreon.com/AndreasKasper)
[![donate via PayPal](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/AndreasKasper)
[![donate via Ko-fi](https://img.shields.io/badge/Donate-Ko--fi-green.svg)](https://ko-fi.com/andreaskasper)
[![Sponsors](https://img.shields.io/github/sponsors/andreaskasper)](https://github.com/sponsors/andreaskasper)
