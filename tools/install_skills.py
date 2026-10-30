"""Copy this collection into a Codex skill directory without overwriting skills."""
import argparse
import os
from pathlib import Path
import shutil

NAMES = ("sherlock-investigator", "internet-archaeologist", "truth-engine")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "skills"
    dest = args.dest.expanduser().resolve()
    for name in NAMES:
        if not (source / name / "SKILL.md").is_file():
            parser.error(f"Missing source skill: {name}")
        if (dest / name).exists():
            parser.error(f"Already exists; move it outside the skills folder to back it up first: {dest / name}")
    for name in NAMES:
        print(f"{source / name} -> {dest / name}")
        if not args.dry_run:
            shutil.copytree(source / name, dest / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".venv", "*.egg-info", "results"))
    print("Preview complete." if args.dry_run else "Installed 3 skills. Open a new Codex conversation.")

if __name__ == "__main__":
    main()
