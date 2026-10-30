from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def bundle():
    return json.loads((ROOT / 'examples/public-landmark.evidence.json').read_text(encoding='utf-8'))
