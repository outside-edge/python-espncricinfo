import requests
import grequests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import MatchNotFoundError, NoSeriesError

class Series(object):

    def __init__(self, series_id):
        self.series_id = series_id
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/".format(str(series_id))
        self.events_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/events".format(str(series_id))
        self.seasons_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/seasons".format(str(series_id))
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
        r = requests.get(url)
        if r.status_code == 404:
            raise "Not Found"
        else:
            return r.json()

    def get_events_for_season(self, season):
        responses = []
        season_events = []
        season_events_url = self.seasons_url+"/{0}/events".format(str(season))
        season_events_json = self.get_json(season_events_url)
        if season_events_json:
            rs = (grequests.get(event['$ref']) for event in season_events_json['items'])
            responses = grequests.map(rs)
            for response in responses:
                event_json = response.json()
                venue_json = self.get_json(event_json['venues'][0]['$ref'])
                season_events.append({"url": event_json['$ref'], "match_id": event_json['id'], "class": event_json['competitions'][0]['class']['generalClassCard'], "date": event_json['date'], "description": event_json['shortDescription'], "venue_url": event_json['venues'][0]['$ref'], "venue": venue_json['fullName']})
            return season_events
        else:
            return None

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
