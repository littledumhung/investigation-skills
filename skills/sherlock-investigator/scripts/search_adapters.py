"""Provider contracts, bounded orchestration and a host-agent result inbox.

No HTTP client, upload or credential storage is included. Network providers must
implement connection-time public IP pinning, redirect checks and their own
documented timeout. Host tools retain their own network security boundaries.
"""
import time
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode

CAPABILITIES = ('web_search', 'image_search', 'reverse_image', 'maps', 'geocoding',
                'street_view', 'overpass', 'commons', 'archives', 'ocr', 'vision')
BUDGETS = {'quick': {'searches': 3, 'calls': 8, 'candidates': 3, 'seconds': 120},
           'standard': {'searches': 10, 'calls': 25, 'candidates': 5, 'seconds': 600},
           'deep': {'searches': 25, 'calls': 60, 'candidates': 5, 'seconds': 1800}}

class ProviderUnavailable(RuntimeError):
    """Expected missing capability, timeout, or temporary provider failure."""

class SearchProvider(Protocol):
    name: str
    capabilities: set[str]
    def search(self, query: str, capability: str, timeout: float) -> list[dict]: ...

@dataclass
class Budget:
    mode: str = 'standard'
    calls: int = 0
    searches: int = 0
    started: float = 0

    def __post_init__(self):
        if self.mode not in BUDGETS:
            raise ValueError('Invalid mode')
        self.started = time.monotonic()

    def consume(self, search=True):
        limits = BUDGETS[self.mode]
        if self.calls >= limits['calls'] or search and self.searches >= limits['searches'] or time.monotonic() - self.started >= limits['seconds']:
            raise ProviderUnavailable('Investigation budget exhausted')
        self.calls += 1
        self.searches += int(search)

class Research:
    def __init__(self, providers=(), mode='standard'):
        self.providers = list(providers)
        self.budget = Budget(mode)
        self.failures = []

    def search(self, query, capability='web_search'):
        for provider in self.providers:
            if capability not in provider.capabilities:
                continue
            for attempt in range(2):
                try:
                    self.budget.consume()
                    return provider.search(query, capability, timeout=15)
                except (ProviderUnavailable, TimeoutError, ConnectionError):
                    self.failures.append({'provider': provider.name, 'capability': capability,
                                          'error': 'unavailable or budget exhausted', 'attempt': attempt + 1})
        return []

def manual_links(query):
    return {'web': 'https://www.google.com/search?' + urlencode({'q': query}),
            'images': 'https://www.google.com/search?' + urlencode({'tbm': 'isch', 'q': query}),
            'maps': 'https://www.google.com/maps/search/?' + urlencode({'api': 1, 'query': query}),
            'commons': 'https://commons.wikimedia.org/w/index.php?' + urlencode({'search': query})}
