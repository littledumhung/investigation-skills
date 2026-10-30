"""Public repository identity, tags, releases, and recent commit history."""
import re
from urllib.parse import quote
from .models import ProviderResult
from .transport import Transport, ProviderError, secret


class GitHubHistory:
    name = "github"
    capabilities = {"repository", "tags", "releases", "commits"}

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    def search(self, repo: str, limit: int = 30) -> ProviderResult:
        result = ProviderResult(self.name)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            return ProviderResult(self.name, status="unavailable", errors=["Expected owner/repository"])
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token := secret("GITHUB_TOKEN"): headers["Authorization"] = f"Bearer {token}"
        base = "https://api.github.com/repos/" + quote(repo, safe="/")
        try:
            metadata = self.transport.json(base, headers)
            if not isinstance(metadata, dict) or not metadata.get("full_name") or metadata.get("private") is not False:
                raise ValueError("Not a confirmed public repository")
            result.records.append({"kind": "repository", "requested_name": repo, "full_name": metadata["full_name"],
                "url": metadata.get("html_url"), "created_at": metadata.get("created_at"), "archived": metadata.get("archived"),
                "description": metadata.get("description"), "owner": metadata.get("owner", {}).get("login"),
                "name_differs": repo.lower() != metadata["full_name"].lower(),
                "limitation": "Current API identity; not proof of rename date or earliest project origin"})
            for kind in ("releases", "tags", "commits"):
                for page in range(1, 4):
                    rows = self.transport.json(f"{base}/{kind}?per_page={min(limit, 100)}&page={page}", headers)
                    if not isinstance(rows, list): raise ValueError(f"Invalid {kind} response")
                    for row in rows:
                        if not isinstance(row, dict): raise ValueError("Malformed repository history record")
                        record = {"kind": kind, "name": row.get("name") or row.get("tag_name") or row.get("sha"),
                            "url": row.get("html_url"), "published_at": row.get("published_at"),
                            "sha": row.get("sha") or row.get("commit", {}).get("sha"),
                            "prerelease": row.get("prerelease")}
                        if kind == "commits": record["committed_at"] = row.get("commit", {}).get("committer", {}).get("date")
                        if kind == "tags": record["url"] = metadata["html_url"] + "/tree/" + quote(row["name"], safe="")
                        result.records.append(record)
                    if len(rows) < min(limit, 100): break
                    if page == 3: result.truncated = True
        except (ProviderError, ValueError, KeyError, TypeError, AttributeError) as exc:
            result.status = "partial" if result.records else "unavailable"
            result.errors.append(str(exc))
        return result
