"""JSON-compatible investigation records; unknown facts remain None."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Snapshot:
    snapshot_id: str
    original_url: str
    archive_url: str | None
    captured_at: str | None = None
    content_timestamp: str | None = None
    http_status: int | None = None
    mime_type: str | None = None
    content_hash: str | None = None
    archive_provider: str = "unknown"
    available_assets: list[str] | None = None
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderResult:
    provider: str
    records: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    errors: list[str] = field(default_factory=list)
    truncated: bool = False
    queried_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def capture_date(value: str) -> str:
    return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).isoformat()
