import json
import asyncio
from datetime import date as _date
from playwright.async_api import async_playwright
from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError
from espncricinfo.match_ref import MatchRef


async def _async_playwright_fetch(url):
    """
    Fetch a page via Playwright (WebKit) and return the parsed __NEXT_DATA__ dict.
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
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', content, re.DOTALL)
    if not m:
        raise NoScorecardError("Could not find __NEXT_DATA__ in page")
    return json.loads(m.group(1))


def _playwright_fetch(url):
    """Synchronous wrapper around _async_playwright_fetch."""
    return asyncio.run(_async_playwright_fetch(url))


def _normalise(next_data, match_id, series_id):
    """
    Transform the __NEXT_DATA__ dict (at props.appPageProps.data.data) into a
    dict shaped like the old engine JSON, so that all existing private methods
    (_description, _match_class, etc.) continue to work unchanged.
    """
    try:
        app_data = next_data["props"]["appPageProps"]["data"]
        # Live pages return match/content directly; fixtures wrap with an extra "data" key
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

    teams_normalised = [build_team(t) for t in teams_raw]

    # ---- home_team_id ----
    home_team_id = None
    for t in teams_raw:
        if t.get("isHome"):
            home_team_id = str(t["team"]["objectId"])
            break

    # ---- toss ----
    toss_winner_internal = match.get("tossWinnerTeamId")
    toss_winner_team_id = team_id_to_objectid.get(toss_winner_internal, "") if toss_winner_internal else ""
    toss_choice = match.get("tossWinnerChoice")
    toss_decision = "1" if toss_choice == 1 else "2"
    toss_decision_name = "bat" if toss_choice == 1 else "bowl"

    # ---- winner ----
    winner_internal = match.get("winnerTeamId")
    winner_team_id = team_id_to_objectid.get(winner_internal, "") if winner_internal else ""

    # ---- batting first ----
    batting_first_team_id = ""
    if innings_raw:
        batting_first_team_id = str(innings_raw[0]["team"]["objectId"])

    # ---- innings ----
    innings_normalised = []
    for inn in innings_raw:
        overs = inn.get("overs") or 0
        runs = inn.get("runs") or 0
        try:
            run_rate = round(runs / overs, 2) if overs > 0 else 0.0
        except (ZeroDivisionError, TypeError):
            run_rate = 0.0
        innings_normalised.append({
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
            "extras": inn.get("extras"),
            "byes": inn.get("byes"),
            "legbyes": inn.get("legbyes"),
            "wides": inn.get("wides"),
            "noballs": inn.get("noballs"),
            "target": inn.get("target"),
        })

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
    innings_list = [str(i + 1) for i in range(len(innings_normalised))]

    # ---- description ----
    if teams_raw and len(teams_raw) >= 2:
        description = (
            f"{teams_raw[0]['team']['name']} v {teams_raw[1]['team']['name']}"
        )
    else:
        description = match.get("title", "")

    # ---- Assemble normalised dict ----
    normalised = {
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
                "core_recreation_id": str(series_data.get("objectId", series_id)),
                "slug": series_data.get("slug", ""),
            }
        ],
        "live": {
            "status": match.get("statusText", ""),
        },
        "team": teams_normalised,
        "innings": innings_normalised,
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

    return normalised


class Match(object):

    def __init__(self, match_id, series_id):
        self.match_id = int(match_id)
        self.series_id = int(series_id)
        self.json = self.get_json()
        self.html = self.get_html()
        self.comms_json = self.get_comms_json()
        if self.json:
            self.__unicode__ = self._description()
            self.status = self._status()
            self.match_class = self._match_class()
            self.season = self._season()
            self.description = self._description()
            self.legacy_scorecard_url = self._legacy_scorecard_url()
            self.series = self._series()
            self.series_name = self._series_name()
            self.series_id = self._series_id()
            self.event_url = (
                "http://core.espnuk.org/v2/sports/cricket/leagues/"
                f"{self.series_id}/events/{match_id}"
            )
            self.details_url = self._details_url()
            self.officials = self._officials()
            self.current_summary = self._current_summary()
            self.present_datetime_local = self._present_datetime_local()
            self.present_datetime_gmt = self._present_datetime_gmt()
            self.start_datetime_local = self._start_datetime_local()
            self.start_datetime_gmt = self._start_datetime_gmt()
            self.cancelled_match = self._cancelled_match()
            self.rain_rule = self._rain_rule()
            self.date = self._date()
            self.continent = self._continent()
            self.town_area = self._town_area()
            self.town_name = self._town_name()
            self.town_id = self._town_id()
            self.weather_location_code = self._weather_location_code()
            self.match_title = self._match_title()
            self.result = self._result()
            self.ground_id = self._ground_id()
            self.ground_name = self._ground_name()
            self.lighting = self._lighting()
            self.followon = self._followon()
            self.scheduled_overs = self._scheduled_overs()
            self.innings_list = self._innings_list()
            self.innings = self._innings()
            self.latest_batting = self._latest_batting()
            self.latest_bowling = self._latest_bowling()
            self.latest_innings = self._latest_innings()
            self.latest_innings_fow = self._latest_innings_fow()
            self.team_1 = self._team_1()
            self.team_1_id = self._team_1_id()
            self.team_1_abbreviation = self._team_1_abbreviation()
            self.team_1_players = self._team_1_players()
            self.team_1_innings = self._team_1_innings()
            self.team_1_run_rate = self._team_1_run_rate()
            self.team_1_overs_batted = self._team_1_overs_batted()
            self.team_1_batting_result = self._team_1_batting_result()
            self.team_2 = self._team_2()
            self.team_2_id = self._team_2_id()
            self.team_2_abbreviation = self._team_2_abbreviation()
            self.team_2_players = self._team_2_players()
            self.team_2_innings = self._team_2_innings()
            self.team_2_run_rate = self._team_2_run_rate()
            self.team_2_overs_batted = self._team_2_overs_batted()
            self.team_2_batting_result = self._team_2_batting_result()
            if not self.status == 'dormant':
                self.home_team = self._home_team()
                self.batting_first = self._batting_first()
                self.match_winner = self._match_winner()
                self.toss_winner = self._toss_winner()
                self.toss_decision = self._toss_decision()
                self.toss_decision_name = self._toss_decision_name()
                self.toss_choice_team_id = self._toss_choice_team_id()
                self.toss_winner_team_id = self._toss_winner_team_id()
                self.espn_api_url = self._espn_api_url()
                # from comms_json / content
                self.rosters = self._rosters()
                self.all_innings = self._all_innings()

    def __str__(self):
        return self.description

    def __repr__(self):
        return f"{self.__class__.__name__}({self.match_id!r})"

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def get_json(self):
        """
        Fetch the match page via Playwright, extract __NEXT_DATA__, and return
        a normalised dict shaped like the old engine JSON.
        """
        url = (
            f"https://www.espncricinfo.com/series/"
            f"x-{self.series_id}/x-{self.match_id}/full-scorecard"
        )
        next_data = _playwright_fetch(url)
        return _normalise(next_data, self.match_id, self.series_id)

    def get_html(self):
        """Not used in the new implementation; returns None."""
        return None

    def get_comms_json(self):
        """Commentary data is now available via self.json['_content']; returns None."""
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def match_json(self):
        return self.json["match"]

    def innings_comms_url(self, innings=1, page=1):
        return (
            f"https://hsapi.espncricinfo.com/v1/pages/match/comments"
            f"?lang=en&leagueId={self.series_id}&eventId={self.match_id}"
            f"&period={innings}&page={page}&filter=full&liveTest=false"
        )

    def _espn_api_url(self):
        return (
            f"https://site.api.espn.com/apis/site/v2/sports/cricket/"
            f"{self.series_id}/summary?event={self.match_id}"
        )

    def _legacy_scorecard_url(self):
        return "https://static.espncricinfo.com" + self.match_json()["legacy_url"]

    def _details_url(self, page=1, number=1000):
        return (
            self.event_url
            + f"/competitions/{self.match_id}/details"
            f"?page_size={number}&page={page}"
        )

    def _status(self):
        return self.match_json()["match_status"]

    def _match_class(self):
        if self.match_json()["international_class_card"] != "":
            return self.match_json()["international_class_card"]
        else:
            return self.match_json()["general_class_card"]

    def _season(self):
        return self.match_json()["season"]

    def _description(self):
        return self.json["description"]

    def _series(self):
        return self.json["series"]

    def _series_name(self):
        try:
            return self.json["series"][-1]["series_name"]
        except Exception:
            return None

    def _series_id(self):
        return self.json["series"][-1]["core_recreation_id"]

    def _officials(self):
        return self.json["official"]

    def _current_summary(self):
        return self.match_json().get("current_summary")

    def _present_datetime_local(self):
        return self.match_json()["present_datetime_local"]

    def _present_datetime_gmt(self):
        return self.match_json()["present_datetime_gmt"]

    def _start_datetime_local(self):
        return self.match_json()["start_datetime_local"]

    def _start_datetime_gmt(self):
        return self.match_json()["start_datetime_gmt"]

    def _cancelled_match(self):
        return self.match_json()["cancelled_match"] != "N"

    def _rain_rule(self):
        if self.match_json().get("rain_rule") == "1":
            return self.match_json()["rain_rule_name"]
        return None

    def _date(self):
        return self.match_json()["start_date_raw"]

    def _continent(self):
        return self.match_json().get("continent_name")

    def _town_area(self):
        return self.match_json().get("town_area")

    def _town_name(self):
        return self.match_json().get("town_name")

    def _town_id(self):
        return self.match_json().get("town_id")

    def _weather_location_code(self):
        return self.match_json().get("weather_location_code")

    def _match_title(self):
        return self.match_json()["cms_match_title"]

    def _result(self):
        return self.json["live"]["status"]

    def _ground_id(self):
        return self.match_json()["ground_id"]

    def _ground_name(self):
        return self.match_json()["ground_name"]

    def _lighting(self):
        return self.match_json()["floodlit_name"]

    def _followon(self):
        if self.match_json().get("followon") == "1":
            return True
        return False

    def _scheduled_overs(self):
        try:
            return int(self.match_json()["scheduled_overs"])
        except Exception:
            return None

    def _innings_list(self):
        try:
            return self.json["centre"]["common"]["innings_list"]
        except Exception:
            return None

    def _innings(self):
        return self.json["innings"]

    def _latest_batting(self):
        try:
            return self.json["centre"]["common"]["batting"]
        except Exception:
            return None

    def _latest_bowling(self):
        try:
            return self.json["centre"]["common"]["bowling"]
        except Exception:
            return None

    def _latest_innings(self):
        try:
            return self.json["centre"]["common"]["innings"]
        except Exception:
            return None

    def _latest_innings_fow(self):
        return self.json["centre"].get("fow")

    def _team_1(self):
        return self.json["team"][0]

    def _team_1_id(self):
        return self._team_1()["team_id"]

    def _team_1_abbreviation(self):
        return self._team_1()["team_abbreviation"]

    def _team_1_players(self):
        return self._team_1().get("player", [])

    def _team_1_innings(self):
        try:
            return [
                inn for inn in self.json["innings"]
                if inn["batting_team_id"] == self._team_1_id()
            ][0]
        except Exception:
            return None

    def _team_1_run_rate(self):
        try:
            return float(self._team_1_innings()["run_rate"])
        except Exception:
            return None

    def _team_1_overs_batted(self):
        try:
            return float(self._team_1_innings()["overs"])
        except Exception:
            return None

    def _team_1_batting_result(self):
        try:
            return self._team_1_innings()["event_name"]
        except Exception:
            return None

    def _team_2(self):
        return self.json["team"][1]

    def _team_2_id(self):
        return self._team_2()["team_id"]

    def _team_2_abbreviation(self):
        return self._team_2()["team_abbreviation"]

    def _team_2_players(self):
        return self._team_2().get("player", [])

    def _team_2_innings(self):
        try:
            return [
                inn for inn in self.json["innings"]
                if inn["batting_team_id"] == self._team_2_id()
            ][0]
        except Exception:
            return None

    def _team_2_run_rate(self):
        try:
            return float(self._team_2_innings()["run_rate"])
        except Exception:
            return None

    def _team_2_overs_batted(self):
        try:
            return float(self._team_2_innings()["overs"])
        except Exception:
            return None

    def _team_2_batting_result(self):
        try:
            return self._team_2_innings()["event_name"]
        except Exception:
            return None

    def _home_team(self):
        if self._team_1_id() == self.match_json()["home_team_id"]:
            return self._team_1_abbreviation()
        return self._team_2_abbreviation()

    def _batting_first(self):
        if self._team_1_id() == self.match_json()["batting_first_team_id"]:
            return self._team_1_abbreviation()
        return self._team_2_abbreviation()

    def _match_winner(self):
        if self._team_1_id() == self.match_json()["winner_team_id"]:
            return self._team_1_abbreviation()
        return self._team_2_abbreviation()

    def _toss_winner(self):
        if self._team_1_id() == self.match_json()["toss_winner_team_id"]:
            return self._team_1_id()
        return self._team_2_id()

    def _toss_decision(self):
        if self.match_json()["toss_decision"] == "" and len(self.innings) > 0:
            if self.innings[0]["batting_team_id"] == self.toss_winner:
                decision = "1"
            else:
                decision = "2"
        else:
            decision = self.match_json()["toss_decision"]
        return decision

    def _toss_decision_name(self):
        if self.match_json()["toss_decision_name"] == "" and len(self.innings) > 0:
            if self.innings[0]["batting_team_id"] == self.toss_winner:
                decision_name = "bat"
            else:
                decision_name = "bowl"
        else:
            decision_name = self.match_json()["toss_decision_name"]
        return decision_name

    def _toss_choice_team_id(self):
        return self.match_json()["toss_choice_team_id"]

    def _toss_winner_team_id(self):
        return self.match_json()["toss_winner_team_id"]

    # ------------------------------------------------------------------
    # Content / scorecard accessors (formerly comms_json methods)
    # ------------------------------------------------------------------

    def _rosters(self):
        try:
            return self.json["_match_players"]
        except Exception:
            return None

    def _all_innings(self):
        try:
            return self.json["_content"]["innings"]
        except Exception:
            return self.json["innings"]

    def batsmen(self, innings):
        try:
            return self.json["innings"][innings - 1]["inningBatsmen"]
        except Exception:
            return None

    def bowlers(self, innings):
        try:
            return self.json["innings"][innings - 1]["inningBowlers"]
        except Exception:
            return None

    def extras(self, innings):
        try:
            inn = self.json["innings"][innings - 1]
            return {
                "extras": inn.get("extras"),
                "byes": inn.get("byes"),
                "legbyes": inn.get("legbyes"),
                "wides": inn.get("wides"),
                "noballs": inn.get("noballs"),
            }
        except Exception:
            return None

    def fows(self, innings):
        try:
            return self.json["innings"][innings - 1]["inningFallOfWickets"]
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Scorecard helpers
    # ------------------------------------------------------------------

    def _batting_entry(self, raw: dict) -> dict:
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
            "name":        player.get("name"),
            "full_name":   player.get("longName"),
            "player_id":   player.get("objectId"),
            "runs":        raw.get("runs") if batted else None,
            "balls":       raw.get("balls") if batted else None,
            "minutes":     raw.get("minutes") if batted else None,
            "fours":       raw.get("fours") if batted else None,
            "sixes":       raw.get("sixes") if batted else None,
            "strike_rate": raw.get("strikerate") if batted else None,
            "is_out":      is_out,
            "dismissal":   dismissal,
            "batted":      batted,
        }

    @property
    def batting_scorecard(self) -> list:
        """
        Return batting scorecard for all innings as ``list[list[dict]]``.

        Outer list is indexed by innings order; inner list has one entry
        per batsman. Players who did not bat have ``batted=False`` and
        numeric fields as ``None``.

        Example::

            for i, innings in enumerate(m.batting_scorecard, 1):
                print(f"Innings {i}:")
                for b in innings:
                    print(f"  {b['name']}: {b['runs']} ({b['balls']}) - {b['dismissal']}")
        """
        result = []
        for i in range(1, len(self.innings) + 1):
            raw_list = self.batsmen(i)
            if raw_list:
                result.append([self._batting_entry(r) for r in raw_list])
            else:
                result.append([])
        return result

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_recent_matches(date=None) -> list[MatchRef]:
        """
        Return a list of :class:`~espncricinfo.match_ref.MatchRef` objects from the results page.

        Fetches https://www.espncricinfo.com/live-cricket-match-results
        (optionally with ?date=YYYY-MM-DD) and extracts match data from
        __NEXT_DATA__ at props.appPageProps.data.data.content.matches.
        """
        if date:
            url = f"https://www.espncricinfo.com/live-cricket-match-results?date={date}"
        else:
            today = _date.today().isoformat()
            url = f"https://www.espncricinfo.com/live-cricket-match-results?date={today}"

        next_data = _playwright_fetch(url)
        try:
            matches = (
                next_data["props"]["appPageProps"]["data"]["data"]
                ["content"]["matches"]
            )
        except (KeyError, TypeError):
            return []

        results = []
        for m in matches:
            try:
                series_id = m["series"]["objectId"]
                match_id = m["objectId"]
                results.append(MatchRef(series_id=series_id, match_id=match_id))
            except (KeyError, TypeError):
                continue
        return results
