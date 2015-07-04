import requests

class Summary(object):

    def __init__(self):
        self.url = "http://www.espncricinfo.com/netstorage/summary.json"
        self.json = self.get_json()
        self.match_ids = self.json['matches'].keys()
        self.all_matches = self.json['matches'].values()

    def get_json(self):
        r = requests.get(self.url)
        return r.json()

    def match(self, id):
        m = self.json['matches'][id]
        m['url'] = "http://www.espncricinfo.com"+m['url']
        return m
