"""Teams within a series from the ESPN core API."""

from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any

from espncricinfo._core import collection_refs, get_json, reference_ids
from espncricinfo.exceptions import NoTeamError
from espncricinfo.match_ref import MatchRef

if TYPE_CHECKING:
    from espncricinfo.player import Player


class Team:
    """A team as it appears in one series."""

    #: ESPNcricinfo team id.
    id: int
    #: ESPNcricinfo series (league) id.
    series_id: int
    #: Core API URL of the team within the series.
    url: str
    #: ``'Chennai Super Kings'``.
    name: str | None
    #: Abbreviation, e.g. ``'CSK'``.
    short_name: str | None
    #: Home location, or None.
    location: str | None
    #: Nickname, or None.
    nickname: str | None
    #: URL slug.
    slug: str | None
    #: Team color as hex, or None.
    color: str | None
    #: Logo URL, or None.
    logo: str | None
    #: True for national sides.
    is_national: bool | None
    #: True if ESPN marks the team active.
    is_active: bool | None
    #: Start of the team's linked match (UTC), or None.
    match_date: datetime | None
    #: The team's linked match in this series, or None.
    match: MatchRef | None
    #: The core API team record.
    json: dict[str, Any]

    def __init__(self, team_id: int | str, series_id: int | str) -> None:
        """Load the team record.

        Args:
            team_id: ESPNcricinfo team id.
            series_id: ESPNcricinfo series (league) id.
        """
        self.id = int(team_id)
        self.series_id = int(series_id)
        self.url = (
            "http://core.espnuk.org/v2/sports/cricket/leagues/"
            f"{self.series_id}/teams/{self.id}"
        )
        self.json = get_json(self.url, NoTeamError)
        self.name = self.json.get("name")
        self.short_name = self.json.get("abbreviation")
        self.location = self.json.get("location")
        self.nickname = self.json.get("nickname")
        self.slug = self.json.get("slug")
        self.color = self.json.get("color")
        self.logo = next(
            (logo["href"] for logo in self.json.get("logos", []) if "href" in logo),
            None,
        )
        self.is_national = self.json.get("isNational")
        self.is_active = self.json.get("isActive")
        event = self.json.get("event") or {}
        self.match_date = (
            datetime.fromisoformat(event["date"]) if event.get("date") else None
        )
        self.match = (
            MatchRef.from_core_event_url(event["$ref"]) if event.get("$ref") else None
        )

    @classmethod
    def from_reference(cls, url: str) -> Team:
        """Build a Team from a core API team URL."""
        series_id, team_id = reference_ids(url, "teams")
        return cls(team_id, series_id)

    @cached_property
    def players(self) -> list[Player]:
        """The squad as Players, loaded on first access (one request each)."""
        from espncricinfo.player import Player

        athletes = self.json.get("athletes") or {}
        if not athletes.get("$ref"):
            return []
        return [
            Player(int(url.rstrip("/").rsplit("/", 1)[-1]))
            for url in collection_refs(athletes["$ref"], NoTeamError)
        ]

    def __repr__(self) -> str:
        """Return a constructor-style summary."""
        return f"Team(id={self.id}, series_id={self.series_id}, name={self.name!r})"
