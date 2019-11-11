import requests
from bs4 import BeautifulSoup

class Summary(object):

    def __init__(self):
        self.url = "http://static.cricinfo.com/rss/livescores.xml"
        self.xml = self.get_xml()
        
        self.match_ids = []
        self.match_urls = []

        for g in self.xml.findAll('guid'):
            self.match_ids.append(g.text.strip().split('/')[-1].split('.')[0])
            self.match_urls.append(g.text.strip())

    def get_xml(self):
        r = requests.get(self.url)
        if r.ok:
            return BeautifulSoup(r.text)
        else:
            return None
