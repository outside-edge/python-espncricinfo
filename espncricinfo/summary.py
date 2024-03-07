import requests
from bs4 import BeautifulSoup
from espncricinfo.match import Match

class Summary(object):

    def __init__(self):
        self.url = "http://static.cricinfo.com/rss/livescores.xml"
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self.xml = self.get_xml()
        self.match_ids = self._match_ids()
        self.matches = self._build_matches()

    def get_xml(self):
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 404:
            raise MatchNotFoundError
        else:
            return BeautifulSoup(r.text, 'xml')

    def _match_ids(self):
        matches = [x.link.text.split(".html")[0].split('/')[6] for x in self.xml.findAll('item')]
        return matches

    def _build_matches(self):
        return [Match(m) for m in self.match_ids]
