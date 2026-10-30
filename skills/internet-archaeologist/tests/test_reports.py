import unittest
from scripts.report_builder import build_report, markdown
from scripts.identity_resolver import resolve
from tests.helpers import observation


class ReportTests(unittest.TestCase):
    def test_identity_evidence_auditable_in_markdown(self) -> None:
        evidence = [observation("official", "official_rename"), observation("conflict", "temporal_contradiction", False)]
        evidence[1]["event_date"] = "2017-01-01"
        r = build_report("game", "deep", {}, [], {"search_log": []}, resolve(evidence))
        output = markdown(r)
        self.assertIn("https://example.org/conflict", output)
        self.assertIn("2017-01-01", output)
        self.assertIn("UNRESOLVED", output)

    def test_no_records_not_found_claim(self) -> None:
        r = build_report("game", "quick", {}, [], {"search_log": []})
        self.assertIsNone(r["most_likely_target"])
        self.assertEqual(r["identification"]["label"], "UNRESOLVED")
