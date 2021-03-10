import json
import requests
import datetime
from bs4 import BeautifulSoup
from espncricinfo.match import Match

class Summary(object):

    def __init__(self):
        self.url = "https://www.espncricinfo.com/live-cricket-score"
        self.html = self.get_html()
        self.match_ids = self._match_ids()
        self.matches = self._build_matches()

    def get_html(self):
        r = requests.get(self.url)
        if r.status_code == 404:
            raise MatchNotFoundError
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def summary_json(self):
        try:
            text = self.html.find_all('script')[15].contents[0]
            return json.loads(text)
        except:
            return None

    def _match_ids(self):
        matches = [x['objectId'] for x in self.summary_json()['props']['pageProps']['data']['pageData']['content']['matches']]
        return matches

    def _build_matches(self):
        #matches = []
        #for m in self.match_ids:
        #    try:
        #        matches.append(Match(m))
        #    except:
        #        matches.append(m)
        #return matches
        return [Match(m) for m in self.match_ids]
