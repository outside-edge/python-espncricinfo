import json
import requests
from datetime import datetime
from espncricinfo.exceptions import MatchNotFoundError, NoTeamError
from espncricinfo.match import Match

class Team:
    def __init__(self, team_id, league_id=8081):
        self.id = team_id
        self.json_url = f"http://core.espnuk.org/v2/sports/cricket/leagues/{league_id}/teams/{series_id}/"
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self.json = self.get_json(self.json_url)
        
        if self.json:
            self.location = self.json.get('location')
            self.name = self.json.get('name')
            self.nickname = self.json.get('nickname')
            self.short_name = self.json.get('abbreviation')
            self.slug = self.json.get('slug')
            self.color = self.json.get('color')
            self.logo = next((logo.get("href") for logo in data.get("logos", []) if "href" in logo), None)
            self.is_national = self.json.get('slug')
            self.is_active = self.json.get('is_active')
            self.match_date = self.parse_date(self.json.get('event').get('date'))
            self._match_url = self.json.get('event').get('$ref')
            self.match = Match(self.match_url.split("/events/")[-1])
            self._players_url = self.json.get('athletes').get('$ref')
            self._players = []
    
    @property
    def players(self):
        if not self._players:
            from espncricinfo.player import Player
            players_json = self.get_json(self._players_url)
            if players_json:
                player_urls = [x['$ref'] for x in players_json['items']]
                for url in player_urls:
                    player_ = Player(url.split("/athletes/")[-1])
                    self._players.append(player_)
        return self._players
    
    def get_json(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            raise NoTeamError("Season not found.")
        return response.json()
    
    def parse_date(self, date_str):
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")
        return None

    def __repr__(self):
        return f"Team({self.team_id}, {self.name}, {self.short_name})"
