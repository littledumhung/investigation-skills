"""Preserve different date meanings and avoid claiming a launch date."""
from typing import Any


def build_timeline(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        source = record.get("archive_url") or record.get("url")
        for field, meaning in (("captured_at", "snapshot"), ("content_timestamp", "content_publication_unverified"),
                               ("published_at", "release_publication"), ("committed_at", "commit"), ("created_at", "record_creation")):
            value = record.get(field)
            if not value: continue
            key = (str(value), meaning, str(source))
            if key in seen: continue
            seen.add(key)
            events.append({"date": value, "date_type": meaning, "source_url": source,
                           "snapshot_id": record.get("snapshot_id"),
                           "description": "可查證的快照索引紀錄（不是創立日期）" if field == "captured_at" else record.get("name") or record.get("title") or meaning,
                           "http_status": record.get("http_status")})
    return sorted(events, key=lambda r: str(r["date"]))
