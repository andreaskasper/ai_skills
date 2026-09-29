#!/usr/bin/env python3
"""
readme_check.py - compare a README against the repository it describes.

Reports facts a README should reflect and claims that no longer hold:
  * project facts: manifests, languages, Dockerfile, CI, license, entry points
  * broken relative links and images (target file does not exist)
  * paths mentioned in code blocks / inline code that do not exist
  * badges that point to a different owner/repo than the git remote
  * obvious placeholders (TODO, lorem ipsum, [your-name], example.com ...)

Usage:
  python3 readme_check.py [repo_dir] [--readme README.md] [--json]
Only reads files; never writes.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

MANIFESTS = {
    "package.json": "Node.js", "composer.json": "PHP (Composer)", "pyproject.toml": "Python",
    "requirements.txt": "Python", "setup.py": "Python", "go.mod": "Go", "Cargo.toml": "Rust",
    "pom.xml": "Java (Maven)", "build.gradle": "Java/Kotlin (Gradle)", "pubspec.yaml": "Dart/Flutter",
    "Gemfile": "Ruby", "*.csproj": ".NET", "Dockerfile": "Docker image",
    "docker-compose.yml": "Docker Compose", "compose.yaml": "Docker Compose",
    "Makefile": "Make targets", "SKILL.md": "Agent skill",
}
PLACEHOLDERS = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum)\b|\[your[- ]name\]|<your[- ]", re.I)
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "__pycache__"}


def git_remote(root):
    try:
        url = subprocess.check_output(["git", "-C", str(root), "remote", "get-url", "origin"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
    return f"{m.group(1)}/{m.group(2)}".lower() if m else None


def facts(root):
    found = {}
    for pattern, label in MANIFESTS.items():
        hits = list(root.glob(pattern)) + list(root.glob(f"*/{pattern}"))
        if hits:
            found[label] = sorted(str(h.relative_to(root)) for h in hits)[:5]
    ci = [str(p.relative_to(root)) for p in (root / ".github" / "workflows").glob("*.y*ml")] \
        if (root / ".github" / "workflows").exists() else []
    lic = [p.name for p in root.iterdir() if p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING"))]
    top = sorted(p.name + ("/" if p.is_dir() else "") for p in root.iterdir()
                 if p.name not in SKIP_DIRS and not p.name.startswith("."))
    pkg = {}
    if (root / "package.json").exists():
        try:
            j = json.loads((root / "package.json").read_text())
            pkg = {"name": j.get("name"), "version": j.get("version"), "scripts": list((j.get("scripts") or {}).keys())}
        except Exception:
            pass
    return {"stack": found, "ci_workflows": ci, "license_files": lic, "top_level": top, "package_json": pkg}


def check(root, readme_path):
    text = readme_path.read_text(encoding="utf-8", errors="replace")
    issues = []
    # relative links and images
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
        target = m.group(1).split("#")[0]
        if not target or re.match(r"^[a-z]+:", target, re.I) or target.startswith("//"):
            continue
        if not (readme_path.parent / target).exists():
            issues.append({"type": "broken_relative_link", "target": target})
    # paths inside inline code / code blocks that look like repo paths
    for m in re.finditer(r"`([^`\n]+)`", text):
        tok = m.group(1).strip()
        if re.fullmatch(r"\.?/?[\w.-]+(/[\w.-]+)+/?", tok) and not tok.startswith(("/usr", "/etc", "/tmp", "/var", "/mnt", "/home", "~")):
            if not (root / tok.lstrip("./")).exists():
                issues.append({"type": "path_not_found", "path": tok})
    # badges pointing elsewhere
    remote = git_remote(root)
    if remote:
        for m in re.finditer(r"(?:shields\.io/github/[\w-]+(?:/[\w-]+)?|github\.com)/([\w.-]+)/([\w.-]+)", text):
            ref = f"{m.group(1)}/{m.group(2)}".lower().removesuffix(".svg")
            if ref.split("/")[0] == remote.split("/")[0] and ref != remote and not ref.startswith(remote):
                issues.append({"type": "badge_or_link_other_repo", "ref": ref, "remote": remote})
    for m in PLACEHOLDERS.finditer(text):
        issues.append({"type": "placeholder", "text": m.group(0)})
    headings = re.findall(r"^#{1,3} .+", text, re.M)
    return {"readme": str(readme_path.relative_to(root)), "length_chars": len(text),
            "headings": headings, "remote": remote, "issues": issues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--readme")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.repo).resolve()
    readme = Path(a.readme).resolve() if a.readme else next(
        (p for p in root.iterdir() if p.name.lower() in ("readme.md", "readme.rst", "readme.txt", "readme")), None)
    out = {"facts": facts(root)}
    out["readme_check"] = check(root, readme) if readme else {"readme": None, "issues": [{"type": "missing_readme"}]}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False)); return
    f = out["facts"]; r = out["readme_check"]
    print(f"Repo: {root.name}  remote: {r.get('remote')}")
    print("Stack:", ", ".join(f"{k} ({', '.join(v)})" for k, v in f["stack"].items()) or "-")
    print("CI:", ", ".join(f["ci_workflows"]) or "-", "| License:", ", ".join(f["license_files"]) or "MISSING")
    print("Top level:", ", ".join(f["top_level"]))
    print(f"README: {r.get('readme')}  ({r.get('length_chars', 0)} chars, {len(r.get('headings', []))} headings)")
    if not r["issues"]:
        print("No mechanical problems found (content still needs a human read).")
    for i in r["issues"]:
        print(" -", i["type"], {k: v for k, v in i.items() if k != "type"})


if __name__ == "__main__":
    main()
