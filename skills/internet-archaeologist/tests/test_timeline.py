import unittest
from scripts.timeline_builder import build_timeline


class TimelineTests(unittest.TestCase):
    def test_capture_publication_separate(self) -> None:
        r = build_timeline([{"captured_at": "2013-01-01", "content_timestamp": "2011-01-01", "archive_url": "https://example.org/a"}])
        self.assertEqual([e["date_type"] for e in r], ["content_publication_unverified", "snapshot"])
        self.assertEqual(len(r), 2)

    def test_dedup(self) -> None:
        row = {"captured_at": "2013-01-01", "archive_url": "https://example.org/a"}
        self.assertEqual(len(build_timeline([row, row])), 1)
