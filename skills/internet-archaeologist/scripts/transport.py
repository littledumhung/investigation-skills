"""Bounded public HTTPS transport. No cookies, proxies or credentials in URLs.

DNS is pinned into the socket to avoid a validation/connection rebinding gap.
Redirects are independently validated; network errors are never empty results.
"""
import hashlib
import http.client
import ipaddress
import json
import os
import socket
import ssl
import time
from pathlib import Path
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit


class ProviderError(RuntimeError):
    """Unavailable, unsafe, malformed, over-budget or denied provider request."""


def normalize_url(value: str) -> str:
    value = value.strip()
    if any(ord(c) < 33 for c in value) or "\\" in value:
        raise ValueError("URL contains whitespace, controls or backslashes")
    parts = urlsplit(value if "://" in value else "https://" + value)
    if parts.scheme not in {"https", "http"} or not parts.hostname:
        raise ValueError("Only public HTTP(S) URLs are supported")
    if parts.username is not None or parts.password is not None:
        raise ValueError("URL credentials are forbidden")
    host = parts.hostname.rstrip(".").encode("idna").decode().lower()
    if parts.port not in {None, 80, 443}:
        raise ValueError("Nonstandard ports are forbidden")
    authority = f"[{host}]" if ":" in host else host
    if parts.port and parts.port != (443 if parts.scheme == "https" else 80):
        authority += f":{parts.port}"
    return urlunsplit((parts.scheme, authority, parts.path or "/", parts.query, ""))


def public_addresses(host: str, port: int) -> list[str]:
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise ProviderError("Non-public host rejected")
    try:
        addresses = sorted({r[4][0] for r in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)})
    except OSError as exc:
        raise ProviderError("DNS resolution failed") from exc
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise ProviderError("Non-public address rejected")
    return addresses


class Transport:
    """One investigation, bounded requests including retries and redirects."""

    def __init__(self, cache: Path | None = None, timeout: float = 12,
                 retries: int = 2, interval: float = 1.1, budget: int = 24,
                 max_bytes: int = 4_000_000, deadline: float = 180) -> None:
        self.cache = cache
        self.timeout = timeout
        self.retries = retries
        self.interval = interval
        self.budget = budget
        self.max_bytes = max_bytes
        self.expires = time.monotonic() + deadline
        self.calls = 0
        self.last: dict[str, float] = {}
        self.events: list[dict[str, Any]] = []

    def _request(self, url: str, headers: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port or (443 if parts.scheme == "https" else 80)
        address = public_addresses(host, port)[0]
        remaining = self.expires - time.monotonic()
        if remaining <= 0:
            raise ProviderError("Investigation deadline exceeded")
        conn = http.client.HTTPSConnection(host, port, timeout=min(self.timeout, remaining)) if parts.scheme == "https" else http.client.HTTPConnection(host, port, timeout=min(self.timeout, remaining))
        sock = socket.create_connection((address, port), timeout=min(self.timeout, remaining))
        try:
            conn.sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host) if parts.scheme == "https" else sock
            conn.request("GET", urlunsplit(("", "", parts.path or "/", parts.query, "")), headers=headers)
            response = conn.getresponse()
            data = response.read(self.max_bytes + 1)
            if len(data) > self.max_bytes:
                raise ProviderError("Response exceeds size limit")
            return response.status, {k.lower(): v for k, v in response.getheaders()}, data
        finally:
            conn.close()
            sock.close()

    def get(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        url = normalize_url(url)
        request_headers = {"User-Agent": "InternetArchaeologist/0.1 (public historical research)",
                           "Accept": "application/json,text/html;q=0.8,*/*;q=0.1"}
        request_headers.update(headers or {})
        # Never persist authenticated responses or secrets in cache keys/logs.
        sensitive_headers = {"authorization", "x-api-key", "x-subscription-token"}
        cacheable = not any(k.lower() in sensitive_headers for k in request_headers)
        key = hashlib.sha256(url.encode()).hexdigest()
        cachefile = self.cache / f"{key}.json" if self.cache and cacheable else None
        if cachefile and cachefile.exists():
            try:
                entry = json.loads(cachefile.read_text(encoding="utf-8"))
                if time.time() - entry["time"] < 86400:
                    self.events.append({"url": url, "cache": "hit", "fetched_at": entry["time"]})
                    return bytes.fromhex(entry["body"])
            except (OSError, ValueError, KeyError, TypeError):
                cachefile = None
        initial_host = urlsplit(url).hostname
        for redirect in range(6):
            host = urlsplit(url).hostname or ""
            for attempt in range(self.retries + 1):
                if self.calls >= self.budget or time.monotonic() >= self.expires:
                    raise ProviderError("Request budget/deadline exhausted")
                delay = max(0.0, self.interval - (time.monotonic() - self.last.get(host, 0)))
                if time.monotonic() + delay >= self.expires:
                    raise ProviderError("Deadline before rate-limit wait")
                time.sleep(delay)
                self.calls += 1
                self.last[host] = time.monotonic()
                response_headers: dict[str, str] = {}
                try:
                    status, response_headers, body = self._request(url, request_headers)
                    self.events.append({"url": url, "status": status, "attempt": attempt + 1})
                    if status in {429, 500, 502, 503, 504}:
                        raise ProviderError(f"HTTP {status}")
                    break
                except (OSError, http.client.HTTPException, ProviderError) as exc:
                    if attempt == self.retries or isinstance(exc, ProviderError) and "rejected" in str(exc):
                        raise ProviderError(str(exc)) from exc
                    retry_after = response_headers.get("retry-after", "") if 'response_headers' in locals() else ""
                    if retry_after and not retry_after.isdigit():
                        try:
                            wait_until = parsedate_to_datetime(retry_after)
                            retry_after = str(max(0, int((wait_until - datetime.now(timezone.utc)).total_seconds()) + 1))
                        except (TypeError, ValueError, OverflowError):
                            raise ProviderError("Unrecognized Retry-After; stopping to respect provider limits") from exc
                    backoff = max(2 ** attempt, float(retry_after) if retry_after.isdigit() else 0)
                    if backoff > 30 or time.monotonic() + backoff >= self.expires:
                        raise ProviderError("Retry wait exceeds investigation limits") from exc
                    time.sleep(backoff)
            if status in {301, 302, 303, 307, 308}:
                location = response_headers.get("location")
                if not location:
                    raise ProviderError("Redirect missing Location")
                previous_scheme = urlsplit(url).scheme
                url = normalize_url(urljoin(url, location))
                if previous_scheme == "https" and urlsplit(url).scheme != "https":
                    raise ProviderError("HTTPS downgrade redirect rejected")
                if urlsplit(url).hostname != initial_host:
                    request_headers = {k: v for k, v in request_headers.items() if k.lower() not in sensitive_headers}
                continue
            if not 200 <= status < 300:
                raise ProviderError(f"HTTP {status}")
            if cachefile:
                cachefile.parent.mkdir(parents=True, exist_ok=True)
                cachefile.write_text(json.dumps({"time": time.time(), "body": body.hex()}), encoding="utf-8")
            return body
        raise ProviderError("Too many redirects")

    def json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        try:
            return json.loads(self.get(url, headers))
        except (ValueError, UnicodeError) as exc:
            raise ProviderError("Malformed JSON response") from exc


def secret(name: str) -> str | None:
    return os.environ.get(name) or None
