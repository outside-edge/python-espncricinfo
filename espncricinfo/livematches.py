import requests, re
from bs4 import BeautifulSoup

class LiveMatch(object):
    def __init__(self, match_time, match_id, match_number, venue, date, year, series, teams, match_status):
        self.match_time = match_time
        self.match_id = match_id
        self.match_number = match_number
        self.venue = venue
        self.date = date
        self.year = year
        self.series = series
        self.teams = teams
        self.match_status = match_status

    def __repr__(self):
        teams_info = " | ".join([f"{team[0]}: {team[1]}" for team in self.teams])
        return (f"Match Time: {self.match_time}\n"
                f"Match Number: {self.match_number}\n"
                f"Venue: {self.venue}\n"
                f"Date: {self.date}, {self.year}\n"
                f"Series: {self.series}\n"
                f"Teams: {teams_info}\n"
                f"Status: {self.match_status}\n")

class LiveMatches:
    
    def __init__(self):
        self.match_url = "https://www.espncricinfo.com/live-cricket-score"
        self.headers = {'user-agent': 'Mozilla/5.0'}
        self._live_matches = []
        self.html = None
    
    @property
    def live_matches(self):
        self._get_live_matches()
    
    def _fetch_html(self):
        response = requests.get(self.match_url, headers=self.headers)
        if response.status_code != 200:
            print("Failed to retrieve page")
            return None
        return BeautifulSoup(response.text, "html.parser")

    def _get_live_matches(self):
        self.html = self.fetch_html()
        if not self.html:
            return []
        
        parent_div = self.html.select_one("html > body > div > section > section > div:nth-of-type(3) > div > div:nth-of-type(3) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(3) > div > div:nth-of-type(1) > div > div:nth-of-type(2) > div")
        if parent_div:
            matches = []
            for match_ in parent_div.find_all(recursive=False):
                a_div = match_.select_one("a.ds-no-tap-higlight")
                match_url = a_div.get("href") or ""
                match_id = re.search(r'-(\d+)/[^/]+$', match_url).group(1)
                span_text = match_.select_one("span.ds-text-tight-xs.ds-font-bold.ds-uppercase.ds-leading-5")
                div_text = match_.select_one("div.ds-text-tight-xs.ds-truncate.ds-text-typo-mid3")
                match_time = span_text.text.strip() if span_text else "N/A"
                match_date = div_text.text.strip() if div_text else "N/A"
                
                teams = []
                teams_div = match_.select_one("div.ds-flex.ds-flex-col.ds-mt-2.ds-mb-2")
                for team in teams_div.find_all("div", class_="ci-team-score"):
                    team_div = team.find("div", class_="ds-flex ds-items-center ds-min-w-0 ds-mr-1")
                    team_name = team_div.get("title") if team_div else "Unknown"
                    score_div = team.find("div", class_="ds-text-compact-s")
                    if score_div:
                        overs_target = score_div.select_one('span[class*="ds-mr-0.5"]')
                        overs_target_text = overs_target.text.strip() if overs_target else ""
                        scores = [s.text.strip() for s in score_div.select("strong")]
                        formatted_score = f"{overs_target_text} {' & '.join(scores)}" if overs_target_text else " & ".join(scores)
                    else:
                        formatted_score = "N/A"
                    teams.append((team_name, formatted_score))
                
                if match_date != "N/A":
                    match_number, venue, date, year, series = match_date.split(", ")
                else:
                    match_number = venue = date = year = series = "N/A"
                
                match_status_p = match_.find("p", class_="ds-text-tight-s ds-font-medium ds-truncate ds-text-typo")
                match_status = match_status_p.text.strip() if match_status_p else "N/A"
                
                matches.append(LiveMatch(match_time, match_id, match_number, venue, date, year, series, teams, match_status))
        return matches
