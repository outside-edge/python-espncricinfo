import unittest
from unittest.mock import MagicMock, patch

import pytest

from espncricinfo.exceptions import (
    MatchNotFoundError,
    NoScorecardError,
    PlayerNotFoundError,
)
from espncricinfo.match import Match
from espncricinfo.player import Player


def _mock_player_response(status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = "<html><body></body></html>"
    mock.json.side_effect = ValueError("No JSON")
    return mock


class TestExceptionInheritance(unittest.TestCase):
    def test_match_not_found_is_type_error_subclass(self):
        assert issubclass(MatchNotFoundError, TypeError)

    def test_no_scorecard_is_type_error_subclass(self):
        assert issubclass(NoScorecardError, TypeError)

    def test_player_not_found_is_type_error_subclass(self):
        assert issubclass(PlayerNotFoundError, TypeError)


class TestMatchExceptions(unittest.TestCase):
    def test_match_not_found(self):
        with (
            patch(
                "espncricinfo.match._playwright_fetch",
                side_effect=MatchNotFoundError("not found"),
            ),
            pytest.raises(MatchNotFoundError),
        ):
            Match(1, 1)

    def test_no_scorecard(self):
        with (
            patch(
                "espncricinfo.match._playwright_fetch",
                side_effect=NoScorecardError("no scorecard"),
            ),
            pytest.raises(NoScorecardError),
        ):
            Match(2, 2)

    def test_match_not_found_is_type_error_subclass(self):
        assert issubclass(MatchNotFoundError, TypeError)

    def test_no_scorecard_is_type_error_subclass(self):
        assert issubclass(NoScorecardError, TypeError)


class TestPlayerExceptions(unittest.TestCase):
    def test_player_not_found(self):
        mock_404 = _mock_player_response(status_code=404)
        with (
            patch("espncricinfo._core.http_get", return_value=mock_404),
            pytest.raises(PlayerNotFoundError),
        ):
            Player(999999)

    def test_player_not_found_is_type_error_subclass(self):
        assert issubclass(PlayerNotFoundError, TypeError)
