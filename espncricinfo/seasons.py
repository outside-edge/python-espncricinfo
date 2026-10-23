"""Seasons of a series from the ESPN core API."""

from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any

from espncricinfo._core import collection_refs, get_json, reference_ids
from espncricinfo.exceptions import NoSeasonError
from espncricinfo.match_ref import MatchRef
from espncricinfo.teams import Team

if TYPE_CHECKING:
    from espncricinfo.series import Series


class Season:
    """One season of a series, with its teams and matches."""

    #: Season id, usually the year.
    id: int
    #: ESPNcricinfo series (league) id.
    series_id: int
    #: Core API URL of the season.
    url: str
    #: ESPN's season year, the year the season starts: ``2024`` for 2024/25.
    year: int
    #: ESPNcricinfo's label: ``'2024/25'`` for a season that crosses New Year,
    #: otherwise the year, e.g. ``'2025'``.
    label: str
    #: ``'Indian Premier League 2025'``.
    name: str | None
    #: Short name, or None.
    short_name: str | None
    #: Start of the season (UTC), or None.
    start_date: datetime | None
    #: End of the season (UTC), or None.
    end_date: datetime | None
    #: The core API season record.
    json: dict[str, Any]

    def __init__(self, season_id: int | str, series_id: int | str) -> None:
        """Load the season record.

        Args:
            season_id: Season id, usually the year.
            series_id: ESPNcricinfo series (league) id.
        """
        self.id = int(season_id)
        self.series_id = int(series_id)
        self.url = (
            "http://core.espnuk.org/v2/sports/cricket/leagues/"
            f"{self.series_id}/seasons/{self.id}"
        )
        self.json = get_json(self.url, NoSeasonError)
        self.year = int(self.json.get("year", self.id))
        self.name = self.json.get("name")
        self.short_name = self.json.get("shortName")
        self.start_date = _parse_date(self.json.get("startDate"))
        self.end_date = _parse_date(self.json.get("endDate"))
        self.label = _label(self.year, self.start_date, self.end_date)

    @classmethod
    def from_reference(cls, url: str) -> Season:
        """Build a Season from a core API season URL."""
        series_id, season_id = reference_ids(url, "seasons")
        return cls(season_id, series_id)

    @cached_property
    def teams(self) -> list[Team]:
        """Teams in this season, loaded on first access (one request each)."""
        urls = collection_refs(f"{self.url}/teams", NoSeasonError)
        return [Team.from_reference(url) for url in urls]

    @cached_property
    def match_refs(self) -> list[MatchRef]:
        """MatchRefs for this season's matches, loaded on first access."""
        urls = collection_refs(f"{self.url}/events", NoSeasonError)
        return [MatchRef.from_core_event_url(url) for url in urls]

    @cached_property
    def series(self) -> Series:
        """The parent Series, loaded on first access."""
        from espncricinfo.series import Series

        return Series(self.series_id)

    def __str__(self) -> str:
        """Return the season name, or its year."""
        return self.name or str(self.year)

    def __repr__(self) -> str:
        """Return a constructor-style summary."""
        return f"Season(id={self.id}, series_id={self.series_id}, name={self.name!r})"


def _label(year: int, start: datetime | None, end: datetime | None) -> str:
    if start and end and end.year > start.year:
        return f"{start.year}/{end.year % 100:02d}"
    return str(year)


def _parse_date(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
