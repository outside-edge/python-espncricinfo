import datetime as dt
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError
from espncricinfo.match import Match

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _make_match():
    next_data = json.loads((FIXTURE_DIR / "match_1478914_next_data.json").read_text())
    with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
        return Match(1478914, 1478874)


class TestMatchAttributes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    # ---- identity / core ----

    def test_match_id(self):
        assert self.match.match_id == 1478914

    def test_description(self):
        assert self.match.description == "IND Women v AUS Women"

    def test_match_class(self):
        assert self.match.match_class == "WT20I"

    def test_season(self):
        assert self.match.season == "2025/26"

    def test_status(self):
        assert self.match.status == "result"

    def test_date_format(self):
        # date should be non-empty YYYY-MM-DD
        assert re.search(r"^\d{4}-\d{2}-\d{2}$", self.match.date)

    def test_result(self):
        assert "IND Women" in self.match.result

    # ---- series ----

    def test_series_name(self):
        assert self.match.series_name == "India Women in Australia"

    def test_series_id(self):
        assert self.match.series_id == 1478874

    # ---- ground / location ----

    def test_ground_id_is_nonempty_string(self):
        assert isinstance(self.match.ground_id, str)
        assert len(self.match.ground_id) > 0

    def test_ground_name(self):
        assert self.match.ground_name == "Adelaide Oval"

    def test_town_name_is_string_or_none(self):
        assert self.match.town_name is None or isinstance(self.match.town_name, str)

    # ---- match flags ----

    def test_not_canceled(self):
        assert self.match.canceled is False

    def test_scheduled_overs(self):
        assert self.match.scheduled_overs == 20

    # ---- teams ----

    def test_team_1_is_dict(self):
        assert isinstance(self.match.team_1, dict)

    def test_team_2_is_dict(self):
        assert isinstance(self.match.team_2, dict)

    def test_team_ids_are_different_strings(self):
        assert isinstance(self.match.team_1_id, str)
        assert isinstance(self.match.team_2_id, str)
        assert self.match.team_1_id != self.match.team_2_id

    def test_team_abbreviations(self):
        assert self.match.team_1_abbreviation == "IND-W"
        assert self.match.team_2_abbreviation == "AUS-W"

    def test_team_players_nonempty(self):
        assert len(self.match.team_1_players) > 0
        assert len(self.match.team_2_players) > 0

    # ---- toss ----

    def test_toss_winner_is_valid_team_id(self):
        assert self.match.toss_winner in [self.match.team_1_id, self.match.team_2_id]

    def test_toss_decision_name_is_bat_or_bowl(self):
        assert self.match.toss_decision_name in ["bat", "bowl"]

    def test_toss_winner_is_a_team_id(self):
        assert self.match.toss_winner in {self.match.team_1_id, self.match.team_2_id}

    # ---- result / outcome ----

    def test_batting_first(self):
        assert self.match.batting_first == "IND-W"

    def test_match_winner(self):
        assert self.match.match_winner == "IND-W"

    def test_home_team(self):
        assert self.match.home_team == "AUS-W"

    # ---- innings ----

    def test_innings_count(self):
        assert isinstance(self.match.innings, list)
        assert len(self.match.innings) == 2

    def test_innings_list_count(self):
        assert isinstance(self.match.innings_list, list)
        assert len(self.match.innings_list) == 2

    # ---- run rates ----

    def test_team_1_run_rate_positive(self):
        rr = self.match.team_1_run_rate
        assert rr is not None
        assert rr > 0

    def test_team_2_run_rate_positive(self):
        rr = self.match.team_2_run_rate
        assert rr is not None
        assert rr > 0

    def test_team_1_overs_batted_positive(self):
        ob = self.match.team_1_overs_batted
        assert ob is not None
        assert ob > 0

    # ---- URLs ----

    def test_event_url_contains_match_id(self):
        assert "1478914" in self.match.event_url

    def test_espn_api_url_contains_match_id(self):
        assert "1478914" in self.match.espn_api_url

    def test_details_url_contains_match_id(self):
        assert "1478914" in self.match.details_url

    # ---- officials / rosters ----

    def test_rosters_is_dict_or_none(self):
        assert self.match.rosters is None or isinstance(self.match.rosters, dict)

    def test_all_innings_is_list(self):
        assert isinstance(self.match.all_innings, list)

    # ---- dunder methods ----

    def test_str_is_nonempty(self):
        assert len(str(self.match)) > 0

    def test_repr(self):
        r = repr(self.match)
        assert "Match" in r
        assert "1478914" in r


class TestMatchScorecardMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    def test_batsmen_nonempty(self):
        assert len(self.match.batsmen(1)) > 0

    def test_batsmen_second_innings_is_list(self):
        assert isinstance(self.match.batsmen(2), list)

    def test_bowlers_nonempty(self):
        assert len(self.match.bowlers(1)) > 0

    def test_bowlers_second_innings_is_list(self):
        assert isinstance(self.match.bowlers(2), list)

    def test_extras_has_required_keys(self):
        result = self.match.extras(1)
        for key in ("extras", "byes", "legbyes", "wides", "noballs"):
            assert key in result

    def test_extras_values(self):
        result = self.match.extras(1)
        assert result["wides"] == 5
        assert result["byes"] == 0
        assert result["extras"] == 6

    def test_fows_nonempty_for_completed_innings(self):
        result = self.match.fows(1)
        assert len(result) > 0

    def test_fows_second_innings_is_list(self):
        assert isinstance(self.match.fows(2), list)

    def test_batsmen_invalid_innings_returns_none(self):
        # out-of-range innings should not raise, just return None
        assert self.match.batsmen(99) is None

    def test_bowlers_invalid_innings_returns_none(self):
        assert self.match.bowlers(99) is None


class TestMatchExceptions(unittest.TestCase):
    def test_match_not_found_error_raised_on_404(self):
        with (
            patch(
                "espncricinfo.match._playwright_fetch",
                side_effect=MatchNotFoundError("Match not found"),
            ),
            pytest.raises(MatchNotFoundError),
        ):
            Match(9999999, 9999999)

    def test_no_scorecard_error_on_bad_structure(self):
        bad_next_data = {"props": {"appPageProps": {"data": {}}}}
        with (
            patch(
                "espncricinfo.match._playwright_fetch",
                return_value=bad_next_data,
            ),
            pytest.raises(NoScorecardError),
        ):
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
        assert isinstance(sc, list)
        assert len(sc) == 2

    def test_batting_scorecard_innings_are_nonempty_lists(self):
        for innings in self.match.batting_scorecard:
            assert isinstance(innings, list)
            assert len(innings) > 0

    def test_batting_scorecard_entry_has_required_keys(self):
        entry = self.match.batting_scorecard[0][0]
        for key in (
            "name",
            "full_name",
            "player_id",
            "runs",
            "balls",
            "minutes",
            "fours",
            "sixes",
            "strike_rate",
            "is_out",
            "dismissal",
            "batted",
        ):
            assert key in entry

    def test_batting_scorecard_first_batsman_values(self):
        # Smriti Mandhana: 82 runs, 55 balls, out caught Gardner b Sutherland
        entry = self.match.batting_scorecard[0][0]
        assert entry["runs"] == 82
        assert entry["balls"] == 55
        assert entry["is_out"]
        assert "Gardner" in entry["dismissal"]
        assert entry["batted"]
        assert isinstance(entry["player_id"], int)

    def test_batting_scorecard_strike_rate_is_float(self):
        # batting_scorecard[0][4] is Harmanpreet Kaur whose strikerate is
        # returned by the ESPN API as integer 50; verify it is coerced to float.
        entry = self.match.batting_scorecard[0][4]
        assert isinstance(entry["strike_rate"], float)

    def test_batting_scorecard_empty_innings_returns_empty_list(self):
        from unittest.mock import patch

        # Patch batsmen to return None for innings 2
        original_batsmen = self.match.batsmen

        def patched_batsmen(i):
            if i == 2:
                return None
            return original_batsmen(i)

        with patch.object(self.match, "batsmen", side_effect=patched_batsmen):
            sc = self.match.batting_scorecard
        assert sc[1] == []

    # ---- bowling_scorecard ----

    def test_bowling_scorecard_is_list_of_2_innings(self):
        sc = self.match.bowling_scorecard
        assert isinstance(sc, list)
        assert len(sc) == 2

    def test_bowling_scorecard_innings_are_nonempty_lists(self):
        for innings in self.match.bowling_scorecard:
            assert isinstance(innings, list)
            assert len(innings) > 0

    def test_bowling_scorecard_entry_has_required_keys(self):
        entry = self.match.bowling_scorecard[0][0]
        for key in (
            "name",
            "full_name",
            "player_id",
            "overs",
            "maidens",
            "runs",
            "wickets",
            "economy",
            "wides",
            "no_balls",
            "dots",
        ):
            assert key in entry

    def test_bowling_scorecard_first_bowler_values(self):
        # Darcie Brown bowled first innings
        entry = self.match.bowling_scorecard[0][0]
        assert entry["name"] == "D Brown"
        assert isinstance(entry["wickets"], int)
        assert isinstance(entry["overs"], float)

    def test_bowling_scorecard_economy_is_float_or_none(self):
        entry = self.match.bowling_scorecard[0][0]
        assert entry["economy"] is None or isinstance(entry["economy"], float)

    def test_bowling_scorecard_empty_innings_returns_empty_list(self):
        original_bowlers = self.match.bowlers

        def patched_bowlers(i):
            if i == 2:
                return None
            return original_bowlers(i)

        with patch.object(self.match, "bowlers", side_effect=patched_bowlers):
            sc = self.match.bowling_scorecard
        assert sc[1] == []


