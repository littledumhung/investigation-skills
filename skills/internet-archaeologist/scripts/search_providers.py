"""Additional metadata providers and a replaceable capability registry."""
from typing import Protocol, Any
from urllib.parse import urlencode, quote
from .models import ProviderResult
from .transport import Transport, ProviderError, secret


class Provider(Protocol):
    name: str
    capabilities: set[str]


class MetadataSearch:
    """Archive.org, Wikipedia, public GitLab, or explicitly keyed Brave search."""
    def __init__(self, transport: Transport, name: str) -> None:
        if name not in {"archiveorg", "wikipedia", "gitlab", "brave"}: raise ValueError("Unknown provider")
        self.transport, self.name = transport, name
        self.capabilities = {"metadata_search"}

    def search(self, query: str, limit: int = 10, language: str = "en") -> ProviderResult:
        result = ProviderResult(self.name)
        try:
            for page in range(1, 3):
                if self.name == "archiveorg":
                    url = "https://archive.org/advancedsearch.php?" + urlencode({"q": query, "output": "json", "rows": limit, "page": page, "fl[]": ["identifier", "title", "date", "creator", "mediatype"]}, doseq=True)
                    data = self.transport.json(url)
                    rows = data["response"]["docs"]
                    records = [{"title": r.get("title"), "url": "https://archive.org/details/" + quote(r["identifier"], safe=""),
                        "content_timestamp": r.get("date"), "creator": r.get("creator"), "media_type": r.get("mediatype"),
                        "availability": "historical_record", "limitation": "Item metadata does not establish download rights"} for r in rows]
                elif self.name == "wikipedia":
                    if language not in {"en", "zh", "ja"}: raise ValueError("Unsupported language")
                    data = self.transport.json(f"https://{language}.wikipedia.org/w/api.php?" + urlencode({"action": "query", "list": "search", "srsearch": query, "srlimit": min(limit, 50), "sroffset": (page - 1) * min(limit, 50), "format": "json"}))
                    rows = data["query"]["search"]
                    records = [{"title": r["title"], "url": f"https://{language}.wikipedia.org/?curid={r['pageid']}", "limitation": "Secondary discovery source; follow primary citations"} for r in rows]
                elif self.name == "gitlab":
                    data = self.transport.json("https://gitlab.com/api/v4/projects?" + urlencode({"search": query, "visibility": "public", "per_page": min(limit, 100), "page": page}))
                    rows = data
                    records = [{"title": r["path_with_namespace"], "url": r["web_url"], "created_at": r.get("created_at"), "description": r.get("description")} for r in rows if r.get("visibility") == "public"]
                else:
                    token = secret("BRAVE_SEARCH_API_KEY")
                    if not token: return ProviderResult(self.name, status="not_configured", errors=["BRAVE_SEARCH_API_KEY not set; use Agent web search instead"])
                    data = self.transport.json("https://api.search.brave.com/res/v1/web/search?" + urlencode({"q": query, "count": min(limit, 20), "offset": page - 1}), {"X-Subscription-Token": token})
                    rows = data.get("web", {}).get("results", [])
                    records = [{"title": r["title"], "url": r["url"], "description": r.get("description"), "limitation": "Search snippet; verify the underlying page"} for r in rows]
                if not isinstance(rows, list): raise ValueError("Expected results list")
                result.records.extend(records)
                if len(result.records) >= limit:
                    result.records = result.records[:limit]
                    result.truncated = True
                    break
                if not rows: break
        except (ProviderError, ValueError, KeyError, TypeError, AttributeError) as exc:
            result.status = "partial" if result.records else "unavailable"
            result.errors.append(str(exc))
        return result


def capabilities() -> dict[str, dict[str, Any]]:
    return {
        "wayback": {"features": ["url_index", "historical_html"], "configured": True},
        "commoncrawl": {"features": ["url_index", "warc_metadata"], "configured": True},
        "github": {"features": ["repository", "tags", "releases", "commits"], "configured": True, "authenticated": bool(secret("GITHUB_TOKEN"))},
        **{n: {"features": ["metadata_search"], "configured": n != "brave" or bool(secret("BRAVE_SEARCH_API_KEY"))} for n in ("archiveorg", "wikipedia", "gitlab", "brave")},
        "agent": {"features": ["web_search", "translation", "image_understanding"], "configured": None, "limitation": "Detect tools in the host Agent; Python does not supply these capabilities"}}
