from datetime import datetime

from espncricinfo._core import collection_refs, get_json, reference_ids
from espncricinfo.exceptions import NoSeasonError
from espncricinfo.match_ref import MatchRef
from espncricinfo.teams import Team


class Season:
    def __init__(self, season_id, series_id):
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
        self.start_date = self._parse_date(self.json.get("startDate"))
        self.end_date = self._parse_date(self.json.get("endDate"))
        self._teams = None
        self._match_refs = None
        self._series = None

    @staticmethod
    def _parse_date(value):
        return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None

    @classmethod
    def from_reference(cls, url):
        series_id, season_id = reference_ids(url, "seasons")
        return cls(season_id, series_id)

    @property
    def teams(self):
        if self._teams is None:
            urls = collection_refs(f"{self.url}/teams", NoSeasonError)
            self._teams = [Team.from_reference(url) for url in urls]
        return self._teams

    @property
    def match_refs(self):
        if self._match_refs is None:
            urls = collection_refs(f"{self.url}/events", NoSeasonError)
            self._match_refs = [MatchRef.from_core_event_url(url) for url in urls]
        return self._match_refs

    @property
    def series(self):
        if self._series is None:
            from espncricinfo.series import Series

            self._series = Series(self.series_id)
        return self._series

    def __str__(self):
        return self.name or str(self.year)

    def __repr__(self):
        return f"Season(id={self.id}, series_id={self.series_id}, name={self.name!r})"
