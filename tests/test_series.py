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
