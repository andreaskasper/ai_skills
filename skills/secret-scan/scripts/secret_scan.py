#!/usr/bin/env python3
"""
secret_scan.py - find leaked credentials in a working tree AND its git history.

Findings are printed MASKED (first 4 chars + length) so the report itself does
not leak anything. Exit code 1 if something was found (usable in CI).

Usage:
  python3 secret_scan.py [repo_dir]            # working tree + full history
  python3 secret_scan.py . --no-history        # working tree only
  python3 secret_scan.py . --json
"""
import argparse, json, math, re, subprocess, sys
from pathlib import Path

RULES = [
    ("private-key", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    ("github-token", r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    ("aws-access-key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("openai/anthropic-key", r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}\b"),
    ("slack-token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ("stripe-key", r"\b[rs]k_live_[A-Za-z0-9]{20,}\b"),
    ("google-api-key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("jwt", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("url-with-password", r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s:@]{4,}@"),
    ("assignment", r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)\b\s*[:=]\s*[\"']?([^\s\"'<>{}$]{8,})"),
]
COMPILED = [(n, re.compile(p)) for n, p in RULES]
PLACEHOLDER = re.compile(r"(?i)your[_-]|example|changeme|placeholder|xxxx|\*\*\*|<.+>|dummy|test|sample|\.\.\.")
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".mp4", ".woff", ".woff2", ".ttf", ".lock"}


def entropy(s):
    return -sum(s.count(c) / len(s) * math.log2(s.count(c) / len(s)) for c in set(s)) if s else 0


def mask(s):
    return f"{s[:4]}…({len(s)} chars)"


def scan_line(line):
    hits = []
    for name, rx in COMPILED:
        for m in rx.finditer(line):
            val = m.group(1) if m.groups() else m.group(0)
            if PLACEHOLDER.search(val) or PLACEHOLDER.search(line):
                continue
            if name == "assignment" and entropy(val) < 3.0:
                continue
            hits.append((name, val))
    return hits


def scan_tree(root):
    out = []
    try:
        files = subprocess.check_output(["git", "-C", str(root), "ls-files"], text=True).splitlines()
    except Exception:
        files = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    for f in files:
        p = root / f
        if p.suffix.lower() in SKIP_EXT or not p.is_file():
            continue
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            for name, val in scan_line(line):
                out.append({"where": "tree", "file": f, "line": i, "rule": name, "value": mask(val)})
    return out


def scan_history(root):
    out, commit, fname = [], None, None
    proc = subprocess.Popen(["git", "-C", str(root), "log", "--all", "-p", "--no-color", "--pretty=format:@@COMMIT %h %ad", "--date=short"],
                            stdout=subprocess.PIPE, text=True, errors="ignore")
    for line in proc.stdout:
        if line.startswith("@@COMMIT "):
            commit = line.split()[1] + " " + line.split()[2]
        elif line.startswith("+++ b/"):
            fname = line[6:].strip()
        elif line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            if fname and Path(fname).suffix.lower() in SKIP_EXT:
                continue
            for name, val in scan_line(line[1:]):
                out.append({"where": "history", "commit": commit, "file": fname,
                            "change": "added" if line[0] == "+" else "removed", "rule": name, "value": mask(val)})
    seen, uniq = set(), []
    for h in out:
        k = (h["file"], h["rule"], h["value"])
        if k not in seen:
            seen.add(k); uniq.append(h)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--no-history", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.repo).resolve()
    res = scan_tree(root) + ([] if a.no_history else scan_history(root))
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        if not res:
            print("No findings. (Heuristic scan: absence of findings is not proof of absence.)")
        for h in res:
            loc = f"{h['file']}:{h['line']}" if h["where"] == "tree" else f"{h['commit']} {h['file']} ({h['change']})"
            print(f"[{h['where']}] {h['rule']:22} {loc}  {h['value']}")
    sys.exit(1 if res else 0)


if __name__ == "__main__":
    main()
