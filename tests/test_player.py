import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from requests import HTTPError, Response

from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.player import Player

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load(name):
    text = (FIXTURE_DIR / name).read_text()
    return json.loads(text) if name.endswith(".json") else text


def _mock_response(json_data=None, text=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
        mock.text = json.dumps(json_data)
    else:
        mock.text = text or ""
        mock.json.side_effect = ValueError("No JSON")
    return mock


def _make_player():
    json_data = _load("player_253802.json")

    def side_effect(url, headers=None, timeout=None):
        if "/athletes/" in url:
            return _mock_response(json_data=json_data)
        if "/teams/" in url:
            return _mock_response(json_data={"name": f"Team {url.rsplit('/', 1)[-1]}"})
        raise AssertionError(f"Unexpected request: {url}")

    with patch("espncricinfo._core.http_get", side_effect=side_effect):
        player = Player(253802)
        _ = player.major_teams
        return player


class TestPlayerAttributes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = _make_player()

    def test_cricinfo_id_is_string(self):
        assert self.player.cricinfo_id == "253802"

    def test_name_is_nonempty_string(self):
        assert isinstance(self.player.name, str)
        assert len(self.player.name) > 0

    def test_first_name_is_string(self):
        assert isinstance(self.player.first_name, str)

    def test_full_name_is_nonempty_string(self):
        assert isinstance(self.player.full_name, str)
        assert len(self.player.full_name) > 0

    def test_date_of_birth_is_set(self):
        assert self.player.date_of_birth is not None
        assert len(str(self.player.date_of_birth)) > 0

    def test_current_age_is_set(self):
        assert self.player.current_age is not None

    def test_playing_role_is_string_or_none(self):
        role = self.player.playing_role
        assert role is None or isinstance(role, (str, dict))

    def test_batting_style_is_dict_or_none(self):
        style = self.player.batting_style
        assert style is None or isinstance(style, dict)

    def test_bowling_style_is_dict_or_none(self):
        style = self.player.bowling_style
        assert style is None or isinstance(style, dict)

    def test_major_teams_is_nonempty_list(self):
        assert isinstance(self.player.major_teams, list)
        assert len(self.player.major_teams) > 0

    def test_major_teams_are_strings(self):
        for team in self.player.major_teams:
            assert isinstance(team, str)

    def test_major_teams_resolve_core_references_once(self):
        player_data = _load("player_253802.json")
        player_data["majorTeams"] = [
            {"$ref": "http://core.espnuk.org/v2/sports/cricket/teams/6"},
            {"$ref": "http://core.espnuk.org/v2/sports/cricket/teams/1668"},
        ]
        responses = [
            _mock_response(json_data=player_data),
            _mock_response(json_data={"displayName": "India"}),
            _mock_response(json_data={"name": "Delhi"}),
        ]
        with patch("espncricinfo._core.http_get", side_effect=responses) as get:
            player = Player(253802)
            assert get.call_count == 1
            assert player.major_teams == ["India", "Delhi"]
            assert player.major_teams == ["India", "Delhi"]
            assert get.call_count == 3


class TestPlayerErrors(unittest.TestCase):
    def test_404_raises_player_not_found(self):
        mock_404 = _mock_response(status_code=404)
        with (
            patch("espncricinfo._core.http_get", return_value=mock_404),
            pytest.raises(PlayerNotFoundError),
        ):
            Player(999999)

    def test_non_404_http_error_is_not_decoded_as_json(self):
        denied = Response()
        denied.status_code = 403
        denied._content = b"<html>Access Denied</html>"
        with (
            patch("espncricinfo._core.http_get", return_value=denied),
            pytest.raises(HTTPError),
        ):
            Player(253802)


class TestPlayerIntegration:
    @pytest.mark.integration
    def test_live_name(self):
        player = Player(253802)
        assert isinstance(player.name, str)
        assert len(player.name) > 0

    @pytest.mark.integration
    def test_live_full_name(self):
        player = Player(253802)
        assert isinstance(player.full_name, str)
        assert len(player.full_name) > 0

    @pytest.mark.integration
    def test_live_dob(self):
        player = Player(253802)
        assert player.date_of_birth is not None

    @pytest.mark.integration
    def test_live_major_teams(self):
        player = Player(253802)
        assert isinstance(player.major_teams, list)
        assert len(player.major_teams) > 0

    @pytest.mark.integration
    def test_live_cricinfo_id(self):
        player = Player(253802)
        assert player.cricinfo_id == "253802"


def test_get_data_sends_headers_and_writes_rows(tmp_path):
    player = _make_player()
    # ESPN's stats pages put each cell on its own line; get_data splits on that.
    rows = (
        "<tr>\n<td>Runs</td>\n<td>Ground</td>\n</tr>"
        "<tr>\n<td>61</td>\n<td>Manchester</td>\n</tr>"
    )
    page = "<table></table>" * 3 + f"<table>{rows}</table>"
    out = tmp_path / "data.csv"
    with patch(
        "espncricinfo._core.http_get", return_value=_mock_response(text=page)
    ) as get:
        player.get_data(file_name=str(out))
    assert get.call_args.kwargs["headers"] == player.headers
    assert out.read_text().splitlines() == [",Runs,Ground", ",61,Manchester"]
