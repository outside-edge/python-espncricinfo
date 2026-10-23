from unittest.mock import MagicMock, patch

import pytest

from espncricinfo._core import reference_ids
from espncricinfo.exceptions import NoSeasonError, NoTeamError
from espncricinfo.match_ref import MatchRef
from espncricinfo.seasons import Season
from espncricinfo.series import Series
from espncricinfo.teams import Team

ROOT = "http://core.espnuk.org/v2/sports/cricket/leagues"


def fake_get(routes):
    def get(url, headers=None, timeout=None):
        response = MagicMock()
        if url not in routes:
            raise AssertionError(f"Unexpected request: {url}")
        status, data = routes[url]
        response.status_code = status
        response.json.return_value = data
        return response

    return get


def test_team_uses_reference_league_and_resolves_match_without_browser():
    team_url = f"{ROOT}/23262/teams/1812"
    athlete_url = f"{team_url}/athletes"
    event_url = f"{ROOT}/24371/events/1535654"
    routes = {
        team_url: (
            200,
            {
                "name": "India Women",
                "abbreviation": "IND-W",
                "isNational": False,
                "isActive": True,
                "logos": [{"href": "https://example.org/logo.png"}],
                "event": {"$ref": event_url, "date": "2026-10-20T13:30:15Z"},
                "athletes": {"$ref": athlete_url},
            },
        ),
        athlete_url: (
            200,
            {
                "items": [
                    {"$ref": "http://core.espnuk.org/v2/sports/cricket/athletes/253802"}
                ]
            },
        ),
    }
    with patch("espncricinfo._core.http_get", side_effect=fake_get(routes)) as get:
        team = Team.from_reference(team_url)
        assert (team.id, team.series_id, team.name) == (1812, 23262, "India Women")
        assert team.short_name == "IND-W"
        assert team.logo == "https://example.org/logo.png"
        assert team.match == MatchRef(24371, 1535654)
        assert team.match_date.year == 2026
        assert team.match_date.second == 15
        assert get.call_count == 1
        with patch("espncricinfo.player.Player") as player:
            assert team.players == [player.return_value]
            assert team.players == [player.return_value]
            player.assert_called_once_with(253802)
        assert get.call_count == 2


def test_season_loads_teams_and_all_event_pages_lazily():
    season_url = f"{ROOT}/23262/seasons/2026"
    team_url = f"{ROOT}/23262/teams/1812"
    routes = {
        season_url: (
            200,
            {
                "year": 2026,
                "name": "India Women tour of Australia",
                "startDate": "2026-02-13T00:00Z",
                "endDate": "2026-03-09T23:59Z",
            },
        ),
        f"{season_url}/teams": (200, {"items": [{"$ref": team_url}]}),
        team_url: (200, {"name": "India Women"}),
        f"{season_url}/events": (
            200,
            {"pageCount": 2, "items": [{"$ref": f"{ROOT}/23262/events/1478912"}]},
        ),
        f"{season_url}/events?page=2": (
            200,
            {"pageCount": 2, "items": [{"$ref": f"{ROOT}/23262/events/1478918"}]},
        ),
    }
    with patch("espncricinfo._core.http_get", side_effect=fake_get(routes)) as get:
        season = Season.from_reference(season_url)
        assert season.year == 2026
        assert season.start_date.month == 2
        assert get.call_count == 1
        assert [team.name for team in season.teams] == ["India Women"]
        assert season.match_refs == [
            MatchRef(23262, 1478912),
            MatchRef(23262, 1478918),
        ]
        assert season.match_refs == season.match_refs
        assert get.call_count == 5


def test_series_navigation_uses_canonical_references_and_live_status():
    alias = f"{ROOT}/1478874"
    canonical = f"{ROOT}/23262"
    season_url = f"{canonical}/seasons/2026"
    past_event = f"{canonical}/events/1478918"
    live_event = f"{canonical}/events/1535654"
    routes = {
        f"{alias}/": (
            200,
            {
                "name": "India Women tour of Australia",
                "shortName": "India Women in Australia",
                "abbreviation": "IND-W in AUS-W",
                "slug": "india-women-in-australia",
                "isTournament": False,
                "links": [{"href": "https://www.espncricinfo.com/series/1478874"}],
                "season": {"$ref": season_url},
                "events": {"$ref": f"{canonical}/events"},
            },
        ),
        f"{alias}/seasons": (200, {"items": [{"$ref": season_url}]}),
        f"{alias}/events": (200, {"items": [{"$ref": past_event}]}),
        season_url: (200, {"year": 2026, "name": "India Women tour of Australia"}),
        f"{season_url}/events": (
            200,
            {"items": [{"$ref": past_event}, {"$ref": live_event}]},
        ),
        f"{canonical}/events": (
            200,
            {"items": [{"$ref": past_event}, {"$ref": live_event}]},
        ),
        past_event: (
            200,
            {"competitions": [{"status": {"$ref": f"{past_event}/status"}}]},
        ),
        live_event: (
            200,
            {"competitions": [{"status": {"$ref": f"{live_event}/status"}}]},
        ),
        f"{past_event}/status": (200, {"type": {"state": "post"}}),
        f"{live_event}/status": (200, {"type": {"state": "in"}}),
    }
    with patch("espncricinfo._core.http_get", side_effect=fake_get(routes)):
        series = Series(1478874)
        assert series.years == ["2026"]
        assert series.current_season.year == 2026
        assert [season.year for season in series.season_objects] == [2026]
        assert series.matches == [MatchRef(23262, 1478918), MatchRef(23262, 1535654)]
        assert series.current_matches == [MatchRef(23262, 1535654)]


