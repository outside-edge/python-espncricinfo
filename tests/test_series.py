import unittest
from unittest.mock import MagicMock, patch

from espncricinfo.exceptions import NoSeriesError
from espncricinfo.series import Series


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    return mock


class TestSeriesNotFound(unittest.TestCase):

    def test_series_not_found_raises_no_series_error(self):
        with patch("espncricinfo.series.requests.get",
                   return_value=_mock_response(status_code=404)):
            with self.assertRaises(NoSeriesError):
                Series(9999999)


def _mock_series_response():
    """A minimal valid series JSON."""
    return _mock_response(status_code=200, json_data={
        "name": "India Women in Australia",
        "shortName": "IND-W in AUS",
        "abbreviation": "IND-W v AUS-W",
        "slug": "india-women-in-australia-2025-26",
        "isTournament": False,
        "links": [{"href": "https://www.espncricinfo.com/series/india-women-in-australia-2025-26-1478874"}],
    })


def _mock_seasons_response():
    return _mock_response(status_code=200, json_data={"items": [
        {"$ref": "http://core.espnuk.org/v2/sports/cricket/leagues/1478874/seasons/2025"}
    ]})


def _mock_events_response():
    return _mock_response(status_code=200, json_data={"items": []})


class TestSeriesHappyPath(unittest.TestCase):

    def test_series_name_populated(self):
        def side_effect(url, headers=None):
            if url.endswith("/seasons"):
                return _mock_seasons_response()
            elif url.endswith("/events"):
                return _mock_events_response()
            else:
                return _mock_series_response()

        with patch("espncricinfo.series.requests.get", side_effect=side_effect):
            s = Series(1478874)
            self.assertEqual(s.name, "India Women in Australia")
            self.assertEqual(s.short_name, "IND-W in AUS")
            self.assertFalse(s.is_tournament)
