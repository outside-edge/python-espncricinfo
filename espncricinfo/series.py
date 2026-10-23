"""Series (ESPN "league") records from the ESPN core API."""

import re
from functools import cached_property
from typing import Any

from espncricinfo import _core
from espncricinfo._core import collection_refs, get_json
from espncricinfo.exceptions import NoSeasonError, NoSeriesError
from espncricinfo.match_ref import MatchRef
from espncricinfo.seasons import Season

_LEAGUES = "http://core.espnuk.org/v2/sports/cricket/leagues"
_SEASON_KEY = re.compile(r"(\d{4})(?:[/-](\d{2}|\d{4}))?")


class Series:
    """A series or league, with its seasons, teams and matches.

    Example values are for ``Series(1449924)``, the Indian Premier League.
    """

    #: ESPNcricinfo series (league) id.
    series_id: int
    #: ``'Indian Premier League'``.
    name: str
    #: Short name, e.g. ``'IPL'``.
    short_name: str
    #: ESPN abbreviation.
    abbreviation: str
    #: URL slug.
    slug: str
    #: True for tournaments, False for bilateral series.
    is_tournament: bool
    #: ESPNcricinfo web page for the series.
    url: str | None
    #: Core API URLs of the series' seasons.
    seasons: list[str]
    #: Season years as strings, e.g. ``['2008', ..., '2025']``.
    years: list[str]
    #: The core API series record.
    json: dict[str, Any]

    def __init__(self, series_id: int | str) -> None:
        """Load the series record and its list of seasons.

        Args:
            series_id: ESPNcricinfo series (league) id.
        """
        self.series_id = int(series_id)
        self.json = self._get_json(f"{_LEAGUES}/{self.series_id}/")
        self.name = self.json["name"]
        self.short_name = self.json["shortName"]
        self.abbreviation = self.json["abbreviation"]
        self.slug = self.json["slug"]
        self.is_tournament = bool(self.json.get("isTournament"))
        links = self.json.get("links") or []
        self.url = links[0]["href"] if links else None
        self.seasons = collection_refs(
            f"{_LEAGUES}/{self.series_id}/seasons", NoSeriesError
        )
        self.years = [ref.rstrip("/").rsplit("/", 1)[-1] for ref in self.seasons]

    def _get_json(self, url: str) -> dict[str, Any]:
        response = _core.http_get(url)
        if response.status_code == 404:
            raise NoSeriesError(f"Series not found: {self.series_id}")
        response.raise_for_status()
        return response.json()

    def __str__(self) -> str:
        """Return the series name."""
        return self.name

    def __repr__(self) -> str:
        """Return ``Series(series_id)``."""
        return f"Series({self.series_id})"

    @cached_property
    def events(self) -> list[dict[str, Any]]:
        """Core API event records for the series' first page of events.

        One request per event, made on first access.
        """
        refs = self._get_json(f"{_LEAGUES}/{self.series_id}/events").get("items", [])
        return [self._get_json(item["$ref"]) for item in refs]

    @cached_property
    def season_objects(self) -> list[Season]:
        """Every season of the series, loaded on first access."""
        return [Season.from_reference(url) for url in self.seasons]

    def season(self, key: int | str) -> Season:
        """Return one season, by year or by ESPNcricinfo's two-year label.

        Multi-year seasons live under their own series id, which this exposes
        as ``season.series_id``: for the Big Bash League,
        ``Series(8044).season("2024/25").series_id`` is ``1443056``.

        Args:
            key: ``2024``, ``"2024"``, ``"2024/25"``, ``"2024-25"`` or
                ``"2024/2025"``. A bare year matches the season starting then.

        Returns:
            The matching season.

        Raises:
            NoSeasonError: If the series has no such season.
        """
        match = _SEASON_KEY.fullmatch(str(key).strip())
        if match is None:
            raise NoSeasonError(f"Not a season year or label: {key!r}")
        start, end = match.groups()
        ref = next(
            (r for r in self.seasons if r.rstrip("/").endswith(f"/{start}")), None
        )
        if ref is None:
            raise NoSeasonError(f"{self.name} has no season starting in {start}")
        season = Season.from_reference(ref)
        if end is not None and season.label != f"{start}/{end[-2:]}":
            raise NoSeasonError(
                f"{self.name} {start} season is labeled {season.label!r}, not {key!r}"
            )
        return season

    @cached_property
    def current_season(self) -> Season | None:
        """The season ESPN marks as current, or None."""
        reference = (self.json.get("season") or {}).get("$ref")
        return Season.from_reference(reference) if reference else None

    @cached_property
    def matches(self) -> list[MatchRef]:
        """MatchRefs for every match across all seasons, without duplicates."""
        if self.seasons:
            return list(
                dict.fromkeys(
                    ref for season in self.season_objects for ref in season.match_refs
                )
            )
        reference = (self.json.get("events") or {}).get("$ref")
        urls = collection_refs(
            reference or f"{_LEAGUES}/{self.series_id}/events", NoSeriesError
        )
        return [MatchRef.from_core_event_url(url) for url in urls]

    @cached_property
    def current_matches(self) -> list[MatchRef]:
        """Matches whose ESPN status is in progress (two requests per match)."""
        active = []
        for ref in self.matches:
            event = get_json(
                f"{_LEAGUES}/{ref.series_id}/events/{ref.match_id}", NoSeriesError
            )
            for competition in event.get("competitions", []):
                status_url = (competition.get("status") or {}).get("$ref")
                if status_url and (
                    get_json(status_url, NoSeriesError).get("type", {}).get("state")
                    == "in"
                ):
                    active.append(ref)
                    break
        return active
