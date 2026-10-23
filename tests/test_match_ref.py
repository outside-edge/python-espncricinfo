import dataclasses
import unittest
from unittest.mock import patch

import pytest

from espncricinfo.match_ref import MatchRef


class TestMatchRefFields(unittest.TestCase):
    def test_fields_stored_as_int(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        assert ref.series_id == 1478874
        assert ref.match_id == 1478914
        assert isinstance(ref.series_id, int)
        assert isinstance(ref.match_id, int)

    def test_string_inputs_coerced_to_int(self):
        ref = MatchRef(series_id="1478874", match_id="1478914")
        assert isinstance(ref.series_id, int)
        assert isinstance(ref.match_id, int)

    def test_tuple_unpacking(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        series_id, match_id = ref
        assert series_id == 1478874
        assert match_id == 1478914

    def test_repr(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        assert "1478874" in repr(ref)
        assert "1478914" in repr(ref)

    def test_is_hashable(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        # Should be usable in a set and as a dict key
        s = {ref}
        assert ref in s
        d = {ref: "test"}
        assert d[ref] == "test"

    def test_is_immutable(self):
        ref = MatchRef(series_id=1478874, match_id=1478914)
        with pytest.raises(dataclasses.FrozenInstanceError):
            ref.series_id = 999


class TestMatchRefSerialization(unittest.TestCase):
    def setUp(self):
        self.ref = MatchRef(series_id=1478874, match_id=1478914)

    # --- to_dict ---

    def test_to_dict_returns_dict(self):
        assert isinstance(self.ref.to_dict(), dict)

    def test_to_dict_keys(self):
        d = self.ref.to_dict()
        assert "series_id" in d
        assert "match_id" in d

    def test_to_dict_values_are_int(self):
        d = self.ref.to_dict()
        assert d["series_id"] == 1478874
        assert d["match_id"] == 1478914
        assert isinstance(d["series_id"], int)
        assert isinstance(d["match_id"], int)

    # --- from_dict ---

    def test_from_dict_round_trips(self):
        d = self.ref.to_dict()
        restored = MatchRef.from_dict(d)
        assert restored.series_id == self.ref.series_id
        assert restored.match_id == self.ref.match_id

    def test_from_dict_accepts_string_values(self):
        ref = MatchRef.from_dict({"series_id": "1478874", "match_id": "1478914"})
        assert ref.series_id == 1478874
        assert ref.match_id == 1478914

    # --- to_csv_row ---

    def test_to_csv_row_returns_list(self):
        assert isinstance(self.ref.to_csv_row(), list)

    def test_to_csv_row_values_are_strings(self):
        row = self.ref.to_csv_row()
        assert row == ["1478874", "1478914"]
        for v in row:
            assert isinstance(v, str)

    def test_to_csv_row_order_is_series_then_match(self):
        row = self.ref.to_csv_row()
        assert row[0] == "1478874"  # series_id first
        assert row[1] == "1478914"  # match_id second

    # --- from_csv_row ---

    def test_from_csv_row_round_trips(self):
        row = self.ref.to_csv_row()
        restored = MatchRef.from_csv_row(row)
        assert restored.series_id == self.ref.series_id
        assert restored.match_id == self.ref.match_id

    def test_from_csv_row_accepts_tuple(self):
        ref = MatchRef.from_csv_row(("1478874", "1478914"))
        assert ref.series_id == 1478874
        assert ref.match_id == 1478914


class TestMatchRefToMatch(unittest.TestCase):
    def test_to_match_returns_match_instance(self):
        import json
        from pathlib import Path

        from espncricinfo.match import Match

        fixture_path = (
            Path(__file__).parent / "fixtures" / "match_1478914_next_data.json"
        )
        next_data = json.loads(fixture_path.read_text())

        ref = MatchRef(series_id=1478874, match_id=1478914)
        with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
            m = ref.to_match()
        assert isinstance(m, Match)

    def test_to_match_passes_correct_ids(self):
        import json
        from pathlib import Path

        fixture_path = (
            Path(__file__).parent / "fixtures" / "match_1478914_next_data.json"
        )
        next_data = json.loads(fixture_path.read_text())

        ref = MatchRef(series_id=1478874, match_id=1478914)
        with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
            m = ref.to_match()
        assert m.match_id == 1478914


class TestGetRecentMatchesReturnsMatchRef(unittest.TestCase):
    def test_get_recent_matches_returns_list(self):
        """get_recent_matches returns a list (empty if the fixture has no results)."""
        import json
        from pathlib import Path

        from espncricinfo.match import Match

        fixture_path = (
            Path(__file__).parent / "fixtures" / "match_1478914_next_data.json"
        )
        next_data = json.loads(fixture_path.read_text())

        with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
            results = Match.get_recent_matches("2026-02-06")

        assert isinstance(results, list)

    def test_get_recent_matches_items_are_match_refs(self):
        """Any items returned must be MatchRef objects, not tuples."""
        import json
        from pathlib import Path

        from espncricinfo.match import Match

        fixture_path = (
            Path(__file__).parent / "fixtures" / "match_1478914_next_data.json"
        )
        next_data = json.loads(fixture_path.read_text())

        with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
            results = Match.get_recent_matches("2026-02-06")

        for r in results:
            assert isinstance(r, MatchRef)
            assert not isinstance(r, tuple)
