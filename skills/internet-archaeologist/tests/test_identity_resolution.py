import unittest
from scripts.identity_resolver import resolve
from tests.helpers import observation


class IdentityTests(unittest.TestCase):
    def test_translated_game_name_alone_unknown(self) -> None:
        self.assertEqual(resolve([observation("a", "translated_name")])["label"], "UNRESOLVED")

    def test_multilingual_alias_primary(self) -> None:
        self.assertEqual(resolve([observation("a", "official_rename"), observation("b", "developer")])["label"], "SAME_ENTITY")

    def test_similar_games_different(self) -> None:
        self.assertEqual(resolve([observation("a", "appearance"), observation("b", "official_distinct", False)])["label"], "DIFFERENT_ENTITY")

    def test_domain_reuse(self) -> None:
        self.assertEqual(resolve([observation("a", "same_domain"), observation("b", "ownership_discontinuity", False)])["label"], "UNRESOLVED")

    def test_renamed_repository(self) -> None:
        r = resolve([observation("a", "repository_continuity"), observation("b", "official_migration")])
        self.assertEqual(r["label"], "SAME_ENTITY")

    def test_third_party_only(self) -> None:
        self.assertEqual(resolve([observation("a", "mention")])["label"], "UNRESOLVED")

    def test_copies_not_independent(self) -> None:
        a = observation("a", "official_rename")
        r = resolve([a, dict(a, source_url="https://mirror.example.org/")])
        self.assertEqual(r["independent_origins"], 1)
        self.assertEqual(r["label"], "POSSIBLY_SAME")

    def test_chronology_conflict_blocks(self) -> None:
        r = resolve([observation("a", "official_rename"), observation("b", "developer"), observation("c", "temporal_contradiction", False)])
        self.assertEqual(r["label"], "UNRESOLVED")

    def test_unknown_origin_not_counted(self) -> None:
        a = observation("a", "official_rename")
        del a["origin_id"]
        self.assertEqual(resolve([a])["independent_origins"], 0)

    def test_same_origin_contradiction_never_discarded(self) -> None:
        rows = [observation("a", "official_rename"), observation("b", "developer"), observation("a", "temporal_contradiction", False)]
        for evidence in (rows, list(reversed(rows))):
            r = resolve(evidence)
            self.assertEqual(r["label"], "UNRESOLVED")
            self.assertEqual(len(r["contradictions"]), 1)

    def test_appearance_and_name_not_enough(self) -> None:
        self.assertEqual(resolve([observation("a", "title"), observation("b", "appearance")])["label"], "UNRESOLVED")

    def test_same_origin_multiple_claims_not_corroboration(self) -> None:
        r = resolve([observation("a", "official_rename"), observation("a", "developer")])
        self.assertEqual(r["label"], "POSSIBLY_SAME")

    def test_malformed_evidence_rejected(self) -> None:
        with self.assertRaises(ValueError): resolve([None])

    def test_negative_relationship_is_not_positive(self) -> None:
        self.assertEqual(resolve([observation("a", "related", False)])["label"], "UNRESOLVED")
