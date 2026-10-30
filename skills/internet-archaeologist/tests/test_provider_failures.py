import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.transport import Transport, ProviderError
from scripts.wayback_client import WaybackClient
from scripts.commoncrawl_client import CommonCrawlClient
from scripts.github_history import GitHubHistory
from scripts.search_providers import MetadataSearch
from tests.helpers import FakeTransport


class FailureTests(unittest.TestCase):
    def test_wayback_outage(self) -> None:
        r = WaybackClient(FakeTransport([ProviderError("HTTP 503")])).search("example.org")
        self.assertEqual(r.status, "unavailable")
        self.assertIn("503", r.errors[0])

    def test_cc_outage(self) -> None:
        r = CommonCrawlClient(FakeTransport([ProviderError("Timeout")])).search("example.org")
        self.assertEqual(r.status, "unavailable")

    def test_invalid_response(self) -> None:
        r = WaybackClient(FakeTransport([b"<html>Denied</html>"])).search("example.org")
        self.assertEqual(r.status, "unavailable")

    def test_cc_metadata_no_fake_replay(self) -> None:
        fake = FakeTransport([[{"id": "CC-MAIN-2015-06"}], {"pages": 1}, b'{"url":"http://example.org/","timestamp":"20150101000000","status":"200","mime":"text/html","filename":"crawl-data/x","offset":"1","length":"2"}'])
        r = CommonCrawlClient(fake).search("example.org", 2015, 2015)
        self.assertEqual(r.status, "ok")
        self.assertIsNone(r.records[0]["archive_url"])
        self.assertEqual(r.records[0]["warc"]["offset"], "1")

    def test_github_partial_history(self) -> None:
        fake = FakeTransport([{"full_name": "new/name", "private": False, "html_url": "https://github.com/new/name"}, [], ProviderError("rate limited")])
        r = GitHubHistory(fake).search("old/name")
        self.assertEqual(r.status, "partial")
        self.assertTrue(r.records[0]["name_differs"])

    def test_private_repo_rejected(self) -> None:
        r = GitHubHistory(FakeTransport([{"full_name": "a/b", "private": True}])).search("a/b")
        self.assertEqual(r.status, "unavailable")

    @patch("scripts.transport.time.sleep")
    def test_retry_and_budget(self, sleep: object) -> None:
        t = Transport(retries=2, budget=2, interval=0)
        with patch.object(t, "_request", return_value=(503, {}, b"")) as request:
            with self.assertRaises(ProviderError): t.get("https://example.org")
            self.assertEqual(request.call_count, 2)
        self.assertEqual(t.calls, 2)

    @patch("scripts.transport.time.sleep")
    def test_cache_reuse(self, sleep: object) -> None:
        with tempfile.TemporaryDirectory() as folder:
            t = Transport(Path(folder), interval=0)
            with patch.object(t, "_request", return_value=(200, {}, b"payload")) as request:
                self.assertEqual(t.get("https://example.org"), b"payload")
                self.assertEqual(t.get("https://example.org"), b"payload")
                self.assertEqual(request.call_count, 1)

    @patch.dict("os.environ", {}, clear=True)
    def test_search_key_optional(self) -> None:
        r = MetadataSearch(FakeTransport([]), "brave").search("game")
        self.assertEqual(r.status, "not_configured")
