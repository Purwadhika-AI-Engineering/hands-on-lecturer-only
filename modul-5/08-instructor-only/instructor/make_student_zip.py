#!/usr/bin/env python3
"""Build the student handout zip: no instructor/ folder, no answer key, README and Makefile cleaned up.

Usage (from the repo root):  python3 instructor/make_student_zip.py [output.zip]
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "acmebot-lab-student.zip"
SKIP_DIRS = {"instructor", "__pycache__", ".pytest_cache", "node_modules", ".git", ".starter_backup", "venv"}


def keep(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if rel.parts[0] == "runtime" and path.name != ".gitkeep":
        return False
    if rel.parts[:2] == ("promptfoo", "results") and path.name != ".gitignore":
        return False
    return path.is_file() and path.name not in {".env"} and not path.name.endswith(".zip") and not path.suffix == ".pyc"


def patch(rel: str, text: str) -> str:
    if rel == "README.md":
        text = re.sub(r"^instructor/.*\n", "", text, flags=re.M)
        text = text.replace(" Try it before looking at the instructor material.", " Try it yourself first.")
    if rel == "Dockerfile":
        text = text.replace("# see instructor/solution/docker-compose.hardened.yml for the pattern once you have tried yourself.", "# Common levers: a non-root USER, read_only filesystem, dropped capabilities, memory and CPU limits.")
    if rel == "Makefile":
        text = text.replace(" solution restore", "")
        text = re.sub(r"\nsolution:.*?\n\trestore:", "", text, flags=re.S)
        text = re.sub(r"\nsolution:[^\n]*\n\t[^\n]*\n", "\n", text)
        text = re.sub(r"\nrestore:[^\n]*\n\t[^\n]*\n?", "\n", text)
    return text


with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        if keep(p):
            rel = p.relative_to(ROOT).as_posix()
            data = p.read_bytes()
            if rel in ("README.md", "Makefile", "Dockerfile"):
                data = patch(rel, data.decode()).encode()
            z.writestr(f"acmebot-lab/{rel}", data)
print(f"wrote {OUT}")
