"""Wayback CDX pagination and truthful snapshot conversion."""
from typing import Any
from urllib.parse import urlencode
from .models import ProviderResult, Snapshot, capture_date
from .transport import Transport, ProviderError, normalize_url


class WaybackClient:
    name = "wayback"
    capabilities = {"url_index", "historical_html", "year_filter"}

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    def search(self, url: str, start: int | None = None, end: int | None = None,
               limit: int = 30) -> ProviderResult:
        result = ProviderResult(self.name)
        try:
            url = normalize_url(url)
            resume: str | None = None
            seen: set[tuple[str, str]] = set()
            while len(result.records) < limit:
                params: dict[str, Any] = {"url": url, "output": "json", "fl": "timestamp,original,statuscode,mimetype,digest",
                                          "limit": min(100, limit - len(result.records)), "showResumeKey": "true",
                                          "collapse": "timestamp:6" if start is not None and start == end else "timestamp:4",
                                          "filter": "!mimetype:warc/revisit"}
                if start: params["from"] = start
                if end: params["to"] = end
                if resume: params["resumeKey"] = resume
                raw = self.transport.get("https://web.archive.org/cdx/search/cdx?" + urlencode(params)).decode("utf-8")
                # CDX appends a resume token after a blank line outside the JSON.
                import json
                chunks = raw.strip().split("\n\n", 1)
                rows = json.loads(chunks[0])
                if not isinstance(rows, list): raise ValueError("CDX response must be a table")
                if not rows: break
                if rows[0] != ["timestamp", "original", "statuscode", "mimetype", "digest"]:
                    raise ValueError("Unexpected CDX header")
                data_rows = rows[1:]
                json_resume = None
                if len(data_rows) >= 2 and data_rows[-2] == [] and isinstance(data_rows[-1], list) and len(data_rows[-1]) == 1:
                    json_resume = data_rows[-1][0]
                    data_rows = data_rows[:-2]
                for row in data_rows:
                    if not isinstance(row, list) or len(row) != 5: raise ValueError("Malformed CDX row")
                    stamp, original, status, mime, digest = row
                    pair = (original, stamp)
                    if pair in seen: continue
                    seen.add(pair)
                    result.records.append(Snapshot(
                        f"wayback:{stamp}:{original}", original,
                        f"https://web.archive.org/web/{stamp}/{original}", capture_date(stamp),
                        http_status=int(status) if str(status).isdigit() else None,
                        mime_type=mime if mime != "-" else None, content_hash=digest if digest != "-" else None,
                        archive_provider=self.name, limitations=["Index record; assets and replay availability unverified", "CDX digest is provider-defined, not SHA-256", "Monthly samples for a single year; yearly samples otherwise; revisit records excluded"]).to_dict())
                next_resume = json_resume or (chunks[1].strip() if len(chunks) == 2 else None)
                if not next_resume or next_resume == resume: break
                resume = next_resume
            result.truncated = bool(result.records)  # Deliberate temporal sampling is not a full capture inventory.
        except (ProviderError, ValueError, TypeError, KeyError) as exc:
            result.status = "partial" if result.records else "unavailable"
            result.errors.append(str(exc))
        return result
