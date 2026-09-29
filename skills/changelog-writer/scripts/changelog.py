#!/usr/bin/env python3
"""
changelog.py - draft a "Keep a Changelog" section from git history.

Groups commits between two refs by Conventional Commit type (feat, fix, ...),
falls back to keyword heuristics for free-form messages, and prints Markdown.
The result is a DRAFT: rewrite entries for humans before committing.

Usage:
  python3 changelog.py                         # since the latest tag
  python3 changelog.py --from v1.2.0 --to HEAD --version 1.3.0
  python3 changelog.py --json
"""
import argparse, datetime, json, re, subprocess, sys

SECTIONS = [("Added", {"feat", "feature", "add"}), ("Changed", {"refactor", "perf", "change", "style"}),
            ("Deprecated", {"deprecate"}), ("Removed", {"remove", "revert"}),
            ("Fixed", {"fix", "bugfix", "hotfix"}), ("Security", {"security", "sec"})]
SKIP = {"chore", "ci", "build", "test", "tests", "docs", "doc", "wip", "merge"}
CC = re.compile(r"^(\w+)(\([^)]*\))?(!)?:\s*(.+)$")
KEYWORDS = [("Fixed", r"\b(fix|fixed|bug|repair)"), ("Added", r"\b(add|added|new|introduce|implement)"),
            ("Removed", r"\b(remove|removed|delete|drop)"), ("Security", r"\b(security|cve|xss|csrf|injection)"),
            ("Changed", r"\b(update|change|improve|refactor|rename|bump)")]


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def latest_tag():
    try:
        return git("describe", "--tags", "--abbrev=0")
    except subprocess.CalledProcessError:
        return None


def classify(subject):
    m = CC.match(subject)
    if m:
        typ, _, bang, text = m.groups()
        typ = typ.lower()
        if bang or "BREAKING" in subject:
            return "Changed", f"**BREAKING:** {text}"
        if typ in SKIP:
            return None, text
        for name, types in SECTIONS:
            if typ in types:
                return name, text
        return "Changed", text
    if subject.lower().startswith(("merge ", "wip")):
        return None, subject
    for name, rx in KEYWORDS:
        if re.search(rx, subject, re.I):
            return name, subject
    return "Changed", subject


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--version", default="Unreleased")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    frm = a.frm or latest_tag()
    rng = f"{frm}..{a.to}" if frm else a.to
    log = git("log", rng, "--no-merges", "--pretty=format:%h%x09%s")
    groups = {name: [] for name, _ in SECTIONS}
    skipped = []
    for line in filter(None, log.splitlines()):
        sha, subject = line.split("\t", 1)
        sec, text = classify(subject)
        (groups[sec] if sec else skipped).append({"sha": sha, "text": text[:1].upper() + text[1:]})
    if a.json:
        print(json.dumps({"range": rng, "sections": groups, "skipped": skipped}, indent=2, ensure_ascii=False)); return
    date = "" if a.version == "Unreleased" else f" - {datetime.date.today()}"
    print(f"## [{a.version}]{date}\n")
    for name, _ in SECTIONS:
        if groups[name]:
            print(f"### {name}\n")
            for e in groups[name]:
                print(f"- {e['text']} ({e['sha']})")
            print()
    print(f"<!-- range {rng}: {sum(map(len, groups.values()))} entries, {len(skipped)} skipped (chore/ci/docs/merge) -->", file=sys.stderr)


if __name__ == "__main__":
    main()
