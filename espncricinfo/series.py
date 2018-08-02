import requests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import MatchNotFoundError, NoSeriesError

class Series(object):

    def __init__(self, series_id):
        self.series_id = series_id
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/".format(str(series_id))
        self.events_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/events".format(str(series_id))
        self.seasons_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/seasons".format(str(series_id))
        self.json = self.get_json(self.json_url)
        if self.json:
            self.name = self.json['name']
            self.short_name = self.json['shortName']
            self.abbreviation = self.json['abbreviation']
            self.slug = self.json['slug']
            self.is_tournament = self.json['isTournament']
            self.url = self.json['links'][0]['href']
            self.season_json = self._get_season()
            self.events_json = self._get_events()

        if self.season_json:
            self.year = self.season_json['year']
            self.start_date = self.season_json['startDate']
            self.end_date = self.season_json['endDate']

        if self.events_json:
            self.events = self._build_events()

    def get_json(self, url):
        r = requests.get(url)
        if r.status_code == 404:
            raise "Not Found"
        else:
            return r.json()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _get_season(self):
        season_json = self.get_json(self.json['season']['$ref'])
        if season_json:
            return season_json
        else:
            return None

    def _get_events(self):
        events_json = self.get_json(self.events_url)
        if events_json:
            return events_json['items']
        else:
            return None

    def _build_events(self):
        events = []
        for event in self.events_json:
            events.append(self.get_json(event['$ref']))
        return events
