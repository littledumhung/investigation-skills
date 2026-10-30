"""Common Crawl collection discovery and paginated CDXJ metadata (no WARC execution)."""
import json
import re
from urllib.parse import urlencode
from .models import ProviderResult, Snapshot, capture_date
from .transport import Transport, ProviderError, normalize_url


class CommonCrawlClient:
    name = "commoncrawl"
    capabilities = {"url_index", "collection_discovery", "year_filter"}

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    def search(self, url: str, start: int | None = None, end: int | None = None,
               limit: int = 30, collections: int = 3) -> ProviderResult:
        result = ProviderResult(self.name)
        try:
            url = normalize_url(url)
            catalog = self.transport.json("https://index.commoncrawl.org/collinfo.json")
            if not isinstance(catalog, list): raise ValueError("Invalid collection catalog")
            selected = []
            for item in catalog:
                match = re.fullmatch(r"CC-MAIN-(\d{4})-\d{2}", item.get("id", ""))
                if match and (start is None or int(match[1]) >= start) and (end is None or int(match[1]) <= end):
                    selected.append(item["id"])
            selected.sort(reverse=True)
            result.truncated = len(selected) > collections
            for collection in selected[:collections]:
                endpoint = f"https://index.commoncrawl.org/{collection}-index?"
                params = {"url": url, "output": "json"}
                pages = self.transport.json(endpoint + urlencode({**params, "showNumPages": "true"}))
                count = pages.get("pages") if isinstance(pages, dict) else None
                if not isinstance(count, int) or count < 0: raise ValueError("Invalid index page count")
                for page in range(min(count, 3)):
                    raw = self.transport.get(endpoint + urlencode({**params, "page": page})).decode("utf-8")
                    for line in raw.splitlines():
                        if not line.strip(): continue
                        row = json.loads(line)
                        original, stamp = row["url"], row["timestamp"]
                        record = Snapshot(f"cc:{collection}:{stamp}:{original}", original, None,
                            capture_date(stamp), http_status=int(row["status"]) if str(row.get("status")).isdigit() else None,
                            mime_type=row.get("mime"), content_hash=row.get("digest"), archive_provider=self.name,
                            limitations=["WARC index metadata only; no replay URL", "Collection sampling may omit older captures"]).to_dict()
                        record["warc"] = {k: row.get(k) for k in ("filename", "offset", "length")}
                        result.records.append(record)
                        if len(result.records) >= limit:
                            result.truncated = True
                            return result
                if count > 3: result.truncated = True
        except (ProviderError, ValueError, TypeError, KeyError, AttributeError) as exc:
            result.status = "partial" if result.records else "unavailable"
            result.errors.append(str(exc))
        return result
