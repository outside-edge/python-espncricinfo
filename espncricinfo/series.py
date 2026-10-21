import requests

from espncricinfo._core import collection_refs, get_json
from espncricinfo.exceptions import NoSeriesError
from espncricinfo.match_ref import MatchRef
from espncricinfo.seasons import Season


class Series(object):
    def __init__(self, series_id):
        self.series_id = series_id
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/".format(
            str(series_id)
        )
        self.events_url = (
            "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/events".format(
                str(series_id)
            )
        )
        self.seasons_url = (
            "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/seasons".format(
                str(series_id)
            )
        )
        self.headers = {"user-agent": "Mozilla/5.0"}
        self.json = self.get_json(self.json_url)
        self.seasons = self._get_seasons()
        self.years = self._get_years_from_seasons()
        self._season_objects = None
        self._current_season = None
        self._match_refs = None
        self._current_matches = None
        if self.json:
            self.name = self.json["name"]
            self.short_name = self.json["shortName"]
            self.abbreviation = self.json["abbreviation"]
            self.slug = self.json["slug"]
            self.is_tournament = self.json["isTournament"]
            self.url = self.json["links"][0]["href"]
            self.events_json = self._get_events()

        if self.events_json:
            self.events = self._build_events()

    def get_json(self, url):
        r = requests.get(url, headers=self.headers)
        if r.status_code == 404:
            raise NoSeriesError("Series not found")
        else:
            return r.json()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _get_seasons(self):
        season_json = self.get_json(self.seasons_url)
        if season_json:
            return [x["$ref"] for x in season_json["items"]]
        else:
            return None

    def _get_years_from_seasons(self):
        return [x.split("/")[9] for x in self.seasons]

    def _get_events(self):
        events_json = self.get_json(self.events_url)
        if events_json:
            return [x for x in events_json["items"]]
        else:
            return None

    def _build_events(self):
        events = []
        for event in self.events_json:
            events.append(self.get_json(event["$ref"]))
        return events

    @property
    def season_objects(self):
        if self._season_objects is None:
            self._season_objects = [Season.from_reference(url) for url in self.seasons]
        return self._season_objects

    @property
    def current_season(self):
        if self._current_season is None:
            reference = (self.json.get("season") or {}).get("$ref")
            self._current_season = (
                Season.from_reference(reference) if reference else None
            )
        return self._current_season

    @property
    def matches(self):
        if self._match_refs is None:
            if self.seasons:
                self._match_refs = list(
                    dict.fromkeys(
                        ref
                        for season in self.season_objects
                        for ref in season.match_refs
                    )
                )
            else:
                reference = (self.json.get("events") or {}).get("$ref")
                urls = collection_refs(reference or self.events_url, NoSeriesError)
                self._match_refs = [MatchRef.from_core_event_url(url) for url in urls]
        return self._match_refs

    @property
    def current_matches(self):
        if self._current_matches is None:
            active = []
            for ref in self.matches:
                url = (
                    "http://core.espnuk.org/v2/sports/cricket/leagues/"
                    f"{ref.series_id}/events/{ref.match_id}"
                )
                event = get_json(url, NoSeriesError)
                for competition in event.get("competitions", []):
                    status_url = (competition.get("status") or {}).get("$ref")
                    if status_url and (
                        get_json(status_url, NoSeriesError).get("type", {}).get("state")
                        == "in"
                    ):
                        active.append(ref)
                        break
            self._current_matches = active
        return self._current_matches
