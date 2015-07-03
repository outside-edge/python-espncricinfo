import requests
import urlparse
from .json_import import simplejson
import six

class ESPNCricInfo(object, id):

    def __init__(self, match_id):
        self.match_url = "http://www.espncricinfo.com/matches/engine/match/{0}.html".format(str(match_id))
        self.json_url = "http://www.espncricinfo.com/matches/engine/match/{0}.json".format(str(match_id))
        self.json = self.get_json()

    def get_json(self):
        r = requests.get(self.json_url)
        return r.json()

    def description(self):
        return self.json['description']

    def match(self):
        return self.json['match']
