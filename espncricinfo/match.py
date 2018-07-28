import requests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError

class Match(object):

    def __init__(self, match_id):
        self.match_id = match_id
        self.match_url = "http://www.espncricinfo.com/matches/engine/match/{0}.html".format(str(match_id))
        self.json_url = "http://www.espncricinfo.com/matches/engine/match/{0}.json".format(str(match_id))
        self.json = self.get_json()
        if self.json:
            self.__unicode__ = self._description()
            self.status = self._status()
            self.match_class = self._match_class()
            self.season = self._season()
            self.description = self._description()
            self.series = self._series()
            self.series_name = self._series_name()
            self.officials = self._officials()
            self.current_summary = self._current_summary()
            self.present_datetime_local = self._present_datetime_local()
            self.present_datetime_gmt = self._present_datetime_gmt()
            self.start_datetime_local = self._start_datetime_local()
            self.start_datetime_gmt = self._start_datetime_gmt()
            self.cancelled_match = self._cancelled_match()
            self.rain_rule = self._rain_rule()
            self.date = self._date()
            self.continent = self._continent()
            self.town_area = self._town_area()
            self.town_name = self._town_name()
            self.town_id = self._town_id()
            self.weather_location_code = self._weather_location_code()
            self.match_title = self._match_title()
            self.result = self._result()
            self.ground_id = self._ground_id()
            self.ground_name = self._ground_name()
            self.lighting = self._lighting()
            self.followon = self._followon()
            self.scheduled_overs = self._scheduled_overs()
            self.innings_list = self._innings_list()
            self.innings = self._innings()
            self.latest_batting = self._latest_batting()
            self.latest_bowling = self._latest_bowling()
            self.latest_innings = self._latest_innings()
            self.latest_innings_fow = self._latest_innings_fow()
            self.team_1 = self._team_1()
            self.team_1_id = self._team_1_id()
            self.team_1_abbreviation = self._team_1_abbreviation()
            self.team_1_players = self._team_1_players()
            self.team_1_innings = self._team_1_innings()
            self.team_1_run_rate = self._team_1_run_rate()
            self.team_1_overs_batted = self._team_1_overs_batted()
            self.team_1_batting_result = self._team_1_batting_result()
            self.team_2 = self._team_2()
            self.team_2_id = self._team_2_id()
            self.team_2_abbreviation = self._team_2_abbreviation()
            self.team_2_players = self._team_2_players()
            self.team_2_innings = self._team_2_innings()
            self.team_2_run_rate = self._team_2_run_rate()
            self.team_2_overs_batted = self._team_2_overs_batted()
            self.team_2_batting_result = self._team_2_batting_result()
            self.home_team = self._home_team()
            self.batting_first = self._batting_first()
            self.match_winner = self._match_winner()
            self.toss_winner = self._toss_winner()
            self.toss_decision = self._toss_decision()
            self.toss_decision_name = self._toss_decision_name()
            self.toss_choice_team_id = self._toss_choice_team_id()
            self.toss_winner_team_id = self._toss_winner_team_id()

    def get_json(self):
        r = requests.get(self.json_url)
        if r.status_code == 404:
            raise MatchNotFoundError
        elif 'Scorecard not yet available' in r.text:
            raise NoScorecardError
        else:
            return r.json()

    def match_json(self):
        return self.json['match']

    def _status(self):
        return self.match_json()['match_status']

    def _match_class(self):
        if self.match_json()['international_class_card'] != "":
            return self.match_json()['international_class_card']
        else:
            return self.match_json()['general_class_card']

    def _season(self):
        return self.match_json()['season']

    def _description(self):
        return self.json['description']

    def _series(self):
        return self.json['series']

    def _series_name(self):
        try:
            return self.json['series'][0]['series_name']
        except:
            return None

    def _officials(self):
        return self.json['official']

    # live matches only
    def _current_summary(self):
        if 'current_summary' in self.match_json().keys():
            return self.match_json()['current_summary']

    def _present_datetime_local(self):
        return self.match_json()['present_datetime_local']

    def _present_datetime_gmt(self):
        return self.match_json()['present_datetime_gmt']

    def _start_datetime_local(self):
        return self.match_json()['start_datetime_local']

    def _start_datetime_gmt(self):
        return self.match_json()['start_datetime_gmt']

    def _cancelled_match(self):
        if self.match_json()['cancelled_match'] == 'N':
            return False
        else:
            return True

    def _rain_rule(self):
        if self.match_json()['rain_rule'] == "1":
            return self.match_json()['rain_rule_name']
        else:
            return None

    def _date(self):
        return self.match_json()['start_date_raw']

    def _continent(self):
        return self.match_json()['continent_name']

    def _town_area(self):
        return self.match_json()['town_area']

    def _town_name(self):
        return self.match_json()['town_name']

    def _town_id(self):
        return self.match_json()['town_id']

    def _weather_location_code(self):
        return self.match_json()['weather_location_code']

    def _match_title(self):
        return self.match_json()['cms_match_title']

    def _result(self):
        return self.json['live']['status']

    def _ground_id(self):
        return self.match_json()['ground_id']

    def _ground_name(self):
        return self.match_json()['ground_name']

    def _lighting(self):
        return self.match_json()['floodlit_name']

    def _followon(self):
        if self.match_json()['followon'] == '1':
            return True
        else:
            return False

    def _scheduled_overs(self):
        return int(self.match_json()['scheduled_overs'])

    def _innings_list(self):
        try:
            return self.json['centre']['common']['innings_list']
        except:
            return None

    def _innings(self):
        return self.json['innings']

    def _latest_batting(self):
        try:
            return self.json['centre']['common']['batting']
        except:
            return None

    def _latest_bowling(self):
        try:
            return self.json['centre']['common']['bowling']
        except:
            return None

    def _latest_innings(self):
        try:
            return self.json['centre']['common']['innings']
        except:
            return None

    def _latest_innings_fow(self):
        if 'fow' in self.json['centre'].keys():
            return self.json['centre']['fow']
        else:
            return None

    def _team_1(self):
        return self.json['team'][0]

    def _team_1_id(self):
        return self._team_1()['team_id']

    def _team_1_abbreviation(self):
        return self._team_1()['team_abbreviation']

    def _team_1_players(self):
        return self._team_1()['player']

    def _team_1_innings(self):
        return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self._team_1_id()][0]

    def _team_1_run_rate(self):
        if self._team_1_innings()['run_rate'] == None:
            return None
        else:
            return float(self._team_1_innings()['run_rate'])

    def _team_1_overs_batted(self):
        return float(self._team_1_innings()['overs'])

    def _team_1_batting_result(self):
        return self._team_1_innings()['event_name']

    def _team_2(self):
        return self.json['team'][1]

    def _team_2_id(self):
        return self._team_2()['team_id']

    def _team_2_abbreviation(self):
        return self._team_2()['team_abbreviation']

    def _team_2_players(self):
        return self._team_2()['player']

    def _team_2_innings(self):
        return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self._team_2_id()][0]

    def _team_2_run_rate(self):
        if self._team_2_innings()['run_rate'] == None:
            return None
        else:
            return float(self._team_2_innings()['run_rate'])

    def _team_2_overs_batted(self):
        return float(self._team_2_innings()['overs'])

    def _team_2_batting_result(self):
        return self._team_2_innings()['event_name']

    def _home_team(self):
        if self._team_1_id() == self.match_json()['home_team_id']:
            return self._team_1_abbreviation()
        else:
            return self._team_2_abbreviation()

    def _batting_first(self):
        if self._team_1_id() == self.match_json()['batting_first_team_id']:
            return self._team_1_abbreviation()
        else:
            return self._team_2_abbreviation()

    def _match_winner(self):
        if self._team_1_id() == self.match_json()['winner_team_id']:
            return self._team_1_abbreviation()
        else:
            return self._team_2_abbreviation()

    def _toss_winner(self):
        if self._team_1_id() == self.match_json()['toss_winner_team_id']:
            return self._team_1_id()
        else:
            return self._team_2_id()

    def _toss_decision(self):
        return self.match_json()['toss_decision']

    def _toss_decision_name(self):
        return self.match_json()['toss_decision_name']

    def _toss_choice_team_id(self):
        return self.match_json()['toss_choice_team_id']

    def _toss_winner_team_id(self):
        return self.match_json()['toss_winner_team_id']

    @staticmethod
    def get_recent_matches(date=None):
        if date:
            url = "http://www.espncricinfo.com/ci/engine/match/index.html?date=%sview=week" % date
        else:
            url = "http://www.espncricinfo.com/ci/engine/match/index.html?view=week"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return [x['href'].split('/',4)[4].split('.')[0] for x in soup.findAll('a', href=True, text='Scorecard')]
