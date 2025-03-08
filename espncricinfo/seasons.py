import requests
from datetime import datetime
from espncricinfo.exceptions import NoSeasonError

class Season:
    def __init__(self, season_id, series_id=8039):
        self.id = season_id
        self.series_id = series_id
        self.json_url = f"http://core.espnuk.org/v2/sports/cricket/leagues/{series_id}/seasons/{season_id}"        
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self.json = self.get_json(self.json_url)
        
        if self.json:
            self.year = self.json.get('year')
            self.start_date = self.parse_date(self.json.get('startDate'))
            self.end_date = self.parse_date(self.json.get('endDate'))
            self.name = self.json.get('name')
            self.short_name = self.json.get('shortName')
            self.slug = self.json.get('slug')
            self._teams_url = self.json.get('teams', {}).get('$ref')
            self._series = None
            self._teams = []
            self.rankings_url = self.json.get('rankings', {}).get('$ref')
    
    @property
    def series(self):
        if self._series is None:
            from espncricinfo.series import Series
            links = self.json.get('links', [])
            if links and len(links)>5:
                series_url = links[5]["href"]
                series_id = series_url.split("/series/")[-1].split(".html")[0]
                self._series = Series(series_id)
        return self._series
    
    @property
    def teams(self):
        if self._teams is None:
            from espncricinfo.teams import Team
            teams_json = self.get_json(self._teams_url)
            teams_ = teams_json.get('items', [])
            for t in teams_:
                team_id = t.split("/teams/")[-1]
                team_ = Team(team_id)
                self._teams.append(team_)
        return self._teams
    
    def get_json(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            raise NoSeasonError("Season not found.")
        return response.json()
    
    def parse_date(self, date_str):
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")
        return None
    
    def __str__(self):
        return self.name if self.name else "Unknown Season"
    
    def __repr__(self):
        return f"Season(id={self.id}, year={self.year}, name={self.name}, start_date={self.start_date}, end_date={self.end_date})"
