import requests
from bs4 import BeautifulSoup
from espncricinfo.exceptions import GroundNotFoundError

class Ground(object):

    def __init__(self, ground_id):
        self.cricinfo_id = ground_id
        self.url = "http://www.espncricinfo.com/ci/content/ground/{0}.html".format(str(self.cricinfo_id))
        self.json_url = "http://core.espnuk.org/v2/sports/cricket/venues/{0}".format(str(self.cricinfo_id))

        self.parsed_html = self.get_html()
        self.json = self.get_json()

        if self.json:
            self.__unicode__ = self._full_name()
            self.short_name = self._short_name()            
            self.capacity = self._capacity()
            self.grass = self._grass()
            self.indoor = self._indoor()
            self.address = self._address()
            self.city = self._city()
            self.state = self._state()
            self.zipcode = self._zipcode()
            self.country = self._country()
            self.summary = self._summary()

        if self.parsed_html:
            self.established = self._established()
            self.floodlights_added = self._floodlights_added()
            self.end_names = self._end_names()
            self.home_team = self._home_team()
            self.other_sports = self._other_sports()
            self.first_test = self._first_test()
            self.last_test = self._last_test()
            self.first_odi = self._first_odi()
            self.last_odi = self._last_odi()
            self.first_t20i = self._first_t20i()
            self.last_t20i = self._last_t20i()

    def get_json(self):
        r = requests.get(self.json_url)
        if not r.ok:
            raise GroundNotFoundError
        else:
            return r.json()

    def _full_name(self):
        return self.json.get('fullName')

    def _short_name(self):
        return self.json.get('shortName')

    def _capacity(self):
        return self.json.get('capacity')

    def _grass(self):
        return self.json.get('grass', False)

    def _indoor(self):
        return self.json.get('indoor', False)

    def _address(self):
        return self.json.get('address', {})

    def _city(self):
        return self.address.get('city')

    def _state(self):
        return self.address.get('state')

    def _zipcode(self):
        return self.address.get('zipCode')

    def _country(self):
        return self.address.get('country')

    def _summary(self):
        return self.address.get('summary')

    def get_html(self):
        r = requests.get(self.url)
        if not r.ok:
            raise GroundNotFoundError
        else:
            soup = BeautifulSoup(r.text, 'html.parser').find('div', id= 'ciHomeContentlhs')
            return soup

    def _parse_ground_stats(self):
        return self.parsed_html.find('div', id = 'stats')

    def _parse_ground_records(self):
        return self.parsed_html.find('div', id = 'recs')

    def _established(self):
        t = self._parse_ground_stats().find('label', text = 'Established ')
        if t:
            return t.next_sibling

    def _floodlights_added(self):
        t = self._parse_ground_stats().find('label', text = 'Floodlights ')
        if t:
            return t.next_sibling

    def _end_names(self):
        t = self._parse_ground_stats().find('label', text = 'End names ')
        if t:
            return t.next_sibling

    def _home_team(self):
        t = self._parse_ground_stats().find('label', text = 'Home team ')
        if t:
            return t.next_sibling

    def _other_sports(self):
        t = self._parse_ground_stats().find('label', text = 'Other sports ')
        if t:
            return t.next_sibling

    def _first_test(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'First Test'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}

    def _last_test(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'Last Test'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}

    def _first_odi(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'First ODI'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}

    def _last_odi(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'Last ODI'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}

    def _first_t20i(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'First T20I'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}

    def _last_t20i(self):
        for tr in self._parse_ground_records().find_all('tr'):
            if tr.find('label', text = 'Last T20I'):
                url = 'http://www.espncricinfo.com' + tr.find('a')['href']
                title = tr.find_all('td')[1].text
                match_id = int(url.split('/')[-1].split('.')[0])
                return {'url': url, 'match_id': match_id, 'title': title}
