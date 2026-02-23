import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError
from espncricinfo.match import Match, _normalise

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _make_match():
    next_data = json.load(open(FIXTURE_DIR / "match_1478914_next_data.json"))
    with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
        return Match(1478914, 1478874)


class TestMatchAttributes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    # ---- identity / core ----

    def test_match_id(self):
        self.assertEqual(self.match.match_id, 1478914)

    def test_description(self):
        self.assertEqual(self.match.description, "IND Women v AUS Women")

    def test_match_class(self):
        self.assertEqual(self.match.match_class, "WT20I")

    def test_season(self):
        self.assertEqual(self.match.season, "2025/26")

    def test_status(self):
        self.assertEqual(self.match.status, "result")

    def test_date_format(self):
        # date should be non-empty YYYY-MM-DD
        self.assertRegex(self.match.date, r"^\d{4}-\d{2}-\d{2}$")

    def test_result(self):
        self.assertIn("IND Women", self.match.result)

    # ---- series ----

    def test_series_name(self):
        self.assertEqual(self.match.series_name, "India Women in Australia")

    def test_series_id(self):
        self.assertEqual(self.match.series_id, "1478874")

    # ---- ground / location ----

    def test_ground_id_is_nonempty_string(self):
        self.assertIsInstance(self.match.ground_id, str)
        self.assertTrue(len(self.match.ground_id) > 0)

    def test_ground_name(self):
        self.assertEqual(self.match.ground_name, "Adelaide Oval")

    def test_continent_is_none(self):
        self.assertIsNone(self.match.continent)

    def test_town_name_is_string_or_none(self):
        self.assertTrue(
            self.match.town_name is None
            or isinstance(self.match.town_name, str)
        )

    # ---- match flags ----

    def test_cancelled_match_is_false(self):
        self.assertFalse(self.match.cancelled_match)

    def test_followon_is_false(self):
        self.assertFalse(self.match.followon)

    def test_rain_rule_is_none(self):
        self.assertIsNone(self.match.rain_rule)

    def test_scheduled_overs(self):
        self.assertEqual(self.match.scheduled_overs, 20)

    # ---- teams ----

    def test_team_1_is_dict(self):
        self.assertIsInstance(self.match.team_1, dict)

    def test_team_2_is_dict(self):
        self.assertIsInstance(self.match.team_2, dict)

    def test_team_ids_are_different_strings(self):
        self.assertIsInstance(self.match.team_1_id, str)
        self.assertIsInstance(self.match.team_2_id, str)
        self.assertNotEqual(self.match.team_1_id, self.match.team_2_id)

    def test_team_abbreviations(self):
        self.assertEqual(self.match.team_1_abbreviation, "IND-W")
        self.assertEqual(self.match.team_2_abbreviation, "AUS-W")

    def test_team_players_nonempty(self):
        self.assertGreater(len(self.match.team_1_players), 0)
        self.assertGreater(len(self.match.team_2_players), 0)

    # ---- toss ----

    def test_toss_winner_is_valid_team_id(self):
        self.assertIn(
            self.match.toss_winner,
            [self.match.team_1_id, self.match.team_2_id],
        )

    def test_toss_decision_is_1_or_2(self):
        self.assertIn(self.match.toss_decision, ["1", "2"])

    def test_toss_decision_name_is_bat_or_bowl(self):
        self.assertIn(self.match.toss_decision_name, ["bat", "bowl"])

    def test_toss_winner_team_id_is_string(self):
        self.assertIsInstance(self.match.toss_winner_team_id, str)

    # ---- result / outcome ----

    def test_batting_first(self):
        self.assertEqual(self.match.batting_first, "IND-W")

    def test_match_winner(self):
        self.assertEqual(self.match.match_winner, "IND-W")

    def test_home_team(self):
        self.assertEqual(self.match.home_team, "AUS-W")

    # ---- innings ----

    def test_innings_count(self):
        self.assertIsInstance(self.match.innings, list)
        self.assertEqual(len(self.match.innings), 2)

    def test_innings_list_count(self):
        self.assertIsInstance(self.match.innings_list, list)
        self.assertEqual(len(self.match.innings_list), 2)

    # ---- run rates ----

    def test_team_1_run_rate_positive(self):
        rr = self.match.team_1_run_rate
        self.assertIsNotNone(rr)
        self.assertGreater(rr, 0)

    def test_team_2_run_rate_positive(self):
        rr = self.match.team_2_run_rate
        self.assertIsNotNone(rr)
        self.assertGreater(rr, 0)

    def test_team_1_overs_batted_positive(self):
        ob = self.match.team_1_overs_batted
        self.assertIsNotNone(ob)
        self.assertGreater(ob, 0)

    # ---- URLs ----

    def test_event_url_contains_match_id(self):
        self.assertIn("1478914", self.match.event_url)

    def test_espn_api_url_contains_match_id(self):
        self.assertIn("1478914", self.match.espn_api_url)

    def test_legacy_scorecard_url(self):
        url = self.match.legacy_scorecard_url
        self.assertTrue(url.startswith("http"))
        self.assertIn("1478914", url)

    def test_details_url_contains_match_id(self):
        self.assertIn("1478914", self.match.details_url)

    # ---- officials / rosters ----

    def test_officials_is_list(self):
        self.assertIsInstance(self.match.officials, list)

    def test_rosters_is_dict_or_none(self):
        self.assertTrue(
            self.match.rosters is None
            or isinstance(self.match.rosters, dict)
        )

    def test_all_innings_is_list(self):
        self.assertIsInstance(self.match.all_innings, list)

    # ---- dunder methods ----

    def test_str_is_nonempty(self):
        self.assertTrue(len(str(self.match)) > 0)

    def test_repr(self):
        r = repr(self.match)
        self.assertIn("Match", r)
        self.assertIn("1478914", r)


class TestMatchScorecardMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    def test_batsmen_nonempty(self):
        self.assertGreater(len(self.match.batsmen(1)), 0)

    def test_batsmen_second_innings_is_list(self):
        self.assertIsInstance(self.match.batsmen(2), list)

    def test_bowlers_nonempty(self):
        self.assertGreater(len(self.match.bowlers(1)), 0)

    def test_bowlers_second_innings_is_list(self):
        self.assertIsInstance(self.match.bowlers(2), list)

    def test_extras_has_required_keys(self):
        result = self.match.extras(1)
        for key in ("extras", "byes", "legbyes", "wides", "noballs"):
            self.assertIn(key, result)

    def test_extras_values(self):
        result = self.match.extras(1)
        self.assertEqual(result["wides"], 5)
        self.assertEqual(result["byes"], 0)
        self.assertEqual(result["extras"], 6)

    def test_fows_nonempty_for_completed_innings(self):
        result = self.match.fows(1)
        self.assertGreater(len(result), 0)

    def test_fows_second_innings_is_list(self):
        self.assertIsInstance(self.match.fows(2), list)

    def test_batsmen_invalid_innings_returns_none(self):
        # out-of-range innings should not raise, just return None
        self.assertIsNone(self.match.batsmen(99))

    def test_bowlers_invalid_innings_returns_none(self):
        self.assertIsNone(self.match.bowlers(99))


class TestMatchExceptions(unittest.TestCase):

    def test_match_not_found_error_raised_on_404(self):
        with patch(
            "espncricinfo.match._playwright_fetch",
            side_effect=MatchNotFoundError("Match not found"),
        ):
            with self.assertRaises(MatchNotFoundError):
                Match(9999999, 9999999)

    def test_no_scorecard_error_on_bad_structure(self):
        bad_next_data = {"props": {"appPageProps": {"data": {}}}}
        with patch(
            "espncricinfo.match._playwright_fetch",
            return_value=bad_next_data,
        ):
            with self.assertRaises(NoScorecardError):
                Match(1478914, 1478874)


class TestMatchIntegration:

    @pytest.mark.integration
    def test_live_description_is_string(self):
        m = Match(1478914, 1478874)
        assert isinstance(m.description, str)
        assert len(m.description) > 0

    @pytest.mark.integration
    def test_live_match_class(self):
        m = Match(1478914, 1478874)
        assert isinstance(m.match_class, str)
        assert len(m.match_class) > 0

    @pytest.mark.integration
    def test_live_status_is_result(self):
        m = Match(1478914, 1478874)
        assert m.status == "result"

    @pytest.mark.integration
    def test_live_innings_count(self):
        m = Match(1478914, 1478874)
        assert isinstance(m.innings, list)
        assert len(m.innings) == 2

    @pytest.mark.integration
    def test_live_ground_name(self):
        m = Match(1478914, 1478874)
        assert m.ground_name == "Adelaide Oval"


class TestMatchScorecardProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    # ---- batting_scorecard ----

    def test_batting_scorecard_is_list_of_2_innings(self):
        sc = self.match.batting_scorecard
        self.assertIsInstance(sc, list)
        self.assertEqual(len(sc), 2)

    def test_batting_scorecard_innings_are_nonempty_lists(self):
        for innings in self.match.batting_scorecard:
            self.assertIsInstance(innings, list)
            self.assertGreater(len(innings), 0)

    def test_batting_scorecard_entry_has_required_keys(self):
        entry = self.match.batting_scorecard[0][0]
        for key in ("name", "full_name", "player_id", "runs", "balls",
                    "minutes", "fours", "sixes", "strike_rate",
                    "is_out", "dismissal", "batted"):
            self.assertIn(key, entry)

    def test_batting_scorecard_first_batsman_values(self):
        # Smriti Mandhana: 82 runs, 55 balls, out caught Gardner b Sutherland
        entry = self.match.batting_scorecard[0][0]
        self.assertEqual(entry["runs"], 82)
        self.assertEqual(entry["balls"], 55)
        self.assertTrue(entry["is_out"])
        self.assertIn("Gardner", entry["dismissal"])
        self.assertTrue(entry["batted"])
        self.assertIsInstance(entry["player_id"], int)

    def test_batting_scorecard_strike_rate_is_float(self):
        entry = self.match.batting_scorecard[0][0]
        self.assertIsInstance(entry["strike_rate"], float)
