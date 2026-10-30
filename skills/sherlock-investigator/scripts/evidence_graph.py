"""Validated evidence interchange and graph integrity."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

NODE_TYPES = {'Claim', 'Observation', 'Source', 'Hypothesis', 'Location', 'Object', 'Media'}
RELATIONS = {'SUPPORTS', 'CONTRADICTS', 'DERIVED_FROM', 'MATCHES', 'REQUIRES_VERIFICATION'}
KINDS = {'direct', 'strong', 'weak', 'contradiction', 'missing'}

def now():
    return datetime.now(timezone.utc).isoformat()

def validate_bundle(bundle):
    from scripts.input_analyzer import validate_url
    if not isinstance(bundle, dict):
        raise ValueError('Bundle must be an object')
    for key in ('hypotheses', 'evidence', 'nodes', 'edges', 'contradiction_checks'):
        if key in bundle and not isinstance(bundle[key], list):
            raise ValueError(key + ' must be a list')
    candidates = bundle.get('hypotheses', [])
    ids = [h['id'] for h in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate hypothesis ID')
    for h in candidates:
        for field in ('id', 'name', 'type', 'supporting_clues', 'contradicting_clues', 'unverified', 'next_step'):
            if field not in h:
                raise ValueError('Missing hypothesis field: ' + field)
        for field in ('id', 'name', 'type', 'next_step'):
            if not isinstance(h[field], str) or not h[field].strip():
                raise ValueError('Hypothesis identity/text must be nonempty strings')
        for field in ('supporting_clues', 'contradicting_clues', 'unverified'):
            if not isinstance(h[field], list):
                raise ValueError('Hypothesis clue fields must be lists')
        if 'location' in h:
            loc = h['location']
            if not isinstance(loc, dict):
                raise ValueError('location must be an object')
            for axis, limit in (('latitude', 90), ('longitude', 180)):
                value = loc.get(axis)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > limit:
                    raise ValueError('Invalid WGS84 coordinate')
            if loc.get('role') not in ('poi_center', 'building_center', 'camera_position', 'estimated_photo_position'):
                raise ValueError('Location role required')
            if loc.get('verification') not in ('verified', 'estimated'):
                raise ValueError('Location verification label required')
            accuracy = loc.get('accuracy_m')
            if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not math.isfinite(accuracy) or accuracy <= 0:
                raise ValueError('Positive accuracy_m required')
    evidence = bundle.get('evidence', [])
    eids = [e['evidence_id'] for e in evidence]
    if len(set(eids)) != len(eids):
        raise ValueError('Duplicate evidence ID')
    for e in evidence:
        for field in ('evidence_id', 'source', 'source_type', 'observed_at', 'original_observation',
                      'interpretation', 'supporting_claim_ids', 'limitations', 'hypothesis_id', 'kind'):
            if field not in e:
                raise ValueError('Missing evidence field: ' + field)
        if e['hypothesis_id'] not in ids or e['kind'] not in KINDS:
            raise ValueError('Unknown hypothesis or evidence kind')
        for field in ('evidence_id', 'source', 'source_type', 'observed_at', 'original_observation', 'interpretation'):
            if not isinstance(e[field], str) or not e[field].strip():
                raise ValueError('Evidence text must be nonempty strings')
        if 'uncertain' in e and not isinstance(e['uncertain'], bool):
            raise ValueError('uncertain must be boolean')
        if 'independence_group' in e and not isinstance(e['independence_group'], str):
            raise ValueError('independence_group must be text')
        if not isinstance(e['limitations'], list) or not isinstance(e['supporting_claim_ids'], list):
            raise ValueError('Evidence lists have invalid type')
        datetime.fromisoformat(e['observed_at'].replace('Z', '+00:00'))
        if urlsplit(e['source']).scheme in ('http', 'https'):
            validate_url(e['source'], resolve=False)
    nodes = bundle.get('nodes', [])
    nids = [n['id'] for n in nodes]
    if len(set(nids)) != len(nids) or any(n['type'] not in NODE_TYPES for n in nodes):
        raise ValueError('Invalid graph node')
    for edge in bundle.get('edges', []):
        if edge['from'] not in nids or edge['to'] not in nids or edge['relation'] not in RELATIONS:
            raise ValueError('Invalid graph edge')
    for e in evidence:
        if any(cid not in nids for cid in e['supporting_claim_ids']):
            raise ValueError('Unresolved supporting claim ID')
    for check in bundle.get('contradiction_checks', []):
        if check.get('hypothesis_id') not in ids or not isinstance(check.get('finding'), str) or not check.get('finding'):
            raise ValueError('Invalid contradiction search record')
    return bundle

def load_bundle(path):
    p = Path(path)
    if p.stat().st_size > 5 * 1024 * 1024:
        raise ValueError('Evidence bundle exceeds 5 MB')
    return validate_bundle(json.loads(p.read_text(encoding='utf-8-sig')))