def test_series_without_seasons_uses_direct_event_references():
    url = f"{ROOT}/999"
    event_url = f"{ROOT}/999/events/123"
    routes = {
        f"{url}/": (
            200,
            {
                "name": "One-off match",
                "shortName": "One-off",
                "abbreviation": "ONE",
                "slug": "one-off",
                "isTournament": False,
                "links": [{"href": "https://www.espncricinfo.com/series/999"}],
                "events": {"$ref": f"{url}/events"},
            },
        ),
        f"{url}/seasons": (200, {"items": []}),
        f"{url}/events": (200, {"items": [{"$ref": event_url}]}),
        event_url: (200, {"competitions": []}),
    }
    with patch("espncricinfo._core.http_get", side_effect=fake_get(routes)):
        series = Series(999)
        assert series.current_season is None
        assert series.matches == [MatchRef(999, 123)]


@pytest.mark.parametrize(
    ("reference", "resource"),
    [("https://example.org/no-team/1", "teams"), ("/leagues/a/events/1", "events")],
)
def test_invalid_references_are_rejected(reference, resource):
    with pytest.raises(ValueError, match="Invalid"):
        reference_ids(reference, resource)


@pytest.mark.parametrize(
    ("cls", "url", "error"),
    [
        (Team, f"{ROOT}/23262/teams/999", NoTeamError),
        (Season, f"{ROOT}/23262/seasons/1999", NoSeasonError),
    ],
)
def test_missing_resource_raises_specific_error(cls, url, error):
    with (
        patch("espncricinfo._core.http_get", side_effect=fake_get({url: (404, {})})),
        pytest.raises(error),
    ):
        cls.from_reference(url)


@pytest.mark.integration
def test_live_series_navigation():
    series = Series(1478874)
    assert series.current_season.year == 2026
    assert any(team.name == "India Women" for team in series.current_season.teams)
    assert len(series.matches) == 8
    assert MatchRef(1478874, 1478918) in series.matches
    assert series.current_matches == []


def _bbl_routes():
    """A league whose seasons span New Year, as the Big Bash League's do."""
    league = f"{ROOT}/8044"
    seasons = [
        (1490534, 2025, "2025-12-14", "2026-01-26"),
        (1443056, 2024, "2024-12-15", "2025-01-27"),
    ]
    routes = {
        f"{league}/": (
            200,
            {
                "name": "Big Bash League",
                "shortName": "BBL",
                "abbreviation": "BBL",
                "slug": "big-bash-league",
            },
        ),
        f"{league}/seasons": (
            200,
            {
                "items": [
                    {"$ref": f"{ROOT}/{sid}/seasons/{year}"}
                    for sid, year, _, _ in seasons
                ]
            },
        ),
    }
    for sid, year, start, end in seasons:
        routes[f"{ROOT}/{sid}/seasons/{year}"] = (
            200,
            {
                "year": year,
                "name": f"Big Bash League {year}",
                "startDate": f"{start}T00:00Z",
                "endDate": f"{end}T23:59Z",
            },
        )
    return routes


@pytest.mark.parametrize("key", ["2024/25", "2024-25", "2024/2025", 2024, "2024"])
def test_series_season_finds_multi_year_season_by_any_label(key):
    with patch("espncricinfo._core.http_get", side_effect=fake_get(_bbl_routes())):
        season = Series(8044).season(key)
    assert (season.series_id, season.year, season.label) == (1443056, 2024, "2024/25")


def test_season_label_is_single_year_when_season_does_not_cross_new_year():
    url = f"{ROOT}/1449924/seasons/2025"
    routes = {
        url: (
            200,
            {
                "year": 2025,
                "startDate": "2025-03-21T00:00Z",
                "endDate": "2025-06-03T23:59Z",
            },
        )
    }
    with patch("espncricinfo._core.http_get", side_effect=fake_get(routes)):
        assert Season(2025, 1449924).label == "2025"


@pytest.mark.parametrize("key", ["2019/20", "2024/26", "twenty"])
def test_series_season_rejects_unknown_or_malformed_labels(key):
    with patch("espncricinfo._core.http_get", side_effect=fake_get(_bbl_routes())):
        series = Series(8044)
        with pytest.raises(NoSeasonError):
            series.season(key)


@pytest.mark.integration
def test_live_big_bash_2024_25_resolves_to_its_season_series_id():
    assert Series(8044).season("2024/25").series_id == 1443056
