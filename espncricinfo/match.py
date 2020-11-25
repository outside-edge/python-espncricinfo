import json
import requests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError

class Match(object):

    def __init__(self, match_id):
        self.match_id = match_id
        self.match_url = "https://www.espncricinfo.com/matches/engine/match/{0}.html".format(str(match_id))
        self.json_url = "https://www.espncricinfo.com/matches/engine/match/{0}.json".format(str(match_id))
        self.json = self.get_json()
        self.html = self.get_html()
        self.comms_json = self.get_comms_json()
        if self.json:
            self.__unicode__ = self._description()
            self.status = self._status()
            self.match_class = self._match_class()
            self.season = self._season()
            self.description = self._description()
            self.legacy_scorecard_url = self._legacy_scorecard_url()
            self.series = self._series()
            self.series_name = self._series_name()
            self.series_id = self._series_id()
            self.event_url = "http://core.espnuk.org/v2/sports/cricket/leagues/{0}/events/{1}".format(str(self.series_id), str(match_id))
            self.details_url = self._details_url()
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
            self.espn_api_url = self._espn_api_url()
            # from comms_json
            self.rosters = self._rosters()
            self.all_innings = self._all_innings()
            self.close_of_play = self._close_of_play()


    def __str__(self):
        return self.description

    def __repr__(self):
        return (f'{self.__class__.__name__}('f'{self.match_id!r})')

    def get_json(self):
        r = requests.get(self.json_url)
        if r.status_code == 404:
            raise MatchNotFoundError
        elif 'Scorecard not yet available' in r.text:
            raise NoScorecardError
        else:
            return r.json()

    def get_html(self):
        r = requests.get(self.match_url)
        if r.status_code == 404:
            raise MatchNotFoundError
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def match_json(self):
        return self.json['match']

    def innings_comms_url(self, innings=1, page=1):
        return f"https://hsapi.espncricinfo.com/v1/pages/match/comments?lang=en&leagueId={self.series_id}&eventId={self.match_id}&period={innings}&page={page}&filter=full&liveTest=false"

    def get_comms_json(self):
        try:
            text = self.html.find_all('script')[15].string
            return json.loads(text)
        except:
            return None

    def _espn_api_url(self):
        return "https://site.api.espn.com/apis/site/v2/sports/cricket/{0}/summary?event={1}".format(self.series_id, self.match_id)

    def _legacy_scorecard_url(self):
        return "https://static.espncricinfo.com"+self.match_json()['legacy_url']

    def _details_url(self, page=1, number=1000):
        return self.event_url+"/competitions/{0}/details?page_size={1}&page={2}".format(str(self.match_id), str(number), str(page))

    def __str__(self):
        return self.json['description']

    def __unicode__(self):
        return self.json['description']

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
            return self.json['series'][-1]['series_name']
        except:
            return None

    def _series_id(self):
        return self.json['series'][-1]['core_recreation_id']

    def _officials(self):
        return self.json['official']

    # live matches only
    def _current_summary(self):
        return self.match_json().get('current_summary')

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
        if self.match_json().get('rain_rule') == "1":
            return self.match_json()['rain_rule_name']
        else:
            return None

    def _date(self):
        return self.match_json()['start_date_raw']

    def _continent(self):
        return self.match_json().get('continent_name')

    def _town_area(self):
        return self.match_json().get('town_area')

    def _town_name(self):
        return self.match_json().get('town_name')

    def _town_id(self):
        return self.match_json().get('town_id')

    def _weather_location_code(self):
        return self.match_json().get('weather_location_code')

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
        if self.match_json().get('followon') == '1':
            return True
        else:
            return False

    def _scheduled_overs(self):
        try:
            return int(self.match_json()['scheduled_overs'])
        except:
            return None

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
        return self.json['centre'].get('fow')

    def _team_1(self):
        return self.json['team'][0]

    def _team_1_id(self):
        return self._team_1()['team_id']

    def _team_1_abbreviation(self):
        return self._team_1()['team_abbreviation']

    def _team_1_players(self):
        return self._team_1().get('player', [])

    def _team_1_innings(self):
        try:
            return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self._team_1_id()][0]
        except:
            return None

    def _team_1_run_rate(self):
        try:
            return float(self._team_1_innings()['run_rate'])
        except:
            return None

    def _team_1_overs_batted(self):
        try:
            return float(self._team_1_innings()['overs'])
        except:
            return None

    def _team_1_batting_result(self):
        try:
            return self._team_1_innings()['event_name']
        except:
            return None

    def _team_2(self):
        return self.json['team'][1]

    def _team_2_id(self):
        return self._team_2()['team_id']

    def _team_2_abbreviation(self):
        return self._team_2()['team_abbreviation']

    def _team_2_players(self):
        return self._team_2().get('player', [])

    def _team_2_innings(self):
        try:
            return [inn for inn in self.json['innings'] if inn['batting_team_id'] == self._team_2_id()][0]
        except:
            return None

    def _team_2_run_rate(self):
        try:
            return float(self._team_2_innings()['run_rate'])
        except:
            return None

    def _team_2_overs_batted(self):
        try:
            return float(self._team_2_innings()['overs'])
        except:
            return None

    def _team_2_batting_result(self):
        try:
            return self._team_2_innings()['event_name']
        except:
            return None

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
        if self.match_json()['toss_decision'] == '' and len(self.innings) > 0:
            if self.innings[0]['batting_team_id'] == self.toss_winner:
                decision = '1'
            else:
                decision = '2'
        else:
            decision = self.match_json()['toss_decision']
        return decision

    def _toss_decision_name(self):
        if self.match_json()['toss_decision_name'] == '' and len(self.innings) > 0:
            if self.innings[0]['batting_team_id'] == self.toss_winner:
                decision_name = 'bat'
            else:
                decision_name = 'bowl'
        else:
            decision_name = self.match_json()['toss_decision_name']
        return decision_name

    def _toss_choice_team_id(self):
        return self.match_json()['toss_choice_team_id']

    def _toss_winner_team_id(self):
        return self.match_json()['toss_winner_team_id']

    # comms_json methods

    def _rosters(self):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['teams']
        except:
            return None

    def _all_innings(self):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings']
        except:
            return None

    def _close_of_play(self):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['closePlay']
        except:
            return None

    def batsmen(self, innings):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings'][str(innings)]['batsmen']
        except:
            return None

    def bowlers(self, innings):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings'][str(innings)]['bowlers']
        except:
            return None

    def did_not_bat(self, innings):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings'][str(innings)]['didNotBat']
        except:
            return None

    def extras(self, innings):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings'][str(innings)]['extras']
        except:
            return None

    def fows(self, innings):
        try:
            return self.comms_json['props']['pageProps']['data']['content']['innings'][str(innings)]['fallOfWickets']
        except:
            return None

    @staticmethod
    def get_recent_matches(date=None):
        if date:
            url = "https://www.espncricinfo.com/ci/engine/match/index.html?date=%sview=week" % date
        else:
            url = "https://www.espncricinfo.com/ci/engine/match/index.html?view=week"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return [x['href'].split('/',4)[4].split('.')[0] for x in soup.findAll('a', href=True, text='Scorecard')]
