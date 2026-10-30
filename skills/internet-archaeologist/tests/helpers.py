"""Explicit synthetic fixtures, never investigation evidence."""
from typing import Any
from scripts.transport import ProviderError


class FakeTransport:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = iter(responses)
        self.urls: list[str] = []

    def _next(self, url: str) -> Any:
        self.urls.append(url)
        value = next(self.responses)
        if isinstance(value, Exception): raise value
        return value

    def get(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        return self._next(url)

    def json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        return self._next(url)


def observation(origin: str, kind: str, supports: bool = True) -> dict[str, Any]:
    return {"source_url": "https://example.org/" + origin, "observed_at": "2026-10-30T00:00:00Z", "origin_id": origin,
            "kind": kind, "supports": supports, "detail": "Synthetic test assertion, not real historical evidence"}
