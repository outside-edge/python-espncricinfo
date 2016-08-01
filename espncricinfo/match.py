import requests
from espncricinfo.exceptions import NoMatchFoundError

class Match(object):

    def __init__(self, match_id):
        self.match_id = match_id
        self.match_url = "http://www.espncricinfo.com/matches/engine/match/{0}.html".format(str(match_id))
        self.json_url = "http://www.espncricinfo.com/matches/engine/match/{0}.json".format(str(match_id))
        self.json = self.get_json()
        if self.json:
            self.__unicode__ = self.description()

    def get_json(self):
        r = requests.get(self.json_url)
        if r.status_code == 404:
            raise NoMatchFoundError
        else:
            return r.json()

    def match_json(self):
        return self.json['match']

    def status(self):
        return self.match_json()['match_status']

    def match_class(self):
        if self.match_json()['international_class_card'] != "":
            return self.match_json()['international_class_card']
        else:
            return self.match_json()['general_class_card']

    def season(self):
        return self.match_json()['season']

    def description(self):
        return self.json['description']

    def series(self):
        return self.json['series']

    def officials(self):
        return self.json['official']

    # live matches only
    def current_summary(self):
        if self.match_json().has_key('current_summary'):
            return self.match_json()['current_summary']

    def present_datetime_local(self):
        return self.match_json()['present_datetime_local']

    def present_datetime_gmt(self):
        return self.match_json()['present_datetime_gmt']

    def start_datetime_local(self):
        return self.match_json()['start_datetime_local']

    def start_datetime_gmt(self):
        return self.match_json()['start_datetime_gmt']

    def cancelled_match(self):
        if self.match_json()['cancelled_match'] == 'N':
            return False
        else:
            return True

    def rain_rule(self):
        if self.match_json()['rain_rule'] == "1":
            return self.match_json()['rain_rule_name']
        else:
            return None

    def date(self):
        return self.match_json()['start_date_raw']

    def continent(self):
        return self.match_json()['continent_name']

    def town_area(self):
        return self.match_json()['town_area']

    def town_name(self):
        return self.match_json()['town_name']

    def town_id(self):
        return self.match_json()['town_id']

    def weather_location_code(self):
        return self.match_json()['weather_location_code']

    def match_title(self):
        return self.match_json()['cms_match_title']

    def result(self):
        return self.json['live']['status']

    def ground_id(self):
        return self.match_json()['ground_id']

    def ground_name(self):
        return self.match_json()['ground_name']

    def lighting(self):
        return self.match_json()['floodlit_name']

    def followon(self):
        if self.match_json()['followon'] == '1':
            return True
        else:
            return False

    def scheduled_overs(self):
        return int(self.match_json()['scheduled_overs'])

    def innings_list(self):
        return self.json['centre']['common']['innings_list']

    def innings(self):
        return self.json['innings']

    def latest_batting(self):
        return self.json['centre']['common']['batting']

    def latest_bowling(self):
        return self.json['centre']['common']['bowling']

    def latest_innings(self):
        return self.json['centre']['common']['innings']

    def latest_innings_fow(self):
        if self.json['centre'].has_key('fow'):
            return self.json['centre']['fow']
        else:
            return None

    def team_1(self):
        return self.json['team'][0]

    def team_1_id(self):
        return self.team_1()['team_id']

    def team_1_abbreviation(self):
        return self.team_1()['team_abbreviation']

    def team_1_players(self):
        return self.team_1()['player']

    def team_1_innings(self):
        return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self.team_1_id()][0]

    def team_1_run_rate(self):
        return float(self.team_1_innings()['run_rate'])

    def team_1_overs_batted(self):
        return float(self.team_1_innings()['overs'])

    def team1_batting_result(self):
        return self.team_1_innings()['event_name']

    def team_2(self):
        return self.json['team'][1]

    def team_2_id(self):
        return self.team_2()['team_id']

    def team_2_abbreviation(self):
        return self.team_2()['team_abbreviation']

    def team_2_players(self):
        return self.team_2()['player']

    def team_2_innings(self):
        return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self.team_2_id()][0]

    def team_2_run_rate(self):
        return float(self.team_2_innings()['run_rate'])

    def team_2_overs_batted(self):
        return float(self.team_2_innings()['overs'])

    def team2_batting_result(self):
        return self.team_2_innings()['event_name']

    def home_team(self):
        if self.team_1_id() == self.match_json()['home_team_id']:
            return self.team_1_abbreviation()
        else:
            return self.team_2_abbreviation()

    def batting_first(self):
        if self.team_1_id() == self.match_json()['batting_first_team_id']:
            return self.team_1_abbreviation()
        else:
            return self.team_2_abbreviation()

    def match_winner(self):
        if self.team_1_id() == self.match_json()['winner_team_id']:
            return self.team_1_abbreviation()
        else:
            return self.team_2_abbreviation()

    def toss_winner(self):
        if self.team_1_id() == self.match_json()['toss_winner_team_id']:
            return self.team_1_id()
        else:
            return self.team_2_id()

    def toss_decision(self):
        return self.match_json()['toss_decision_name']
