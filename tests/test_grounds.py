from unittest.mock import MagicMock, patch

import pytest

from espncricinfo.exceptions import NoGroundError
from espncricinfo.grounds import Ground

VENUE = {
    "id": "56293",
    "fullName": "Adelaide Oval",
    "shortName": "Adelaide Oval",
    "capacity": 50000,
    "indoor": False,
    "address": {"city": "Adelaide", "state": "", "country": "Australia"},
}


def _response(status, data=None):
    response = MagicMock(status_code=status)
    response.json.return_value = data
    return response


def test_ground_reads_core_venue_record():
    with patch(
        "espncricinfo._core.http_get", return_value=_response(200, VENUE)
    ) as get:
        ground = Ground(56293)
    assert get.call_args.args[0].endswith("/venues/56293")
    assert (ground.name, ground.city, ground.country) == (
        "Adelaide Oval",
        "Adelaide",
        "Australia",
    )
    assert (ground.capacity, ground.indoor) == (50000, False)
    assert str(ground) == "Adelaide Oval"


def test_missing_fields_become_none():
    with patch(
        "espncricinfo._core.http_get", return_value=_response(200, {"fullName": "X"})
    ):
        ground = Ground(1)
    assert (ground.city, ground.country, ground.capacity) == (None, None, None)


def test_unknown_ground_raises():
    with (
        patch("espncricinfo._core.http_get", return_value=_response(404)),
        pytest.raises(NoGroundError),
    ):
        Ground(999999999)


@pytest.mark.integration
def test_live_match_ground_matches_the_match_page():
    from espncricinfo.match import Match

    match = Match(1478914, 1478874)
    assert match.ground.name == match.ground_name == "Adelaide Oval"
    assert match.ground.country == "Australia"
