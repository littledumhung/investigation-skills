"""Validate package integrity, schema and deterministic unit tests."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    if not text.startswith('---\n') or not re.search(r'^name: sherlock-investigator$', text, re.M):
        raise ValueError('Invalid skill frontmatter')
    for match in re.findall(r'\]\((references/[^)]+)\)', text):
        if not (ROOT / match).is_file():
            raise ValueError('Missing linked reference: ' + match)
    schema = json.loads((ROOT / 'assets/report.schema.json').read_text(encoding='utf-8'))
    try:
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        print('JSON Schema: validated')
    except ImportError:
        print('JSON Schema validation unavailable; install .[test] for full acceptance', file=sys.stderr)
        return 2
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and not result.skipped else 1

if __name__ == '__main__':
    raise SystemExit(main())
