"""Explicit agent/OCR interchange. No invented visual observations."""
import re
from typing import Protocol

class VisionProvider(Protocol):
    def extract(self, path: str) -> list[dict]: ...

def observation(text, method='agent_visual', uncertain=True, region=None):
    if method not in ('agent_visual', 'ocr', 'manual', 'metadata'):
        raise ValueError('Unknown observation method')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Empty observation')
    return {'text': text, 'method': method, 'uncertain': bool(uncertain), 'region': region,
            'trusted_instructions': False}

def classify(text, kind=None):
    tags = []
    rules = {'GEOLOCATION': r'在哪|地點|座標|經緯|街景|猜地|geoguess|where|location|geolocat',
             'OBJECT_IDENTIFICATION': r'型號|機器|物品|model|device|object',
             'IMAGE_PROVENANCE': r'原始|最早|來源|provenance|original|source',
             'HISTORICAL_IDENTIFICATION': r'歷史|舊照|histor|vintage',
             'EVENT_CONTEXT': r'事件|event|context'}
    for tag, pattern in rules.items():
        if re.search(pattern, text, re.I):
            tags.append(tag)
    if kind == 'video':
        tags.append('VIDEO_INVESTIGATION')
    return tags or ['GENERAL_INVESTIGATION']

def privacy_gate(intent, scope):
    """Conservative CLI guard, supplemented by host-agent semantic review.

    Keyword checks are NOT a general-purpose privacy classifier.
    """
    blocked = r'人肉|人臉識別|私人住址|住哪|跟蹤|追蹤.*人|doxx|home address|where.{0,20}live|track.{0,30}(person|her|him)|face recogni'
    if re.search(blocked, intent, re.I):
        return 'refused'
    return 'reviewed_public' if scope in ('public', 'game') else 'pending_review'