class TestGetRecentMatchesUrl:
    @pytest.mark.parametrize(
        "date_arg", ["2026-10-20", "20-10-2026", dt.date(2026, 10, 20)]
    )
    def test_date_sent_as_dd_mm_yyyy(self, date_arg):
        with patch("espncricinfo.match._playwright_fetch", return_value={}) as fetch:
            Match.get_recent_matches(date_arg)
        fetch.assert_called_once_with(
            "https://www.espncricinfo.com/live-cricket-match-results?date=20-10-2026"
        )

    @pytest.mark.integration
    def test_live_dated_results_are_not_empty(self):
        assert Match.get_recent_matches("2026-10-20")


def _next_data_with(**match_fields):
    """The recorded match page with some ``match`` fields overridden."""
    next_data = json.loads((FIXTURE_DIR / "match_1478914_next_data.json").read_text())
    app = next_data["props"]["appPageProps"]["data"]
    data = app if "match" in app else app["data"]
    data["match"].update(match_fields)
    return next_data


def _match_from(next_data):
    with patch("espncricinfo.match._playwright_fetch", return_value=next_data):
        return Match(1478914, 1478874)


def test_no_winner_is_none_not_team_2():
    match = _match_from(_next_data_with(winnerTeamId=None))
    assert match.match_winner is None


def test_no_toss_leaves_toss_fields_none():
    match = _match_from(_next_data_with(tossWinnerTeamId=None, tossWinnerChoice=None))
    assert match.toss_winner is None
    assert match.toss_decision_name is None


def test_series_id_is_int():
    assert isinstance(_make_match().series_id, int)


def test_fetch_works_inside_a_running_event_loop():
    """Jupyter runs an event loop; asyncio.run() refuses to nest inside it (#55)."""
    import asyncio

    import espncricinfo.match as match_module

    async def fake_fetch(url):
        return {"url": url}

    async def notebook_cell():
        return match_module._playwright_fetch("https://example.invalid/page")

    with patch.object(match_module, "_async_playwright_fetch", fake_fetch):
        assert asyncio.run(notebook_cell()) == {"url": "https://example.invalid/page"}


