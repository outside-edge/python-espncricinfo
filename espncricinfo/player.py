import requests
from bs4 import BeautifulSoup
import dateparser
from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.match import Match

class Player(object):

    def __init__(self, player_id):
        self.url = "https://www.espncricinfo.com/player/player-name-{0}".format(str(player_id))
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/athletes/{0}".format(str(player_id))
        self.parsed_html = self.get_html()
        self.json = self.get_json()
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

        if self.parsed_html:
            self.major_teams = self._major_teams()

    def get_html(self):
        r = requests.get(self.url)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def get_json(self):
        r = requests.get(self.json_url)
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
        return [x.text for x in self.parsed_html.find('div', class_='overview-teams-grid').find_all('h5')]

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
