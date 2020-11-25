import requests
from bs4 import BeautifulSoup
import dateparser
from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.match import Match

class Player(object):

    def __init__(self, player_id):
        self.url = "https://www.espncricinfo.com/ci/content/player/{0}.html".format(str(player_id))
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/athletes/{0}".format(str(player_id))
        self.parsed_html = self.get_html()
        self.json = self.get_json()
        self.player_information = self._parse_player_information()
        self.cricinfo_id = str(player_id)
        if self.parsed_html:
            self.__unicode__ = self._full_name()
            self.name = self._name()
            self.first_name = self._first_name()
            self.full_name = self._full_name()
            self.date_of_birth = self._date_of_birth()
            self.current_age = self._current_age()
            self.major_teams = self._major_teams()
            self.nickname = self._nickname()
            self.playing_role = self._playing_role()
            self.batting_style = self._batting_style()
            self.bowling_style = self._bowling_style()
            self.batting_fielding_averages = self._batting_fielding_averages()
            self.bowling_averages = self._bowling_averages()
            self.test_debut = self._test_debut()
            self.last_test = self._last_test()
            self.t20i_debut = self._t20i_debut()
            self.last_t20i = self._last_t20i()
            self.first_class_debut = self._first_class_debut()
            self.last_first_class = self._last_first_class()
            self.list_a_debut = self._list_a_debut()
            self.last_list_a = self._last_list_a()
            self.t20_debut = self._t20_debut()
            self.last_t20 = self._last_t20()
            self.odi_debut = self._odi_debut()
            self.last_odi = self._last_odi()
            self.recent_matches = self._recent_matches()

    def get_html(self):
        r = requests.get(self.url)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup.find("div", class_="pnl490M")

    def get_json(self):
        r = requests.get(self.json_url)
        if r.status_code == 404:
            raise PlayerNotFoundError
        else:
            return r.json()

    def _parse_player_information(self):
        return self.parsed_html.find_all('p', class_='ciPlayerinformationtxt')

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
        return next((p.text.replace('Major teams ','').split(', ') for p in self.player_information if p.find('b').text == 'Major teams'), None)

    def _nickname(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Nickname'), None)

    def _also_known_as(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Also known as'), None)

    def _playing_role(self):
        return self.json['position']

    def _batting_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'batting'), None)

    def _bowling_style(self):
        return next((x for x in self.json['style'] if x['type'] == 'bowling'), None)

    def _batting_fielding_averages(self):
        if len(self.parsed_html.findAll('table', class_='engineTable')) == 4:
            headers = ['matches', 'innings', 'not_out', 'runs', 'high_score', 'batting_average', 'balls_faced', 'strike_rate', 'centuries', 'fifties', 'fours', 'sixes', 'catches', 'stumpings']
            bat_field = [td.text.strip() for td in self.parsed_html.find('table', class_='engineTable').findAll('td')]
            num_formats = int(len(bat_field)/15)
            format_positions = [15*x for x in range(num_formats)]
            formats = [bat_field[x] for x in format_positions]
            avg_starts = [x+1 for x in format_positions[:num_formats]]
            avg_finish = [x+14 for x in avg_starts]
            format_averages = [bat_field[x:y] for x,y in zip(avg_starts, avg_finish)]
            combined = list(zip(formats, format_averages))
            l = [{x: dict(zip(headers, y))} for x,y in combined]
            return { k: v for d in l for k, v in d.items() }
        else:
            return None

    def _bowling_averages(self):
        if len(self.parsed_html.findAll('table', class_='engineTable')) == 4:
            headers = ['matches', 'innings', 'balls_delivered', 'runs', 'wickets', 'best_innings', 'best_match', 'bowling_average', 'economy', 'strike_rate', 'four_wickets', 'five_wickets', 'ten_wickets']
            bowling = [td.text.strip() for td in self.parsed_html.findAll('table', class_='engineTable')[1].findAll('td')]
            num_formats = int(len(bowling)/14)
            format_positions = [14*x for x in range(num_formats)]
            formats = [bowling[x] for x in format_positions]
            avg_starts = [x+1 for x in format_positions[:num_formats]]
            avg_finish = [x+13 for x in avg_starts]
            format_averages = [bowling[x:y] for x,y in zip(avg_starts, avg_finish)]
            combined = list(zip(formats, format_averages))
            l = [{x: dict(zip(headers, y))} for x,y in combined]
            return { k: v for d in l for k, v in d.items() }
        else:
            return None

    def _debuts_and_lasts(self):
        if len(self.parsed_html.findAll('table', class_='engineTable')) == 4:
            return self.parsed_html.findAll('table', class_='engineTable')[2]
        else:
            return None

    def _test_debut(self):
        if self._debuts_and_lasts() is not None:
            test_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Test debut'), None)
            if test_debut:
                url = 'http://www.espncricinfo.com'+test_debut.find('a')['href']
                match_id = int(test_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = test_debut.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _last_test(self):
        if self._debuts_and_lasts() is not None:
            last_test = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last Test'), None)
            if last_test:
                url = 'http://www.espncricinfo.com'+last_test.find('a')['href']
                match_id = int(last_test.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_test.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _t20i_debut(self):
        if self._debuts_and_lasts() is not None:
            t20i_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'T20I debut'), None)
            if t20i_debut:
                url = 'http://www.espncricinfo.com'+t20i_debut.find('a')['href']
                match_id = int(t20i_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = t20i_debut.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _last_t20i(self):
        if self._debuts_and_lasts() is not None:
            last_t20i = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last T20I'), None)
            if last_t20i:
                url = 'http://www.espncricinfo.com'+last_t20i.find('a')['href']
                match_id = int(last_t20i.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_t20i.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _first_class_debut(self):
        if self._debuts_and_lasts() is not None:
            first_class_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'First-class debut'), None)
            if first_class_debut:
                try:
                    url = 'http://www.espncricinfo.com'+first_class_debut.find('a')['href']
                    match_id = int(first_class_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                    title = first_class_debut.findAll('td')[1].text.replace(' scorecard','')
                    return {'url': url, 'match_id': match_id, 'title': title}
                except:
                    return {'url': None, 'match_id': None, 'title': first_class_debut.findAll('td')[1].text}
            else:
                return None
        else:
            return None

    def _last_first_class(self):
        if self._debuts_and_lasts() is not None:
            last_first_class = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last First-class'), None)
            if last_first_class:
                url = 'http://www.espncricinfo.com'+last_first_class.find('a')['href']
                match_id = int(last_first_class.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_first_class.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        return None

    def _list_a_debut(self):
        if self._debuts_and_lasts() is not None:
            list_a_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'List A debut'), None)
            if list_a_debut:
                try:
                    url = 'http://www.espncricinfo.com'+list_a_debut.find('a')['href']
                    match_id = int(list_a_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                    title = list_a_debut.findAll('td')[1].text.replace(' scorecard','')
                    return {'url': url, 'match_id': match_id, 'title': title}
                except:
                    return {'url': None, 'match_id': None, 'title': list_a_debut.findAll('td')[1].text}
            else:
                return None
        else:
            return None

    def _last_list_a(self):
        if self._debuts_and_lasts() is not None:
            last_list_a = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last List A'), None)
            if last_list_a:
                url = 'http://www.espncricinfo.com'+last_list_a.find('a')['href']
                match_id = int(last_list_a.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_list_a.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _t20_debut(self):
        if self._debuts_and_lasts() is not None:
            t20_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Twenty20 debut'), None)
            if t20_debut:
                url = 'http://www.espncricinfo.com'+t20_debut.find('a')['href']
                match_id = int(t20_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = t20_debut.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _last_t20(self):
        if self._debuts_and_lasts() is not None:
            last_t20 = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last Twenty20'), None)
            if last_t20:
                url = 'http://www.espncricinfo.com'+last_t20.find('a')['href']
                match_id = int(last_t20.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_t20.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _odi_debut(self):
        if self._debuts_and_lasts() is not None:
            odi_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'ODI debut'), None)
            if odi_debut:
                url = 'http://www.espncricinfo.com'+odi_debut.find('a')['href']
                match_id = int(odi_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = odi_debut.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _last_odi(self):
        if self._debuts_and_lasts() is not None:
            last_odi = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last ODI'), None)
            if last_odi:
                url = 'http://www.espncricinfo.com'+last_odi.find('a')['href']
                match_id = int(last_odi.find('a')['href'].split('/', 4)[4].split('.')[0])
                title = last_odi.findAll('td')[1].text.replace(' scorecard','')
                return {'url': url, 'match_id': match_id, 'title': title}
            else:
                return None
        else:
            return None

    def _recent_matches(self):
        try:
            table = self.parsed_html.findAll('table', class_='engineTable')[-1]
            return [x.find('a')['href'].split('/', 4)[4].split('.')[0] for x in table.findAll('tr')[1:]]
        except:
            return None

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
