import requests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import MatchNotFoundError, NoSeriesError

class Series(object):

    def __init__(self, series_id):
        self.series_id = series_id
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/".format(str(series_id))
        self.events_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/events".format(str(series_id))
        self.seasons_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/seasons".format(str(series_id))
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self.json = self.get_json(self.json_url)
        self.seasons = self._get_seasons()
        self.years = self._get_years_from_seasons()
        if self.json:
            self.name = self.json['name']
            self.short_name = self.json['shortName']
            self.abbreviation = self.json['abbreviation']
            self.slug = self.json['slug']
            self.is_tournament = self.json['isTournament']
            self.url = self.json['links'][0]['href']
            self.events_json = self._get_events()

        if self.events_json:
            self.events = self._build_events()

    def get_json(self, url):
        r = requests.get(url,headers=self.headers)
        if r.status_code == 404:
            raise "Not Found"
        else:
            return r.json()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _get_seasons(self):
        season_json = self.get_json(self.seasons_url)
        if season_json:
            return [x['$ref'] for x in season_json['items']]
        else:
            return None

    def _get_years_from_seasons(self):
        return [x.split('/')[9] for x in self.seasons]

    def _get_events(self):
        events_json = self.get_json(self.events_url)
        if events_json:
            return [x for x in events_json['items']]
        else:
            return None

    def _build_events(self):
        events = []
        for event in self.events_json:
            events.append(self.get_json(event['$ref']))
        return events
