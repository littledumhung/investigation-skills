import unittest
from scripts.query_expander import expand


class QueryTests(unittest.TestCase):
    def test_multilingual_features(self) -> None:
        result = expand("藍色方塊網頁遊戲")
        self.assertTrue(any(q["language"] == "en" and "blue" in q["query"] for q in result["queries"]))
        self.assertTrue(any(q["language"] == "ja" for q in result["queries"]))

    def test_no_repeat_round(self) -> None:
        first = expand("flash puzzle")
        seen = [q["query"] for q in first["queries"]]
        self.assertEqual(expand("flash puzzle", seen=seen)["queries"], [])
        second = expand("flash puzzle", seen=seen, new_clues=["developer name found"])
        self.assertTrue(second["queries"])
        self.assertTrue(all(q["query"] not in seen for q in second["queries"]))
