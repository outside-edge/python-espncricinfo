import unittest
from unittest.mock import patch

from espncricinfo.match_ref import MatchRef
from espncricinfo.summary import Summary


FAKE_MATCHES = [
    MatchRef(series_id=1478874, match_id=1478914),
    MatchRef(series_id=1234567, match_id=1234568),
]


class TestSummary(unittest.TestCase):

    def test_summary_matches_is_list(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertIsInstance(s.matches, list)

    def test_summary_matches_returns_match_refs(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertEqual(len(s.matches), 2)
            for ref in s.matches:
                self.assertIsInstance(ref, MatchRef)

    def test_summary_passes_date_to_get_recent_matches(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=[]) as mock_grm:
            Summary(date="2026-02-22")
            mock_grm.assert_called_once_with("2026-02-22")

    def test_summary_no_date_calls_get_recent_matches_with_none(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=[]) as mock_grm:
            Summary()
            mock_grm.assert_called_once_with(None)

    def test_summary_matches_support_tuple_unpacking(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            series_id, match_id = s.matches[0]
            self.assertEqual(series_id, 1478874)
            self.assertEqual(match_id, 1478914)
