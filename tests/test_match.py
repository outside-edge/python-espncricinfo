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

    def test_match_id_is_int(self):
        self.assertEqual(self.match.match_id, 1478914)

    def test_description_is_correct(self):
        self.assertEqual(self.match.description, "IND Women v AUS Women")

    def test_description_is_string(self):
        self.assertIsInstance(self.match.description, str)

    def test_match_class_is_wt20i(self):
        self.assertEqual(self.match.match_class, "WT20I")

    def test_season_is_string(self):
        self.assertIsInstance(self.match.season, str)
        self.assertTrue(len(self.match.season) > 0)

    def test_season_value(self):
        self.assertEqual(self.match.season, "2025/26")

    def test_status_is_result(self):
        self.assertEqual(self.match.status, "result")

    def test_date_is_string(self):
        self.assertIsInstance(self.match.date, str)
        self.assertTrue(len(self.match.date) > 0)

    def test_date_format(self):
        # date should be YYYY-MM-DD
        self.assertRegex(self.match.date, r"^\d{4}-\d{2}-\d{2}$")

    def test_result_is_string(self):
        self.assertIsInstance(self.match.result, str)
        self.assertTrue(len(self.match.result) > 0)

    def test_result_contains_ind_women(self):
        self.assertIn("IND Women", self.match.result)

    # ---- series ----

    def test_series_name_is_string_or_none(self):
        self.assertTrue(
            self.match.series_name is None
            or isinstance(self.match.series_name, str)
        )

    def test_series_name_value(self):
        self.assertEqual(self.match.series_name, "India Women in Australia")

    def test_series_id_is_string(self):
        self.assertIsInstance(self.match.series_id, str)

    def test_series_id_value(self):
        self.assertEqual(self.match.series_id, "1478874")

    # ---- ground / location ----

    def test_ground_id_is_string(self):
        self.assertIsInstance(self.match.ground_id, str)
        self.assertTrue(len(self.match.ground_id) > 0)

    def test_ground_name_is_adelaide_oval(self):
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

    def test_cancelled_match_is_bool(self):
        self.assertIsInstance(self.match.cancelled_match, bool)

    def test_followon_is_false(self):
        self.assertFalse(self.match.followon)

    def test_followon_is_bool(self):
        self.assertIsInstance(self.match.followon, bool)

    def test_rain_rule_is_none(self):
        self.assertIsNone(self.match.rain_rule)

    def test_scheduled_overs_is_20(self):
        self.assertEqual(self.match.scheduled_overs, 20)

    def test_scheduled_overs_is_int_or_none(self):
        self.assertTrue(
            self.match.scheduled_overs is None
            or isinstance(self.match.scheduled_overs, int)
        )

    # ---- teams ----

    def test_team_1_is_dict(self):
        self.assertIsInstance(self.match.team_1, dict)

    def test_team_2_is_dict(self):
        self.assertIsInstance(self.match.team_2, dict)

    def test_team_1_id_is_string(self):
        self.assertIsInstance(self.match.team_1_id, str)

    def test_team_2_id_is_string(self):
        self.assertIsInstance(self.match.team_2_id, str)

    def test_team_ids_are_different(self):
        self.assertNotEqual(self.match.team_1_id, self.match.team_2_id)

    def test_team_1_abbreviation_is_string(self):
        self.assertIsInstance(self.match.team_1_abbreviation, str)
        self.assertTrue(len(self.match.team_1_abbreviation) > 0)

    def test_team_2_abbreviation_is_string(self):
        self.assertIsInstance(self.match.team_2_abbreviation, str)
        self.assertTrue(len(self.match.team_2_abbreviation) > 0)

    def test_team_1_abbreviation_value(self):
        self.assertEqual(self.match.team_1_abbreviation, "IND-W")

    def test_team_2_abbreviation_value(self):
        self.assertEqual(self.match.team_2_abbreviation, "AUS-W")

    def test_team_1_players_is_list(self):
        self.assertIsInstance(self.match.team_1_players, list)

    def test_team_2_players_is_list(self):
        self.assertIsInstance(self.match.team_2_players, list)

    def test_team_1_players_nonempty(self):
        self.assertTrue(len(self.match.team_1_players) > 0)

    def test_team_2_players_nonempty(self):
        self.assertTrue(len(self.match.team_2_players) > 0)

    # ---- toss ----

    def test_toss_winner_is_string(self):
        self.assertIsInstance(self.match.toss_winner, str)

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

    def test_batting_first_is_string(self):
        self.assertIsInstance(self.match.batting_first, str)

    def test_batting_first_value(self):
        self.assertEqual(self.match.batting_first, "IND-W")

    def test_match_winner_is_string(self):
        self.assertIsInstance(self.match.match_winner, str)

    def test_match_winner_value(self):
        self.assertEqual(self.match.match_winner, "IND-W")

    def test_home_team_is_string(self):
        self.assertIsInstance(self.match.home_team, str)

    def test_home_team_value(self):
        self.assertEqual(self.match.home_team, "AUS-W")

    # ---- innings ----

    def test_innings_is_list(self):
        self.assertIsInstance(self.match.innings, list)

    def test_innings_count_is_2(self):
        self.assertEqual(len(self.match.innings), 2)

    def test_innings_list_is_list(self):
        self.assertIsInstance(self.match.innings_list, list)

    def test_innings_list_has_2_entries(self):
        self.assertEqual(len(self.match.innings_list), 2)

    # ---- run rates ----

    def test_team_1_run_rate_is_float_or_none(self):
        rr = self.match.team_1_run_rate
        self.assertTrue(rr is None or isinstance(rr, float))

    def test_team_2_run_rate_is_float_or_none(self):
        rr = self.match.team_2_run_rate
        self.assertTrue(rr is None or isinstance(rr, float))

    def test_team_1_run_rate_positive(self):
        if self.match.team_1_run_rate is not None:
            self.assertGreater(self.match.team_1_run_rate, 0)

    def test_team_1_overs_batted_is_float_or_none(self):
        ob = self.match.team_1_overs_batted
        self.assertTrue(ob is None or isinstance(ob, float))

    # ---- URLs ----

    def test_event_url_contains_match_id(self):
        self.assertIn("1478914", self.match.event_url)

    def test_espn_api_url_contains_match_id(self):
        self.assertIn("1478914", self.match.espn_api_url)

    def test_legacy_scorecard_url_starts_with_http(self):
        self.assertTrue(self.match.legacy_scorecard_url.startswith("http"))

    def test_legacy_scorecard_url_contains_match_id(self):
        self.assertIn("1478914", self.match.legacy_scorecard_url)

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

    def test_repr_contains_Match(self):
        self.assertIn("Match", repr(self.match))

    def test_repr_contains_match_id(self):
        self.assertIn("1478914", repr(self.match))


class TestMatchScorecardMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    def test_batsmen_returns_list(self):
        result = self.match.batsmen(1)
        self.assertIsInstance(result, list)

    def test_batsmen_nonempty(self):
        result = self.match.batsmen(1)
        self.assertTrue(len(result) > 0)

    def test_batsmen_second_innings_is_list(self):
        result = self.match.batsmen(2)
        self.assertIsInstance(result, list)

    def test_bowlers_returns_list(self):
        result = self.match.bowlers(1)
        self.assertIsInstance(result, list)

    def test_bowlers_nonempty(self):
        result = self.match.bowlers(1)
        self.assertTrue(len(result) > 0)

    def test_bowlers_second_innings_is_list(self):
        result = self.match.bowlers(2)
        self.assertIsInstance(result, list)

    def test_extras_returns_dict(self):
        result = self.match.extras(1)
        self.assertIsInstance(result, dict)

    def test_extras_has_required_keys(self):
        result = self.match.extras(1)
        for key in ("extras", "byes", "legbyes", "wides", "noballs"):
            self.assertIn(key, result)

    def test_extras_values_are_numeric_or_none(self):
        result = self.match.extras(1)
        for key, val in result.items():
            self.assertTrue(
                val is None or isinstance(val, (int, float)),
                f"Key '{key}' has unexpected type {type(val)}",
            )

    def test_extras_wides_value(self):
        result = self.match.extras(1)
        self.assertEqual(result["wides"], 5)

    def test_extras_byes_value(self):
        result = self.match.extras(1)
        self.assertEqual(result["byes"], 0)

    def test_extras_total_value(self):
        result = self.match.extras(1)
        self.assertEqual(result["extras"], 6)

    def test_fows_returns_list(self):
        result = self.match.fows(1)
        self.assertIsInstance(result, list)

    def test_fows_nonempty_for_completed_innings(self):
        result = self.match.fows(1)
        self.assertTrue(len(result) > 0)

    def test_fows_second_innings_is_list(self):
        result = self.match.fows(2)
        self.assertIsInstance(result, list)

    def test_batsmen_invalid_innings_returns_none_or_list(self):
        result = self.match.batsmen(99)
        self.assertTrue(result is None or isinstance(result, list))

    def test_bowlers_invalid_innings_returns_none_or_list(self):
        result = self.match.bowlers(99)
        self.assertTrue(result is None or isinstance(result, list))


class TestMatchExceptions(unittest.TestCase):

    def test_match_not_found_error_raised_on_404(self):
        from espncricinfo.exceptions import MatchNotFoundError

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
