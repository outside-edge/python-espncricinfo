import requests

class Match(object):

    def __init__(self, match_id):
        self.match_url = "http://www.espncricinfo.com/matches/engine/match/{0}.html".format(str(match_id))
        self.json_url = "http://www.espncricinfo.com/matches/engine/match/{0}.json".format(str(match_id))
        self.json = self.get_json()
        self.__unicode__ = self.description()

    def get_json(self):
        r = requests.get(self.json_url)
        return r.json()

    def match_json(self):
        return self.json['match']

    def season(self):
        return self.match_json()['season']

    def description(self):
        return self.json['description']

    def cancelled_match(self):
        if self.match_json()['cancelled_match'] == 'N':
            return False
        else:
            return True

    def date(self):
        return self.match_json()['start_date_raw']

    def continent(self):
        return self.match_json()['continent_name']

    def match_title(self):
        return self.match_json()['cms_match_title']

    def result(self):
        return self.match_json()['result_short_name']

    def ground_id(self):
        return self.match_json()['ground_id']

    def ground_name(self):
        return self.match_json()['ground_name']

    def lighting(self):
        return self.match_json()['floodlit_name']

    def scheduled_overs(self):
        return int(self.match_json()['scheduled_overs'])

    def team_1(self):
        return self.json['team'][0]

    def team_1_id(self):
        return self.team_1()['team_id']

    def team_1_abbreviation(self):
        return self.team_1()['team_abbreviation']

    def team_1_players(self):
        return self.team_1()['player']

    def team_2(self):
        return self.json['team'][1]

    def team_2_id(self):
        return self.team_2()['team_id']

    def team_2_abbreviation(self):
        return self.team_2()['team_abbreviation']

    def team_2_players(self):
        return self.team_2()['player']

    def match_winner(self):
        if self.team_1_id() == self.match_json()['winner_team_id']:
            return self.team_1_abbreviation()
        else:
            return self.team_2_abbreviation()

    def toss_winner(self):
        if self.team_1_id() == self.match_json()['toss_winner_team_id']:
            return self.team_1_abbreviation()
        else:
            return self.team_2_abbreviation()
