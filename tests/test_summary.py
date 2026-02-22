import unittest
from unittest.mock import patch

from espncricinfo.summary import Summary


FAKE_MATCHES = [
    (1478874, 1478914),
    (1234567, 1234568),
]


class TestSummary(unittest.TestCase):

    def test_summary_matches_is_list(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertIsInstance(s.matches, list)

    def test_summary_matches_returns_tuples(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertEqual(s.matches, FAKE_MATCHES)

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
