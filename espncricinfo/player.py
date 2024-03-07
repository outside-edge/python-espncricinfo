import requests
from bs4 import BeautifulSoup
import dateparser
from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.match import Match
import csv

class Player(object):

    def __init__(self, player_id):
        self.player_id=player_id
        self.url = "https://www.espncricinfo.com/player/player-name-{0}".format(str(player_id))
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/athletes/{0}".format(str(player_id))
        self.new_json_url = "https://hs-consumer-api.espncricinfo.com/v1/pages/player/home?playerId={0}".format(str(player_id))
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self.parsed_html = self.get_html() 
        self.json = self.get_json()       
        self.new_json = self.get_new_json()
        self.cricinfo_id = str(player_id)
        self.__unicode__ = self._full_name()
        self.name = self._name()
        self.first_name = self._first_name()
        self.full_name = self._full_name()
        self.date_of_birth = self._date_of_birth()
        self.current_age = self._current_age()
        self.playing_role = self._playing_role()
        self.batting_style = self._batting_style()
        self.bowling_style = self._bowling_style()
        self.major_teams = self._major_teams()

    def get_html(self):
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def get_json(self):
        r = requests.get(self.json_url, headers=self.headers)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            return r.json()
        
    def get_new_json(self):
        r = requests.get(self.new_json_url, headers=self.headers)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            return r.json()

    def _name(self):
        return self.json['name']

    def _first_name(self):
        return self.json['firstName']

    def _middle_name(self):
        return self.json['middleName']

    def _last_name(self):
        return self.json['lastName']

    def _full_name(self):
        return self.json['fullName']

    def _date_of_birth(self):
        return self.json['dateOfBirth']

    def _current_age(self):
        return self.json['age']

    def _major_teams(self):
        return [x['team']['longName'] for x in self.new_json['content']['teams']]

    def _playing_role(self):
        return self.json['position']

    def _batting_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'batting'), None)

    def _bowling_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'bowling'), None)

    def in_team_for_match(self, match_id):
        m = Match(match_id)
        if next((p for p in m.team_1_players if p['object_id'] == self.cricinfo_id), None) or next((p for p in m.team_2_players if p['object_id'] == self.cricinfo_id), None):
            return True
        else:
            return False

    def batting_for_match(self, match_id):
        batting_stats = []
        m = Match(match_id)
        for innings in list(m.full_scorecard['innings'].keys()):
            stats = next((x for x in m.full_scorecard['innings'][innings]['batsmen'] if x['href'] == self.url), None)
            if stats:
                batting_stats.append({ 'innings': innings, 'balls_faced': next((x['value'] for x in stats['stats'] if x['name'] == 'ballsFaced'), None), 'minutes': next((x['value'] for x in stats['stats'] if x['name'] == 'minutes'), None), 'runs': next((x['value'] for x in stats['stats'] if x['name'] == 'runs'), None), 'fours': next((x['value'] for x in stats['stats'] if x['name'] == 'fours'), None), 'sixes': next((x['value'] for x in stats['stats'] if x['name'] == 'sixes'), None), 'strike_rate': next((x['value'] for x in stats['stats'] if x['name'] == 'strikeRate'), None) })
        return batting_stats

    def bowling_for_match(self, match_id):
        bowling_stats = []
        m = Match(match_id)
        for innings in list(m.full_scorecard['innings'].keys()):
            stats = next((x for x in m.full_scorecard['innings'][innings]['bowlers'] if x['href'] == self.url), None)
            if stats:
                bowling_stats.append({ 'innings': innings, 'overs': next((x['value'] for x in stats['stats'] if x['name'] == 'overs')), 'maidens': next((x['value'] for x in stats['stats'] if x['name'] == 'maidens')), 'conceded': next((x['value'] for x in stats['stats'] if x['name'] == 'conceded')), 'wickets': next((x['value'] for x in stats['stats'] if x['name'] == 'wickets')), 'economy_rate': next((x['value'] for x in stats['stats'] if x['name'] == 'economyRate')), 'dots': next((x['value'] for x in stats['stats'] if x['name'] == 'dots'), None), 'fours_conceded': next((x['value'] for x in stats['stats'] if x['name'] == 'foursConceded'), None), 'sixes_conceded': next((x['value'] for x in stats['stats'] if x['name'] == 'sixesConceded'), None), 'wides': next((x['value'] for x in stats['stats'] if x['name'] == 'wides'), None), 'no_balls': next((x['value'] for x in stats['stats'] if x['name'] == 'noballs'), None)})
        return bowling_stats

    def get_career_averages(self, file_name=None, match_format=11, data_type='allround') :

        """Get Player career averages

        Arguements:
            file_name {string}: File name to save data
            match_format {int}: Match format (default is 11) (1-Test), (2-Odi) (3-T20I), (11-All International), (20-Youth Tests), (21-Youth ODI)
            data_type {string}: Data type (default is allround) (allround, batting, bowling, fielding)
        
        Return:
            Data in csv file
        """
        self.match_format = match_format
        self.data_type = data_type
        self.file_name = file_name

        if self.file_name is None:
            self.file_name = f"{self.player_id}_{self.match_format}_{self.data_type}_career_averages.csv"

        self.url=f"https://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class={self.match_format};template=results;type={self.data_type}"
        html_doc = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        tables = soup.find_all("table")[2]
        table_rows = tables.find_all("tr")
        scores =[]
        for tr in table_rows:
            scores.append(tr.text)
        with open(self.file_name, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for row in scores:
                    writer.writerow(row.splitlines()) 
    
    def get_career_summary(self, file_name=None, match_format=11, data_type='allround'):
        
        """Get Player data match by match sorted by date

        Arguements:
            file_name {string}: File name to save data
            match_format {int}: Match format (default is 11) (1-Test), (2-Odi) (3-T20I), (11-All International), (20-Youth Tests), (21-Youth ODI)
            data_type {string}: Data type (default is allround) (allround, batting, bowling, fielding)
        
        Return:
            Data in csv file
        """
        self.match_format = match_format
        self.data_type = data_type
        self.file_name = file_name

        if self.file_name is None:
            self.file_name = f"{self.player_id}_{self.match_format}_{self.data_type}_career_summary.csv"

        self.url=f"https://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class={self.match_format};template=results;type={self.data_type}"
        html_doc = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        tables = soup.find_all("table")[3]
        table_rows = tables.find_all("tr")
        scores =[]
        for tr in table_rows:
            scores.append(tr.text)
        with open(self.file_name, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for row in scores:
                    writer.writerow(row.splitlines())

    def get_data(self, file_name=None, match_format=11, data_type='allround', view='match'):

        """Get Player data match by match sorted by date

        Arguements:
            file_name {string}: File name to save data
            match_format {int}: Match format (default is 11) (1-Test), (2-Odi) (3-T20I), (11-All International), (20-Youth Tests), (21-Youth ODI)
            data_type {string}: Data type (default is allround) (allround, batting, bowling, fielding)
            view {string}: View type (default is match) (match, innings, cumulative, reverse_cumulative, series, tour, ground)
        
        Return:
            Data in csv file
        """
        self.match_format = match_format
        self.data_type = data_type
        self.view = view
        self.file_name = file_name

        if self.file_name is None:
            self.file_name = f"{self.player_id}_{self.match_format}_{self.data_type}_{self.view}.csv"

        self.url=f"https://stats.espncricinfo.com/ci/engine/player/{self.player_id}.html?class={self.match_format};template=results;type={self.data_type};view={self.view}"
        html_doc = requests.get(self.url, headers=self.headers())
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        tables = soup.find_all("table")[3]
        table_rows = tables.find_all("tr")
        scores =[]
        for tr in table_rows:
            scores.append(tr.text)
        with open(self.file_name, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for row in scores:
                    writer.writerow(row.splitlines())