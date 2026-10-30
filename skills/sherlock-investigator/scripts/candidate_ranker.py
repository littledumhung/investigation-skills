"""Heuristic ordering. Scores are not calibrated probabilities."""
from urllib.parse import urlsplit

WEIGHTS = {'direct': 5, 'strong': 3, 'weak': 1, 'contradiction': -6, 'missing': 0}

def source_group(e):
    # No independence claim => conservatively group all unknown sources together.
    # Independence groups must be assigned by the agent after lineage review.
    return e.get('independence_group') or 'unverified-lineage'

def rank_candidates(hypotheses, evidence, checks=(), weights=None):
    weights = weights or WEIGHTS
    ranked = []
    for h in hypotheses:
        items = [e for e in evidence if e['hypothesis_id'] == h['id']]
        groups = {}
        for e in items:
            group = source_group(e)
            # Multiple mirrors of one source cannot inflate support.
            weight = weights[e['kind']] if not e.get('uncertain') else (min(weights[e['kind']], 1) if weights[e['kind']] > 0 else weights[e['kind']])
            groups.setdefault(group, []).append((weight, e))
        score = 0
        independent_strong = 0
        for group, entries in groups.items():
            positive = max([v for v, _ in entries if v > 0], default=0)
            negative = min([v for v, _ in entries if v < 0], default=0)
            score += positive + negative
            if positive >= 3 and group != 'unverified-lineage':
                independent_strong += 1
        contradiction = any(e['kind'] == 'contradiction' for e in items)
        checked = any(c['hypothesis_id'] == h['id'] for c in checks)
        has_direct = any(e['kind'] == 'direct' and not e.get('uncertain') for e in items)
        confidence = 'undetermined'
        if score > 0:
            confidence = 'low'
        if score >= 5 and independent_strong >= 2 and not contradiction:
            confidence = 'medium'
        if score >= 8 and independent_strong >= 2 and has_direct and checked and not contradiction and not h.get('unverified'):
            confidence = 'high'
        if items and all(e.get('source_type') == 'synthetic' for e in items):
            confidence = 'undetermined'
        ranked.append({**h, 'score': score, 'confidence': confidence,
                       'independent_strong_sources': independent_strong,
                       'contradiction_checked': checked, 'has_contradiction': contradiction})
    return sorted(ranked, key=lambda h: h['score'], reverse=True)
