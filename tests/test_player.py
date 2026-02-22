import json
import unittest
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.player import Player

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load(name):
    with open(FIXTURE_DIR / name) as f:
        return json.load(f) if name.endswith(".json") else f.read()


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
    new_json = _load("player_253802_new.json")

    def side_effect(url, headers=None):
        if "hs-consumer-api" in url:
            return _mock_response(json_data=new_json)
        elif "espnuk.org" in url:
            return _mock_response(json_data=json_data)
        else:
            return _mock_response(text="<html><body></body></html>")

    with patch("espncricinfo.player.requests.get", side_effect=side_effect):
        return Player(253802)


class TestPlayerAttributes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.player = _make_player()

    def test_cricinfo_id_is_string(self):
        self.assertEqual(self.player.cricinfo_id, "253802")

    def test_name_is_nonempty_string(self):
        self.assertIsInstance(self.player.name, str)
        self.assertTrue(len(self.player.name) > 0)

    def test_first_name_is_string(self):
        self.assertIsInstance(self.player.first_name, str)

    def test_full_name_is_nonempty_string(self):
        self.assertIsInstance(self.player.full_name, str)
        self.assertTrue(len(self.player.full_name) > 0)

    def test_date_of_birth_is_set(self):
        self.assertIsNotNone(self.player.date_of_birth)
        self.assertTrue(len(str(self.player.date_of_birth)) > 0)

    def test_current_age_is_set(self):
        self.assertIsNotNone(self.player.current_age)

    def test_playing_role_is_string_or_none(self):
        role = self.player.playing_role
        self.assertTrue(role is None or isinstance(role, (str, dict)))

    def test_batting_style_is_dict_or_none(self):
        style = self.player.batting_style
        self.assertTrue(style is None or isinstance(style, dict))

    def test_bowling_style_is_dict_or_none(self):
        style = self.player.bowling_style
        self.assertTrue(style is None or isinstance(style, dict))

    def test_major_teams_is_nonempty_list(self):
        self.assertIsInstance(self.player.major_teams, list)
        self.assertTrue(len(self.player.major_teams) > 0)

    def test_major_teams_are_strings(self):
        for team in self.player.major_teams:
            self.assertIsInstance(team, str)


class TestPlayerErrors(unittest.TestCase):

    def test_404_raises_player_not_found(self):
        mock_404 = _mock_response(status_code=404)
        with patch("espncricinfo.player.requests.get", return_value=mock_404):
            with self.assertRaises(PlayerNotFoundError):
                Player(999999)


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


class TestPlayerDeprecatedMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.player = _make_player()

    def test_in_team_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.in_team_for_match(1478914, 1478874)

    def test_batting_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.batting_for_match(1478914, 1478874)

    def test_bowling_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.bowling_for_match(1478914, 1478874)

    def test_in_team_for_match_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                self.player.in_team_for_match(1478914, 1478874)
            except NotImplementedError:
                pass
            self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))
