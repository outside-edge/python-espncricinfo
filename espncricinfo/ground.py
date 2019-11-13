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

    def _established(self):
        return self.parsed_html.find('div', id = 'stats').find('label', text = 'Established ').next_sibling

    def _floodlights_added(self):
        return self.parsed_html.find('div', id = 'stats').find('label', text = 'Floodlights ').next_sibling

    def _end_names(self):
        return self.parsed_html.find('div', id = 'stats').find('label', text = 'End names ').next_sibling

    def _home_team(self):
        return self.parsed_html.find('div', id = 'stats').find('label', text = 'Home team ').next_sibling

    def _other_sports(self):
        return self.parsed_html.find('div', id = 'stats').find('label', text = 'Other sports ').next_sibling
