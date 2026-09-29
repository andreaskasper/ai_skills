---
name: changelog-writer
description: Write or update a CHANGELOG.md in "Keep a Changelog" format from git history, tags and merged pull requests, and suggest the next semantic version. Use whenever someone wants a changelog, release notes for a version, "what changed since v1.2", a version bump, or to tidy an existing CHANGELOG. Triggers include "write a changelog", "update CHANGELOG", "what changed since the last release", "prepare release 2.0", "Changelog schreiben", "was hat sich seit Version X geändert", "Release vorbereiten". Reads git only; never tags or pushes without confirmation.
---

# Changelog Writer

Produce a changelog people actually read: grouped, written for users, one line per change, newest version on top. Format: [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/).

## 1. Collect

```bash
python3 scripts/changelog.py                              # since latest tag, section "Unreleased"
python3 scripts/changelog.py --from v1.2.0 --version 1.3.0
python3 scripts/changelog.py --json                       # raw grouping for your own editing
```

The script groups by Conventional Commit type (`feat` → Added, `fix` → Fixed, `feat!`/`BREAKING` → flagged), falls back to keywords for free-form messages and skips `chore/ci/docs/test/merge`. Its output is a **draft**.

Without a local checkout, read tags, commits and merged PRs via a GitHub connector or `gh pr list --state merged --search "merged:>YYYY-MM-DD"`. PR titles and descriptions are usually better source material than commit subjects.

## 2. Edit for humans

- Write from the user's perspective: "Export to CSV" not "add csv_export() helper".
- Merge related commits into one entry; drop pure internals (refactors with no visible effect, typo fixes in code comments).
- Keep issue/PR references: `(#42)`.
- Put **breaking changes** first within their section and say what users must do.
- Sections in this order, only when non-empty: Added, Changed, Deprecated, Removed, Fixed, Security.
- Never invent changes that aren't in the history.

## 3. Version and structure

Suggest the next version: breaking change → major, new feature → minor, only fixes → patch (pre-1.0: breaking → minor). Say why.

```markdown
# Changelog

All notable changes to this project are documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

## [1.3.0] - 2026-09-29
### Added
- CSV export for results (#42)
### Fixed
- Login loop on Safari (#51)

[Unreleased]: https://github.com/OWNER/REPO/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/OWNER/REPO/compare/v1.2.0...v1.3.0
```

Update an existing CHANGELOG in place: keep old entries untouched, move "Unreleased" items into the new version, add the compare links at the bottom. Keep the file's language.

## 4. Deliver

Show the new section (or diff), the suggested version with reasoning, and ask before committing, tagging or creating a GitHub release. For GitHub release notes, the same content works; the `## [x.y.z]` heading is dropped.
