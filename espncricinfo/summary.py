import requests
from xml.etree import ElementTree as ET

class Summary(object):

    def __init__(self):
        self.url = "http://static.cricinfo.com/rss/livescores.xml"
        self.rss = self.get_rss()
        
        self.matches = {}
        self.match_ids = []

        if len(self.rss) > 0:

            for i in self.rss[0].findall('item'):
                desc = i.find('description').text
                guid = i.find('guid').text
                match_id = guid.split('/')[-1].split('.')[0]
                self.matches[match_id] = {'description' : desc, 'url' : guid}
        
            self.match_ids = list(self.matches.keys())

    def get_rss(self):
        
        r = requests.get(self.url)
        if r.ok:
            return ET.fromstring(r.content)
        else:
            return None
