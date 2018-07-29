import requests
from bs4 import BeautifulSoup
import dateparser
from espncricinfo.exceptions import PlayerNotFoundError

class Player(object):

    def __init__(self, player_id):
        self.url = "http://www.espncricinfo.com/whatever/content/current/player/{0}.html".format(str(player_id))
        self.parsed_html = self.get_html()
        self.player_information = self._parse_player_information()
        if self.parsed_html:
            self.__unicode__ = self._full_name()
            self.name = self._name()
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

    def _parse_player_information(self):
        return self.parsed_html.find_all('p', class_='ciPlayerinformationtxt')

    def _name(self):
        return self.parsed_html.find('h1').text.strip()

    def _full_name(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Full name'), None)

    def _date_of_birth(self):
        month_day, year = next(p.find('span').text for p in self.player_information if p.find('b').text == 'Born').strip().split(', ')[0:2]
        return dateparser.parse(month_day+', '+year)

    def _current_age(self):
        return next((p.find('span').text.strip() for p in self.player_information if p.find('b').text == 'Current age'), None)

    def _major_teams(self):
        return next((p.text.replace('Major teams ','').split(', ') for p in self.player_information if p.find('b').text == 'Major teams'), None)

    def _nickname(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Nickname'), None)

    def _also_known_as(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Also known as'), None)

    def _playing_role(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Playing role'), None)

    def _batting_style(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Batting style'), None)

    def _bowling_style(self):
        return next((p.find('span').text for p in self.player_information if p.find('b').text == 'Bowling style'), None)

    def _batting_fielding_averages(self):
        headers = ['matches', 'innings', 'not_out', 'runs', 'high_score', 'batting_average', 'balls_faced', 'strike_rate', 'centuries', 'fifties', 'fours', 'sixes', 'catches', 'stumpings']
        bat_field = [td.text.strip() for td in self.parsed_html.find('table', class_='engineTable').findAll('td')]
        num_formats = int(len(bat_field)/15)
        format_positions = [15*x for x in range(num_formats)]
        formats = [bat_field[x] for x in format_positions]
        avg_starts = [x+1 for x in format_positions[:num_formats-1]]
        avg_finish = [x+14 for x in avg_starts]
        format_averages = [bat_field[x:y] for x,y in zip(avg_starts, avg_finish)]
        combined = list(zip(formats, format_averages))
        return [{x: list(zip(headers, y))} for x,y in combined]

    def _bowling_averages(self):
        headers = ['matches', 'innings', 'balls_delivered', 'runs', 'wickets', 'best_innings', 'best_match', 'bowling_average', 'economy', 'strike_rate', 'four_wickets', 'five_wickets', 'ten_wickets']
        bowling = [td.text.strip() for td in self.parsed_html.findAll('table', class_='engineTable')[1].findAll('td')]
        num_formats = int(len(bowling)/14)
        format_positions = [14*x for x in range(num_formats)]
        formats = [bowling[x] for x in format_positions]
        avg_starts = [x+1 for x in format_positions[:num_formats-1]]
        avg_finish = [x+13 for x in avg_starts]
        format_averages = [bowling[x:y] for x,y in zip(avg_starts, avg_finish)]
        combined = list(zip(formats, format_averages))
        return [{x: list(zip(headers, y))} for x,y in combined]

    def _debuts_and_lasts(self):
        return self.parsed_html.findAll('table', class_='engineTable')[2]

    def _test_debut(self):
        test_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Test debut'), None)
        if test_debut:
            url = 'http://www.espncricinfo.com'+test_debut.find('a')['href']
            match_id = int(test_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = test_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_test(self):
        last_test = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last Test'), None)
        if last_test:
            url = 'http://www.espncricinfo.com'+last_test.find('a')['href']
            match_id = int(last_test.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_test.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _t20i_debut(self):
        t20i_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'T20I debut'), None)
        if t20i_debut:
            url = 'http://www.espncricinfo.com'+t20i_debut.find('a')['href']
            match_id = int(t20i_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = t20i_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_t20i(self):
        last_t20i = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last T20I'), None)
        if last_t20i:
            url = 'http://www.espncricinfo.com'+last_t20i.find('a')['href']
            match_id = int(last_t20i.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_t20i.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _first_class_debut(self):
        first_class_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'First-class debut'), None)
        if first_class_debut:
            url = 'http://www.espncricinfo.com'+first_class_debut.find('a')['href']
            match_id = int(first_class_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = first_class_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_first_class(self):
        last_first_class = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last First-class'), None)
        if last_first_class:
            url = 'http://www.espncricinfo.com'+last_first_class.find('a')['href']
            match_id = int(last_first_class.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_first_class.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _list_a_debut(self):
        list_a_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'List A debut'), None)
        if list_a_debut:
            url = 'http://www.espncricinfo.com'+list_a_debut.find('a')['href']
            match_id = int(list_a_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = list_a_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_list_a(self):
        last_list_a = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last List A'), None)
        if last_list_a:
            url = 'http://www.espncricinfo.com'+last_list_a.find('a')['href']
            match_id = int(last_list_a.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_list_a.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _t20_debut(self):
        t20_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Twenty20 debut'), None)
        if t20_debut:
            url = 'http://www.espncricinfo.com'+t20_debut.find('a')['href']
            match_id = int(t20_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = t20_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_t20(self):
        last_t20 = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last Twenty20'), None)
        if last_t20:
            url = 'http://www.espncricinfo.com'+last_t20.find('a')['href']
            match_id = int(last_t20.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_t20.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _odi_debut(self):
        odi_debut = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'ODI debut'), None)
        if odi_debut:
            url = 'http://www.espncricinfo.com'+odi_debut.find('a')['href']
            match_id = int(odi_debut.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = odi_debut.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _last_odi(self):
        last_odi = next((tr for tr in self._debuts_and_lasts().findAll('tr') if tr.find('b').text == 'Last ODI'), None)
        if last_odi:
            url = 'http://www.espncricinfo.com'+last_odi.find('a')['href']
            match_id = int(last_odi.find('a')['href'].split('/', 4)[4].split('.')[0])
            title = last_odi.findAll('td')[1].text.replace(' scorecard','')
            return {'url': url, 'match_id': match_id, 'title': title}
        else:
            return None

    def _recent_matches(self):
        table = self.parsed_html.findAll('table', class_='engineTable')[3]
        return [x.find('a')['href'].split('/', 4)[4].split('.')[0] for x in table.findAll('tr')[1:]]
