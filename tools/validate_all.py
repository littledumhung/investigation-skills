"""Run skill metadata checks and offline suites in separate processes."""
from pathlib import Path
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def main():
    failed = False
    for skill in sorted((ROOT / "skills").iterdir()):
        if not skill.is_dir():
            continue
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        if front.get("name") != skill.name or not front.get("description"):
            raise ValueError(f"Invalid skill metadata: {skill.name}")
        for link in re.findall(r"\]\(((?:references|assets|examples)/[^)]+)\)", text):
            if not (skill / link).is_file():
                raise ValueError(f"Missing resource: {skill.name}/{link}")
        print(f"Validating {skill.name}", flush=True)
        if skill.name == "truth-engine":
            commands = [[sys.executable, "scripts/validate.py"], [sys.executable, "-m", "pytest", "tests", "-q"]]
        else:
            commands = [[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]]
        for command in commands:
            failed |= subprocess.run(command, cwd=skill).returncode != 0
    return int(failed)

if __name__ == "__main__":
    raise SystemExit(main())
