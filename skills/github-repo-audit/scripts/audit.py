#!/usr/bin/env python3
"""
audit.py - triage every repository of a GitHub user or organisation.

Classifies each repo into one of:
  archive   - no pushes for a long time, or empty, or a fork without own work
  docs      - alive but missing a description, README or license
  work      - has open issues / PRs or recent activity worth continuing
  ok        - nothing to do

Uses the public REST API. Set GITHUB_TOKEN to include private repos and to
raise the rate limit from 60 to 5000 requests per hour.

Usage:
  python3 audit.py <owner>                       # markdown report
  python3 audit.py <owner> --json                # machine-readable
  python3 audit.py <owner> --stale-years 3       # threshold for "archive"
  python3 audit.py <owner> --check-readme        # 1 extra request per repo
  python3 audit.py <owner> --skip-forks
"""
import argparse, json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

API = "https://api.github.com"


def gh(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-repo-audit-skill",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def list_repos(owner):
    # With a token for the owner's own account, /user/repos also returns private repos.
    token = os.environ.get("GITHUB_TOKEN")
    me = None
    if token:
        try:
            me = gh("/user")["login"]
        except urllib.error.HTTPError:
            me = None
    if me and me.lower() == owner.lower():
        base = "/user/repos?affiliation=owner&per_page=100"
    else:
        kind = gh(f"/users/{owner}").get("type", "User")
        base = (f"/orgs/{owner}/repos?type=all&per_page=100" if kind == "Organization"
                else f"/users/{owner}/repos?type=owner&per_page=100")
    repos, page = [], 1
    while True:
        batch = gh(f"{base}&page={page}")
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def has_readme(full_name):
    try:
        gh(f"/repos/{full_name}/readme")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def years_since(ts):
    if not ts:
        return None
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days / 365.25


def classify(r, stale_years, readme):
    reasons = []
    pushed = years_since(r.get("pushed_at"))
    empty = r.get("size", 0) == 0
    if r.get("archived"):
        return "ok", ["already archived"]
    if empty:
        return "archive", ["empty repository (size 0)"]
    if r.get("fork") and pushed is not None and pushed > 1:
        return "archive", [f"fork, last push {pushed:.1f} years ago"]
    if pushed is not None and pushed > stale_years and not r.get("open_issues_count"):
        return "archive", [f"no push for {pushed:.1f} years"]
    if not r.get("description"):
        reasons.append("no description")
    if readme is False:
        reasons.append("no README")
    if not r.get("license") and not r.get("private"):
        reasons.append("public but no license")
    if reasons:
        return "docs", reasons
    if r.get("open_issues_count"):
        return "work", [f"{r['open_issues_count']} open issues/PRs"]
    return "ok", []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("owner")
    ap.add_argument("--stale-years", type=float, default=3)
    ap.add_argument("--check-readme", action="store_true")
    ap.add_argument("--skip-forks", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        repos = list_repos(a.owner)
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API error {e.code}: {e.reason}. "
                 "Rate-limited? Set GITHUB_TOKEN.")

    rows = []
    for r in repos:
        if a.skip_forks and r.get("fork"):
            continue
        readme = has_readme(r["full_name"]) if a.check_readme else None
        cat, why = classify(r, a.stale_years, readme)
        rows.append({
            "name": r["name"], "category": cat, "reasons": why,
            "private": r.get("private"), "fork": r.get("fork"),
            "stars": r.get("stargazers_count", 0),
            "open_issues": r.get("open_issues_count", 0),
            "pushed_at": (r.get("pushed_at") or "")[:10],
            "description": r.get("description") or "",
            "url": r["html_url"],
        })

    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    order = ["work", "docs", "archive", "ok"]
    titles = {"work": "Worth working on", "docs": "Needs description / README / license",
              "archive": "Archive candidates", "ok": "Nothing to do"}
    print(f"# Repository audit for {a.owner} ({len(rows)} repos)\n")
    for cat in order:
        group = sorted((x for x in rows if x["category"] == cat),
                       key=lambda x: (-x["open_issues"], -x["stars"], x["pushed_at"]))
        if not group:
            continue
        print(f"## {titles[cat]} ({len(group)})\n")
        print("| Repo | Last push | Stars | Issues | Why |\n|---|---|---|---|---|")
        for x in group:
            vis = " (private)" if x["private"] else ""
            print(f"| [{x['name']}]({x['url']}){vis} | {x['pushed_at']} | {x['stars']} "
                  f"| {x['open_issues']} | {'; '.join(x['reasons'])} |")
        print()


if __name__ == "__main__":
    main()
