import unittest
from datetime import date
from scripts.query_expander import temporal_range


class TemporalTests(unittest.TestCase):
    def test_five_year_range(self) -> None:
        r = temporal_range("2010–2015")
        self.assertEqual((r["start_year"], r["end_year"]), (2010, 2015))
        self.assertFalse(r["inferred"])

    def test_relative_anchor(self) -> None:
        r = temporal_range("十年前", date(2026, 10, 30))
        self.assertEqual((r["start_year"], r["end_year"]), (2014, 2018))
        self.assertTrue(r["inferred"])

    def test_before(self) -> None:
        r = temporal_range("2009 年以前")
        self.assertIsNone(r["start_year"])
        self.assertEqual(r["end_year"], 2008)

    def test_era_is_heuristic(self) -> None:
        self.assertTrue(temporal_range("Windows XP 時代")["inferred"])

    def test_no_date_unknown(self) -> None:
        self.assertIsNone(temporal_range("blue game")["start_year"])
