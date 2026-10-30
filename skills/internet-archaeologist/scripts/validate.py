"""Validate package structure and run the repeatable offline test suite."""
import re
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    content = (root / "SKILL.md").read_text(encoding="utf-8")
    if not content.startswith("---\n"): raise ValueError("Missing YAML frontmatter")
    front = content.split("---", 2)[1]
    name = re.search(r"^name: (.+)$", front, re.M)
    description = re.search(r"^description: (.+)$", front, re.M)
    if not name or name[1] != root.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name[1]):
        raise ValueError("Invalid skill name")
    if not description or not 1 <= len(description[1]) <= 1024: raise ValueError("Invalid description")
    for resource in re.findall(r"\]\(((?:references|assets)/[^)]+)\)", content):
        if not (root / resource).is_file(): raise ValueError(f"Missing resource: {resource}")
    print("Skill structure: OK", flush=True)
    return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"], cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
