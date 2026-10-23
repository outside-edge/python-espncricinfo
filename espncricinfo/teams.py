"""Teams within a series from the ESPN core API."""

from datetime import datetime

from espncricinfo._core import collection_refs, get_json, reference_ids
from espncricinfo.exceptions import NoTeamError
from espncricinfo.match_ref import MatchRef


class Team:
    """A team as it appears in one series."""

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
        self._players = None

    @classmethod
    def from_reference(cls, url):
        """Build a Team from a core API team URL."""
        series_id, team_id = reference_ids(url, "teams")
        return cls(team_id, series_id)

    @property
    def players(self):
        """Squad as Player objects, loaded on first access (one request each)."""
        if self._players is None:
            from espncricinfo.player import Player

            athletes = self.json.get("athletes") or {}
            self._players = (
                [
                    Player(int(url.rstrip("/").rsplit("/", 1)[-1]))
                    for url in collection_refs(athletes["$ref"], NoTeamError)
                ]
                if athletes.get("$ref")
                else []
            )
        return self._players

    def __repr__(self):
        """Return a constructor-style summary."""
        return f"Team(id={self.id}, series_id={self.series_id}, name={self.name!r})"
