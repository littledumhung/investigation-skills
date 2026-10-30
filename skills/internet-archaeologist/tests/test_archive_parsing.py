import unittest
from scripts.archive_parser import parse_html, compare
from scripts.wayback_client import WaybackClient
from tests.helpers import FakeTransport

HEADER = '["timestamp","original","statuscode","mimetype","digest"]'


class ArchiveTests(unittest.TestCase):
    def test_multi_year(self) -> None:
        body = ('[' + HEADER + ',["20120101000000","http://example.org/","200","text/html","AAA"],'
                '["20170101000000","http://example.org/","404","text/html","BBB"]]').encode()
        r = WaybackClient(FakeTransport([body])).search("example.org")
        self.assertEqual(r.status, "ok")
        self.assertEqual(len(r.records), 2)
        self.assertEqual(r.records[1]["http_status"], 404)
        self.assertIsNone(r.records[0]["content_timestamp"])

    def test_no_archive(self) -> None:
        r = WaybackClient(FakeTransport([b"[]"])).search("example.org")
        self.assertEqual((r.status, r.records), ("ok", []))

    def test_resume_key(self) -> None:
        first = ('[' + HEADER + ',["20120101000000","http://example.org/","200","text/html","AAA"]]\n\nnext-token').encode()
        fake = FakeTransport([first, b"[]"])
        r = WaybackClient(fake).search("example.org")
        self.assertEqual(len(r.records), 1)
        self.assertIn("resumeKey=next-token", fake.urls[1])

    def test_incomplete_html(self) -> None:
        r = parse_html('<title>Old site</title><a href="/about">About<img src="x.png"><p>partial', "https://example.org/")
        self.assertEqual(r["title"], "Old site")
        self.assertEqual(r["assets"][0]["url"], "https://example.org/x.png")
        self.assertEqual(r["assets"][0]["availability"], "unverified")

    def test_json_resume_format(self) -> None:
        first = ('[' + HEADER + ',["20120101000000","http://example.org/","200","text/html","AAA"],[],["next-token"]]').encode()
        fake = FakeTransport([first, b"[]"])
        result = WaybackClient(fake).search("example.org")
        self.assertEqual(result.status, "ok")
        self.assertIn("resumeKey=next-token", fake.urls[1])

    def test_diff(self) -> None:
        r = compare(parse_html("<p>old", "https://example.org"), parse_html("<p>new", "https://example.org"))
        self.assertIn("-old", r["text_diff"])
        self.assertIn("+new", r["text_diff"])