def test_match_without_series_id_uses_legacy_url_and_reads_series_from_page():
    next_data = json.loads((FIXTURE_DIR / "match_1478914_next_data.json").read_text())
    with patch("espncricinfo.match._playwright_fetch", return_value=next_data) as fetch:
        match = Match(1478914)
    fetch.assert_called_once_with(
        "https://www.espncricinfo.com/matches/engine/match/1478914.html"
    )
    assert match.series_id == 1478874


@pytest.mark.integration
def test_live_match_from_id_alone():
    """#50: match 729303 (IPL 2014) loads without knowing its series."""
    match = Match(729303)
    assert match.series_id == 695871
    assert match.batting_scorecard[0]


def test_innings_fours_and_sixes_match_espn_totals():
    match = _make_match()
    first = match.innings[0]
    assert (first["fours"], first["sixes"]) == (15, 4)
    for inn in match.innings:
        batters = inn["inningBatsmen"]
        assert inn["fours"] == sum(b["fours"] or 0 for b in batters)
        assert inn["sixes"] == sum(b["sixes"] or 0 for b in batters)


def test_boundary_count_falls_back_to_batters_then_none():
    from espncricinfo.match import _boundary_count

    assert _boundary_count({"fours": 9, "inningBatsmen": []}, "fours") == 9
    batted = {"battedType": "yes"}
    batters = [{**batted, "fours": 2}, {**batted, "fours": 5}]
    did_not_bat = {"battedType": "DNB", "fours": None}
    assert _boundary_count({"inningBatsmen": [*batters, did_not_bat]}, "fours") == 7
    assert (
        _boundary_count({"inningBatsmen": [{**batted, "fours": None}]}, "fours") is None
    )
    assert _boundary_count({"inningBatsmen": []}, "fours") is None


def test_over_by_over_adds_up_to_innings_totals():
    match = _make_match()
    assert [len(overs) for overs in match.over_by_over] == [20, 20]
    for overs, inn in zip(match.over_by_over, match.innings, strict=True):
        assert sum(o["runs"] for o in overs) == inn["runs"]
        assert sum(o["wickets"] for o in overs) == inn["wickets"]
        assert overs[-1]["total_runs"] == inn["runs"]
        assert [o["over"] for o in overs] == list(range(1, 21))


@pytest.mark.integration
def test_live_old_test_has_no_over_data_and_no_invented_boundaries():
    match = Match(63963, 61791)
    assert all(overs == [] for overs in match.over_by_over)
    assert all(inn["fours"] is None or inn["fours"] >= 0 for inn in match.innings)


def _results_page_with(*matches):
    items = [
        {
            "objectId": mid,
            "series": {"objectId": 1},
            "startDate": f"{start}T00:00:00.000Z",
            "endDate": f"{end}T00:00:00.000Z",
        }
        for mid, start, end in matches
    ]
    return {
        "props": {"appPageProps": {"data": {"data": {"content": {"matches": items}}}}}
    }


def test_get_matches_on_keeps_matches_spanning_the_day():
    page = _results_page_with(
        (10, "2026-10-20", "2026-10-20"),  # one-day match on the day
        (11, "2026-10-19", "2026-10-22"),  # Test in progress
        (12, "2026-10-19", "2026-10-19"),  # finished the day before
        (13, "2026-10-21", "2026-10-21"),  # next day
    )
    with patch("espncricinfo.match._playwright_fetch", return_value=page) as fetch:
        refs = Match.get_matches_on("2026-10-20")
    assert [r.match_id for r in refs] == [10, 11]
    assert fetch.call_args.args[0].endswith("?date=20-10-2026")


def test_get_recent_matches_still_returns_every_listed_match():
    page = _results_page_with(
        (10, "2026-10-20", "2026-10-20"), (12, "2026-10-19", "2026-10-19")
    )
    with patch("espncricinfo.match._playwright_fetch", return_value=page):
        assert [r.match_id for r in Match.get_recent_matches("2026-10-20")] == [10, 12]


@pytest.mark.integration
def test_live_matches_on_a_day_are_a_subset_of_recent_matches():
    on_day = Match.get_matches_on("2026-10-20")
    recent = Match.get_recent_matches("2026-10-20")
    assert on_day
    assert set(on_day) < set(recent)
