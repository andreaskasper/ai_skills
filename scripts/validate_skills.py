#!/usr/bin/env python3
"""
Validate every skill under skills/:
  * SKILL.md exists and starts with YAML frontmatter
  * `name` matches the folder, lowercase letters/digits/hyphens, <= 64 chars
  * `description` present, <= 1024 chars
  * README.md lists the skill in the "Available Skills" table
  * no obvious secrets (hard-coded tokens, passwords, private keys)
Exit code 1 on any error. Standard library only.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SECRET_RES = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "GitHub token"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "API key (sk-...)"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key)\s*[=:]\s*[\"']?[A-Za-z0-9/+_-]{20,}"), "hard-coded credential"),
    (re.compile(r"\b[a-z0-9]{30}\b"), "30-char key (Pushover-style)"),
]
TEXT_EXT = {".md", ".py", ".sh", ".js", ".ts", ".json", ".yml", ".yaml", ".txt", ".toml"}


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data, key = {}, None
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            data[key] = kv.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
    for k, v in data.items():
        v = re.sub(r"^[>|]-?\s*", "", v)
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        data[k] = v
    return data


def main():
    errors, readme = [], (ROOT / "README.md").read_text(encoding="utf-8")
    dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for d in dirs:
        md = d / "SKILL.md"
        if not md.exists():
            errors.append(f"{d.name}: SKILL.md missing"); continue
        fm = frontmatter(md.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{d.name}: no YAML frontmatter"); continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != d.name:
            errors.append(f"{d.name}: name '{name}' does not match folder")
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{d.name}: invalid name '{name}'")
        if not desc:
            errors.append(f"{d.name}: description missing")
        elif len(desc) > 1024:
            errors.append(f"{d.name}: description has {len(desc)} chars (max 1024)")
        if f"`{d.name}`" not in readme:
            errors.append(f"{d.name}: not listed in README.md")
        for f in d.rglob("*"):
            if f.is_file() and f.suffix in TEXT_EXT:
                for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    for rx, label in SECRET_RES:
                        if rx.search(line) and "YOUR_" not in line and "example" not in line.lower():
                            errors.append(f"{f.relative_to(ROOT)}:{i}: possible {label}")
    for e in errors:
        print("ERROR", e)
    print(f"{len(dirs)} skills checked, {len(errors)} problem(s).")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
