"""Match data scraped from ESPNcricinfo match pages via Playwright."""

import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date as _date
from datetime import datetime as _datetime
from typing import Any, TypedDict

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from espncricinfo import _core
from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError
from espncricinfo.match_ref import MatchRef


async def _async_playwright_fetch(url):
    """Fetch a page via Playwright (WebKit) and return the parsed __NEXT_DATA__ dict.

    WebKit is used because Akamai does not block it in headless mode.
    Raises MatchNotFoundError on 404.
    """
    async with async_playwright() as pw:
        browser = await pw.webkit.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/16.0 Safari/605.1.15"
            ),
        )
        page = await context.new_page()

        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if response and response.status == 404:
            await browser.close()
            raise MatchNotFoundError(f"Match not found at {url}")

        content = await page.content()
        await browser.close()

    # Extract __NEXT_DATA__ from the HTML
    import re

    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        content,
        re.DOTALL,
    )
    if not m:
        raise NoScorecardError("Could not find __NEXT_DATA__ in page")
    return json.loads(m.group(1))


def _playwright_fetch(url: str) -> dict[str, Any]:
    """Synchronous wrapper around _async_playwright_fetch.

    Jupyter and other async callers already run an event loop on this thread,
    and asyncio.run() refuses to nest inside one, so the fetch then runs on a
    worker thread with its own loop.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_async_playwright_fetch(url))
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(_async_playwright_fetch(url))).result()


def _boundary_count(inn: dict[str, Any], key: str) -> int | None:
    """Innings fours or sixes: ESPN's total, else the batters' sum, else None.

    Where ESPN gives both, the total equals the batters' sum; older matches
    often carry only the batters' figures, and the oldest carry neither.
    """
    if inn.get(key) is not None:
        return inn[key]
    counts = [
        bat.get(key)
        for bat in inn.get("inningBatsmen") or []
        if bat.get("battedType") == "yes"
    ]
    if not counts or any(count is None for count in counts):
        return None
    return sum(counts)


def _as_float(record: dict[str, Any] | None, key: str) -> float | None:
    """Return ``record[key]`` as a float, or None if absent or not numeric."""
    if record is None:
        return None
    try:
        return float(record[key])
    except (KeyError, TypeError, ValueError):
        return None


def _normalize(next_data, match_id, series_id):
    """Reshape a match page's __NEXT_DATA__ into the old engine JSON layout.

    Match reads its attributes from this layout. Raw page data is kept under
    ``_match``, ``_content`` and ``_match_players``.
    """
    try:
        app_data = next_data["props"]["appPageProps"]["data"]
        # Live pages return match/content directly; fixtures add a "data" level.
        if "match" in app_data and "content" in app_data:
            data = app_data
        elif "data" in app_data:
            data = app_data["data"]
        else:
            raise KeyError("no match/content in appPageProps.data")
    except KeyError as exc:
        raise NoScorecardError(f"Unexpected __NEXT_DATA__ structure: {exc}") from exc

    match = data["match"]
    content = data.get("content", {})
    innings_raw = content.get("innings", [])
    match_players = content.get("matchPlayers", {})
    team_players_list = match_players.get("teamPlayers", [])

    # ---- teams ----
    teams_raw = match.get("teams", [])

    # Build a lookup: team internal id -> objectId (for tossWinnerTeamId mapping)
    team_id_to_objectid = {}
    for t in teams_raw:
        team_id_to_objectid[t["team"]["id"]] = str(t["team"]["objectId"])

    # Build player lists per team (keyed by team objectId)
    players_by_team = {}
    for tp in team_players_list:
        oid = str(tp["team"]["objectId"])
        players_by_team[oid] = tp.get("players", [])

    def build_team(t):
        oid = str(t["team"]["objectId"])
        return {
            "team_id": oid,
            "team_abbreviation": t["team"]["abbreviation"],
            "team_name": t["team"]["name"],
            "team_long_name": t["team"]["longName"],
            "player": players_by_team.get(oid, []),
        }

    teams_normalized = [build_team(t) for t in teams_raw]

    # ---- home_team_id ----
    home_team_id = None
    for t in teams_raw:
        if t.get("isHome"):
            home_team_id = str(t["team"]["objectId"])
            break

    # ---- toss ----
    toss_winner_internal = match.get("tossWinnerTeamId")
    toss_winner_team_id = (
        team_id_to_objectid.get(toss_winner_internal, "")
        if toss_winner_internal
        else ""
    )
    toss_choice = match.get("tossWinnerChoice")
    toss_decision = "1" if toss_choice == 1 else "2"
    toss_decision_name = "bat" if toss_choice == 1 else "bowl"

    # ---- winner ----
    winner_internal = match.get("winnerTeamId")
    winner_team_id = (
        team_id_to_objectid.get(winner_internal, "") if winner_internal else ""
    )

    # ---- batting first ----
    batting_first_team_id = ""
    if innings_raw:
        batting_first_team_id = str(innings_raw[0]["team"]["objectId"])

    # ---- innings ----
    innings_normalized = []
    for inn in innings_raw:
        overs = inn.get("overs") or 0
        runs = inn.get("runs") or 0
        try:
            run_rate = round(runs / overs, 2) if overs > 0 else 0.0
        except (ZeroDivisionError, TypeError):
            run_rate = 0.0
        innings_normalized.append(
            {
                "batting_team_id": str(inn["team"]["objectId"]),
                "runs": runs,
                "wickets": inn.get("wickets"),
                "overs": str(overs),
                "run_rate": str(run_rate),
                "event_name": inn.get("event"),
                "inning_number": inn.get("inningNumber"),
                "inningBatsmen": inn.get("inningBatsmen", []),
                "inningBowlers": inn.get("inningBowlers", []),
                "inningFallOfWickets": inn.get("inningFallOfWickets", []),
                "inningOvers": inn.get("inningOvers") or [],
                "fours": _boundary_count(inn, "fours"),
                "sixes": _boundary_count(inn, "sixes"),
                "extras": inn.get("extras"),
                "byes": inn.get("byes"),
                "legbyes": inn.get("legbyes"),
                "wides": inn.get("wides"),
                "noballs": inn.get("noballs"),
                "target": inn.get("target"),
            }
        )

    # ---- ground location ----
    ground = match.get("ground", {})
    ground_location = ground.get("location", "") or ""
    town = ground.get("town", {}) or {}
    continent = None  # not available in new API
    city = town.get("name") or ground_location or None

    # ---- series ----
    series_data = match.get("series", {})

    # ---- match class ----
    intl_class_map = {
        1: "Test",
        2: "ODI",
        3: "T20I",
        10: "WT20I",
        11: "WODI",
        12: "WTest",
    }
    intl_class_id = match.get("internationalClassId")
    intl_class_card = intl_class_map.get(intl_class_id, "") if intl_class_id else ""
    general_class_card = match.get("format", "")

    # ---- innings_list for centre ----
    innings_list = [str(i + 1) for i in range(len(innings_normalized))]

    # ---- description ----
    if teams_raw and len(teams_raw) >= 2:
        description = f"{teams_raw[0]['team']['name']} v {teams_raw[1]['team']['name']}"
    else:
        description = match.get("title", "")

    return {
        "description": description,
        "match": {
            "match_status": match.get("status", "").lower(),
            "international_class_card": intl_class_card,
            "general_class_card": general_class_card,
            "season": match.get("season", ""),
            "start_date_raw": (match.get("startDate") or "")[:10],
            "cancelled_match": "Y" if match.get("isCancelled") else "N",
            "ground_id": str(ground.get("objectId", "")),
            "ground_name": ground.get("longName", ""),
            "scheduled_overs": match.get("scheduledOvers"),
            "home_team_id": home_team_id,
            "winner_team_id": winner_team_id,
            "toss_winner_team_id": toss_winner_team_id,
            "toss_choice_team_id": toss_winner_team_id,  # same in new API
            "toss_decision": toss_decision,
            "toss_decision_name": toss_decision_name,
            "batting_first_team_id": batting_first_team_id,
            "continent_name": continent,
            "town_name": city,
            "town_area": city,
            "town_id": str(ground.get("objectId", "")),
            "floodlit_name": match.get("floodlit", ""),
            "legacy_url": f"/ci/engine/match/{match_id}.html",
            "cms_match_title": match.get("title", ""),
            "present_datetime_local": match.get("startDate", ""),
            "present_datetime_gmt": match.get("startDate", ""),
            "start_datetime_local": match.get("startDate", ""),
            "start_datetime_gmt": match.get("startDate", ""),
            "rain_rule": None,
            "rain_rule_name": None,
            "weather_location_code": None,
            "followon": None,
            "current_summary": match.get("statusText", ""),
        },
        "series": [
            {
                "series_name": series_data.get("name", ""),
                "core_recreation_id": str(
                    series_data.get("objectId") or series_id or ""
                ),
                "slug": series_data.get("slug", ""),
            }
        ],
        "live": {
            "status": match.get("statusText", ""),
        },
        "team": teams_normalized,
        "innings": innings_normalized,
        "official": [],
        "centre": {
            "common": {
                "innings_list": innings_list,
                "batting": [],
                "bowling": [],
                "innings": None,
            },
            "fow": None,
        },
        # Keep raw new-API data accessible
        "_match": match,
        "_content": content,
        "_match_players": match_players,
    }


class MatchTeam(TypedDict):
    """One side of a match, as held in :attr:`Match.team_1` and ``team_2``."""

    team_id: str
    team_abbreviation: str
    team_name: str
    team_long_name: str
    player: list[dict[str, Any]]


class BattingEntry(TypedDict):
    """One row of :attr:`Match.batting_scorecard`.

    Numeric fields are ``None`` for players who did not bat.
    """

    name: str | None
    full_name: str | None
    player_id: int | None
    runs: int | None
    balls: int | None
    minutes: int | None
    fours: int | None
    sixes: int | None
    strike_rate: float | None
    is_out: bool
    dismissal: str
    batted: bool


class OverEntry(TypedDict):
    """One over of :attr:`Match.over_by_over`."""

    over: int
    runs: int
    wickets: int
    total_runs: int
    total_wickets: int


class BowlingEntry(TypedDict):
    """One row of :attr:`Match.bowling_scorecard`."""

    name: str | None
    full_name: str | None
    player_id: int | None
    overs: float | None
    maidens: int | None
    runs: int | None
    wickets: int | None
    economy: float | None
    wides: int | None
    no_balls: int | None
    dots: int | None


class Match:
    """One match, loaded from its ESPNcricinfo full-scorecard page.

    Loading starts a headless WebKit browser, because the site's CDN refuses
    plain HTTP clients. Example values below are for ``Match(1478914, 1478874)``.
    """

    #: ESPNcricinfo match id.
    match_id: int
    #: ESPNcricinfo series id, as ESPN reports it for this match.
    series_id: int
    #: ``'IND Women v AUS Women'``.
    description: str
    #: Match title within the series, e.g. ``'3rd T20I'``.
    match_title: str
    #: Format, e.g. ``'WT20I'``, ``'T20'``, ``'Test'``.
    match_class: str
    #: ESPN status, e.g. ``'result'``; ``'dormant'`` for unplayed matches.
    status: str
    #: Result line, e.g. ``'IND Women won by 17 runs'``.
    result: str
    #: Season label, e.g. ``'2025/26'``.
    season: str
    #: ``'India Women in Australia'``.
    series_name: str | None
    #: Start date, ``'YYYY-MM-DD'``.
    date: str
    #: Start time in UTC, ISO 8601.
    start_datetime: str
    #: True if ESPN marks the match as canceled.
    canceled: bool
    #: ESPN ground id.
    ground_id: str
    #: ``'Adelaide Oval'``.
    ground_name: str
    #: Town or city of the ground.
    town_name: str | None
    #: Floodlight setting, e.g. ``'night'``.
    lighting: str
    #: Scheduled overs per side; None for Tests.
    scheduled_overs: int | None
    #: Innings numbers as strings, ``['1', '2']``.
    innings_list: list[str]
    #: One dict per innings: team id, runs, wickets, overs, ``fours``, ``sixes``
    #: (None where ESPN has no figures) and ESPN's raw lists.
    innings: list[dict[str, Any]]
    #: ESPN's raw innings records, including partnerships and commentary.
    all_innings: list[dict[str, Any]]
    #: ESPN's raw squads (``teamPlayers``), or None.
    rosters: dict[str, Any] | None
    #: First-listed side.
    team_1: MatchTeam
    #: Second-listed side.
    team_2: MatchTeam
    #: ``team_1['team_id']``.
    team_1_id: str
    #: ``team_2['team_id']``.
    team_2_id: str
    #: ``team_1['team_abbreviation']``, e.g. ``'IND-W'``.
    team_1_abbreviation: str
    #: ``team_2['team_abbreviation']``.
    team_2_abbreviation: str
    #: ESPN's raw player records for team 1.
    team_1_players: list[dict[str, Any]]
    #: ESPN's raw player records for team 2.
    team_2_players: list[dict[str, Any]]
    #: Team 1's first innings record, or None if it has not batted.
    team_1_innings: dict[str, Any] | None
    #: Team 2's first innings record, or None if it has not batted.
    team_2_innings: dict[str, Any] | None
    #: Team 1's runs per over, or None.
    team_1_run_rate: float | None
    #: Team 2's runs per over, or None.
    team_2_run_rate: float | None
    #: Overs team 1 batted, or None.
    team_1_overs_batted: float | None
    #: Overs team 2 batted, or None.
    team_2_overs_batted: float | None
    #: Abbreviation of the home side, or None.
    home_team: str | None
    #: Abbreviation of the side that batted first, or None.
    batting_first: str | None
    #: Abbreviation of the winner; None for no result, a tie or an unplayed match.
    match_winner: str | None
    #: Team id of the toss winner, or None.
    toss_winner: str | None
    #: ``'bat'`` or ``'bowl'``, or None before the toss.
    toss_decision_name: str | None
    #: Core API event URL.
    event_url: str
    #: Core API URL for the ball-by-ball details.
    details_url: str
    #: ESPN site API summary URL.
    espn_api_url: str
    #: The parsed page, reshaped by ``_normalize``. Prefer the attributes.
    json: dict[str, Any]

    def __init__(self, match_id: int | str, series_id: int | str | None = None) -> None:
        """Fetch and parse the match.

        Args:
            match_id: ESPNcricinfo match (event) id.
            series_id: ESPNcricinfo series id the match belongs to. Optional:
                without it the match page is found from the match id alone,
                and ``series_id`` is read from the page.

        Raises:
            MatchNotFoundError: If ESPNcricinfo has no such match.
        """
        self.match_id = int(match_id)
        given_series = int(series_id) if series_id is not None else None
        self.json = self._get_json(given_series)
        data = self.json
        match = data["match"]
        series = data["series"][-1]

        page_series = series.get("core_recreation_id")
        if page_series:
            self.series_id = int(page_series)
        elif given_series is not None:
            self.series_id = given_series
        else:
            raise MatchNotFoundError(f"No series found for match {self.match_id}")
        self.description = data["description"]
        self.match_title = match["cms_match_title"]
        self.match_class = (
            match["international_class_card"] or match["general_class_card"]
        )
        self.status = match["match_status"]
        self.result = data["live"]["status"]
        self.season = match["season"]
        self.series_name = series["series_name"] or None
        self.date = match["start_date_raw"]
        self.start_datetime = match["start_datetime_gmt"]
        self.canceled = match["cancelled_match"] != "N"
        self.ground_id = match["ground_id"]
        self.ground_name = match["ground_name"]
        self.town_name = match.get("town_name")
        self.lighting = match["floodlit_name"]
        overs = match.get("scheduled_overs")
        self.scheduled_overs = int(overs) if overs is not None else None
        self.innings_list = data["centre"]["common"]["innings_list"]
        self.innings = data["innings"]
        self.all_innings = data.get("_content", {}).get("innings", self.innings)
        self.rosters = data.get("_match_players")

        self.team_1, self.team_2 = data["team"][0], data["team"][1]
        self.team_1_id = self.team_1["team_id"]
        self.team_2_id = self.team_2["team_id"]
        self.team_1_abbreviation = self.team_1["team_abbreviation"]
        self.team_2_abbreviation = self.team_2["team_abbreviation"]
        self.team_1_players = self.team_1.get("player", [])
        self.team_2_players = self.team_2.get("player", [])
        self.team_1_innings = self._first_innings_of(self.team_1_id)
        self.team_2_innings = self._first_innings_of(self.team_2_id)
        self.team_1_run_rate = _as_float(self.team_1_innings, "run_rate")
        self.team_2_run_rate = _as_float(self.team_2_innings, "run_rate")
        self.team_1_overs_batted = _as_float(self.team_1_innings, "overs")
        self.team_2_overs_batted = _as_float(self.team_2_innings, "overs")

        self.home_team = self._abbreviation(match.get("home_team_id"))
        self.batting_first = self._abbreviation(match.get("batting_first_team_id"))
        self.match_winner = self._abbreviation(match.get("winner_team_id"))
        toss_winner = match.get("toss_winner_team_id") or None
        self.toss_winner = toss_winner
        self.toss_decision_name = (
            match.get("toss_decision_name") or None if toss_winner else None
        )

        self.event_url = (
            "http://core.espnuk.org/v2/sports/cricket/leagues/"
            f"{self.series_id}/events/{self.match_id}"
        )
        self.details_url = (
            f"{self.event_url}/competitions/{self.match_id}/details"
            "?page_size=1000&page=1"
        )
        self.espn_api_url = (
            "https://site.api.espn.com/apis/site/v2/sports/cricket/"
            f"{self.series_id}/summary?event={self.match_id}"
        )

    def __str__(self) -> str:
        """Return the match description."""
        return self.description

    def __repr__(self) -> str:
        """Return ``Match(match_id, series_id)``."""
        return f"{self.__class__.__name__}({self.match_id!r}, {self.series_id!r})"

    def _get_json(self, series_id: int | None) -> dict[str, Any]:
        """Fetch the match page and reshape its __NEXT_DATA__ blob."""
        if series_id is None:
            # ESPNcricinfo redirects its legacy match URL to the full match
            # page, whatever series the match belongs to.
            url = f"https://www.espncricinfo.com/matches/engine/match/{self.match_id}.html"
        else:
            url = (
                f"https://www.espncricinfo.com/series/"
                f"x-{series_id}/x-{self.match_id}/full-scorecard"
            )
        return _normalize(_playwright_fetch(url), self.match_id, series_id)

    def _first_innings_of(self, team_id: str) -> dict[str, Any] | None:
        return next(
            (inn for inn in self.innings if inn["batting_team_id"] == team_id), None
        )

    def _abbreviation(self, team_id: str | None) -> str | None:
        """Map a team id to its abbreviation; None when ESPN gives no team."""
        teams = {
            self.team_1_id: self.team_1_abbreviation,
            self.team_2_id: self.team_2_abbreviation,
        }
        return teams.get(team_id or "")

    def _innings_field(self, innings: int, field: str) -> Any:
        try:
            return self.innings[innings - 1][field]
        except (IndexError, KeyError):
            return None

    def batsmen(self, innings: int) -> list[dict[str, Any]] | None:
        """ESPN's raw batting records for a 1-based innings, or None."""
        return self._innings_field(innings, "inningBatsmen")

    def bowlers(self, innings: int) -> list[dict[str, Any]] | None:
        """ESPN's raw bowling records for a 1-based innings, or None."""
        return self._innings_field(innings, "inningBowlers")

    def fows(self, innings: int) -> list[dict[str, Any]] | None:
        """ESPN's raw fall-of-wicket records for a 1-based innings, or None."""
        return self._innings_field(innings, "inningFallOfWickets")

    def extras(self, innings: int) -> dict[str, int | None] | None:
        """Extras for a 1-based innings: total, byes, leg byes, wides, no balls."""
        if not 1 <= innings <= len(self.innings):
            return None
        inn = self.innings[innings - 1]
        return {
            key: inn.get(key)
            for key in ("extras", "byes", "legbyes", "wides", "noballs")
        }

    # ------------------------------------------------------------------
    # Scorecard helpers
    # ------------------------------------------------------------------

    def _batting_entry(self, raw: dict[str, Any]) -> BattingEntry:
        """Transform a raw inningBatsmen dict into a clean flat dict."""
        player = raw.get("player") or {}
        batted = raw.get("battedType") == "yes"
        is_out = bool(raw.get("isOut"))
        if not batted:
            dismissal = "did not bat"
        elif is_out:
            dismissal = (raw.get("dismissalText") or {}).get("long", "out")
        else:
            dismissal = "not out"
        return {
            "name": player.get("name"),
            "full_name": player.get("longName"),
            "player_id": player.get("objectId"),
            "runs": raw.get("runs") if batted else None,
            "balls": raw.get("balls") if batted else None,
            "minutes": raw.get("minutes") if batted else None,
            "fours": raw.get("fours") if batted else None,
            "sixes": raw.get("sixes") if batted else None,
            "strike_rate": float(sr)
            if (batted and (sr := raw.get("strikerate")) is not None)
            else None,
            "is_out": is_out,
            "dismissal": dismissal,
            "batted": batted,
        }

    @property
    def batting_scorecard(self) -> list[list[BattingEntry]]:
        """Batting scorecard: one list per innings, one row per batter.

        Outer list is indexed by innings order; inner list has one entry
        per batsman. Players who did not bat have ``batted=False`` and
        numeric fields as ``None``.

        Example::

            for i, innings in enumerate(m.batting_scorecard, 1):
                print(f"Innings {i}:")
                for b in innings:
                    print(b["name"], b["runs"], b["balls"], b["dismissal"])
        """
        result = []
        for i in range(1, len(self.innings) + 1):
            raw_list = self.batsmen(i)
            if raw_list:
                result.append([self._batting_entry(r) for r in raw_list])
            else:
                result.append([])
        return result

    def _bowling_entry(self, raw: dict[str, Any]) -> BowlingEntry:
        """Transform a raw inningBowlers dict into a clean flat dict."""
        player = raw.get("player") or {}
        economy = raw.get("economy")
        overs = raw.get("overs")
        return {
            "name": player.get("name"),
            "full_name": player.get("longName"),
            "player_id": player.get("objectId"),
            "overs": float(overs) if overs is not None else None,
            "maidens": raw.get("maidens"),
            "runs": raw.get("conceded"),
            "wickets": raw.get("wickets"),
            "economy": float(economy) if economy is not None else None,
            "wides": raw.get("wides"),
            "no_balls": raw.get("noballs"),
            "dots": raw.get("dots"),
        }

    @property
    def bowling_scorecard(self) -> list[list[BowlingEntry]]:
        """Bowling scorecard: one list per innings, one row per bowler.

        Outer list is indexed by innings order; inner list has one entry
        per bowler.

        Example::

            for i, innings in enumerate(m.bowling_scorecard, 1):
                print(f"Innings {i}:")
                for b in innings:
                    print(b["name"], b["wickets"], b["runs"], b["overs"])
        """
        result = []
        for i in range(1, len(self.innings) + 1):
            raw_list = self.bowlers(i)
            if raw_list:
                result.append([self._bowling_entry(r) for r in raw_list])
            else:
                result.append([])
        return result

    @property
    def over_by_over(self) -> list[list[OverEntry]]:
        """Runs and wickets per over: one list per innings, one row per over.

        Empty for an innings ESPN has no over data for, as with early Tests.

        Example::

            for over in m.over_by_over[0]:
                print(over["over"], over["runs"], over["total_runs"])
        """
        return [
            [
                OverEntry(
                    over=o["overNumber"],
                    runs=o["overRuns"],
                    wickets=o["overWickets"],
                    total_runs=o["totalRuns"],
                    total_wickets=o["totalWickets"],
                )
                for o in inn.get("inningOvers") or []
            ]
            for inn in self.innings
        ]

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_recent_matches(date: _date | str | None = None) -> list[MatchRef]:
        """Return MatchRefs for the matches on ESPNcricinfo's results page.

        ESPN returns roughly the two weeks of matches ending on ``date``. Use
        :meth:`get_matches_on` for the matches played on one day.

        Args:
            date: A ``datetime.date`` or a string in YYYY-MM-DD or DD-MM-YYYY
                form; defaults to today.

        Returns:
            The listed matches, most recent first.
        """
        return [ref for ref, _, _ in _results_page(_as_day(date))]

    @staticmethod
    def get_matches_on(date: _date | str | None = None) -> list[MatchRef]:
        """Return MatchRefs for the matches being played on one day.

        A match counts if the day falls between its start and end dates, so a
        Test appears on each of its days.

        Args:
            date: A ``datetime.date`` or a string in YYYY-MM-DD or DD-MM-YYYY
                form; defaults to today.

        Returns:
            The matches on that day.
        """
        day = _as_day(date)
        return [ref for ref, start, end in _results_page(day) if start <= day <= end]

    @staticmethod
    def get_match_ids(year: int, match_format: int = 1) -> list[int]:
        """Return the ids of every international match of one format in a year.

        Reads Statsguru's results table, so it covers matches back to 1877.
        Pass each id to :class:`Match` to load it; each load starts a browser.

        Args:
            year: Calendar year, e.g. ``2023``.
            match_format: Statsguru class: 1 Test, 2 ODI, 3 T20I,
                8 women's Test, 9 women's ODI, 10 women's T20I.

        Returns:
            Match ids in the order Statsguru lists them (by date).
        """
        response = _core.http_get(
            "https://stats.espncricinfo.com/ci/engine/records/team/"
            f"match_results.html?class={match_format};id={year};type=year"
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        ids: list[int] = []
        for row in soup.select("table.engineTable tr.data1"):
            for link in row.find_all("a", href=True):
                found = _MATCH_LINK.search(str(link["href"]))
                if found and int(found.group(1)) not in ids:
                    ids.append(int(found.group(1)))
        return ids


_MATCH_LINK = re.compile(r"/ci/engine/match/(\d+)\.html")


def _as_day(date: _date | str | None) -> _date:
    """Parse a date argument; ESPN's results page wants DD-MM-YYYY."""
    if date is None:
        return _datetime.now().astimezone().date()
    if isinstance(date, _date):
        return date
    try:
        return _date.fromisoformat(date)
    except ValueError:
        dd, mm, yyyy = (int(part) for part in date.split("-"))
        return _date(yyyy, mm, dd)


def _results_page(day: _date) -> list[tuple[MatchRef, _date, _date]]:
    """(MatchRef, start date, end date) for each match on the results page."""
    url = f"https://www.espncricinfo.com/live-cricket-match-results?date={day:%d-%m-%Y}"
    next_data = _playwright_fetch(url)
    try:
        matches = next_data["props"]["appPageProps"]["data"]["data"]["content"][
            "matches"
        ]
    except (KeyError, TypeError):
        return []
    results = []
    for m in matches:
        try:
            ref = MatchRef(series_id=m["series"]["objectId"], match_id=m["objectId"])
            start = _date.fromisoformat(m["startDate"][:10])
            end = _date.fromisoformat((m.get("endDate") or m["startDate"])[:10])
        except (KeyError, TypeError, ValueError):
            continue
        results.append((ref, start, end))
    return results
