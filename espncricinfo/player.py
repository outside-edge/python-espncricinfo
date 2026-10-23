"""Player records from the ESPN core API and the Statsguru pages."""

import csv
from pathlib import Path

from bs4 import BeautifulSoup

from espncricinfo import _core
from espncricinfo.exceptions import PlayerNotFoundError


class Player:
    """A player, loaded from the ESPN core API athlete record."""

    def __init__(self, player_id: int | str) -> None:
        """Load the player record.

        Args:
            player_id: ESPNcricinfo player id (the number in a profile URL).
        """
        self.player_id = player_id
        self.url = f"https://www.espncricinfo.com/player/player-name-{player_id!s}"
        self.json_url = (
            f"http://core.espnuk.org/v2/sports/cricket/athletes/{player_id!s}"
        )
        self.headers = {"user-agent": "Mozilla/5.0"}
        self.json = self.get_json()
        self._major_teams_cache = None
        self.cricinfo_id = str(player_id)
        self.name = self._name()
        self.first_name = self._first_name()
        self.full_name = self._full_name()
        self.date_of_birth = self._date_of_birth()
        self.current_age = self._current_age()
        self.playing_role = self._playing_role()
        self.batting_style = self._batting_style()
        self.bowling_style = self._bowling_style()

    def get_html(self):
        """Return the player's profile page as BeautifulSoup."""
        r = _core.http_get(self.url, headers=self.headers)
        if r.status_code == 404:
            raise PlayerNotFoundError
        return BeautifulSoup(r.text, "html.parser")

    def get_json(self):
        """Return the core API athlete record; raise PlayerNotFoundError on 404."""
        r = _core.http_get(self.json_url, headers=self.headers)
        if r.status_code == 404:
            raise PlayerNotFoundError
        r.raise_for_status()
        return r.json()

    def _name(self):
        return self.json["name"]

    def _first_name(self):
        return self.json["firstName"]

    def _middle_name(self):
        return self.json["middleName"]

    def _last_name(self):
        return self.json["lastName"]

    def _full_name(self):
        return self.json["fullName"]

    def _date_of_birth(self):
        return self.json["dateOfBirth"]

    def _current_age(self):
        return self.json["age"]

    @property
    def major_teams(self):
        """Names of the player's major teams (one request per team, cached)."""
        if self._major_teams_cache is None:
            teams = []
            for reference in self.json.get("majorTeams", []):
                response = _core.http_get(reference["$ref"], headers=self.headers)
                response.raise_for_status()
                team = response.json()
                name = (
                    team.get("longName") or team.get("displayName") or team.get("name")
                )
                if name:
                    teams.append(name)
            self._major_teams_cache = teams
        return self._major_teams_cache

    def _playing_role(self):
        return self.json["position"]

    def _batting_style(self):
        return next((x for x in self.json["style"] if x["type"] == "batting"), None)

    def _bowling_style(self):
        return next((x for x in self.json["style"] if x["type"] == "bowling"), None)

    def _write_stats_table(self, query, table_index, file_name):
        """Write one table of the player's stats page to ``file_name`` as CSV.

        Each row's cells are on separate lines in ESPN's HTML, so a row's text
        split on newlines gives its cells (with an empty leading cell).
        """
        url = (
            "https://stats.espncricinfo.com/ci/engine/player/"
            f"{self.player_id}.html?{query}"
        )
        response = _core.http_get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table")[table_index]
        rows = [tr.text.splitlines() for tr in table.find_all("tr")]
        with Path(file_name).open("w", newline="") as csv_file:
            csv.writer(csv_file).writerows(rows)

    def get_career_averages(
        self,
        file_name: str | None = None,
        match_format: int = 11,
        data_type: str = "allround",
    ) -> None:
        """Write career averages (overall and by span) to a CSV file.

        Args:
            file_name: Output path. Defaults to
                ``{player_id}_{match_format}_{data_type}_career_averages.csv``.
            match_format: 1 Test, 2 ODI, 3 T20I, 11 all international,
                20 youth Test, 21 youth ODI.
            data_type: ``allround``, ``batting``, ``bowling`` or ``fielding``.
        """
        if file_name is None:
            file_name = (
                f"{self.player_id}_{match_format}_{data_type}_career_averages.csv"
            )
        query = f"class={match_format};template=results;type={data_type}"
        self._write_stats_table(query, 2, file_name)

    def get_career_summary(
        self,
        file_name: str | None = None,
        match_format: int = 11,
        data_type: str = "allround",
    ) -> None:
        """Write the career summary (one row per format, venue, opponent...) to CSV.

        Args:
            file_name: Output path. Defaults to
                ``{player_id}_{match_format}_{data_type}_career_summary.csv``.
            match_format: 1 Test, 2 ODI, 3 T20I, 11 all international,
                20 youth Test, 21 youth ODI.
            data_type: ``allround``, ``batting``, ``bowling`` or ``fielding``.
        """
        if file_name is None:
            file_name = (
                f"{self.player_id}_{match_format}_{data_type}_career_summary.csv"
            )
        query = f"class={match_format};template=results;type={data_type}"
        self._write_stats_table(query, 3, file_name)

    def get_data(
        self,
        file_name: str | None = None,
        match_format: int = 11,
        data_type: str = "allround",
        view: str = "match",
    ) -> None:
        """Write the player's record match by match (or another view) to CSV.

        Args:
            file_name: Output path. Defaults to
                ``{player_id}_{match_format}_{data_type}_{view}.csv``.
            match_format: 1 Test, 2 ODI, 3 T20I, 11 all international,
                20 youth Test, 21 youth ODI.
            data_type: ``allround``, ``batting``, ``bowling`` or ``fielding``.
            view: ``match``, ``innings``, ``cumulative``, ``reverse_cumulative``,
                ``series``, ``tour`` or ``ground``.
        """
        if file_name is None:
            file_name = f"{self.player_id}_{match_format}_{data_type}_{view}.csv"
        query = f"class={match_format};template=results;type={data_type};view={view}"
        self._write_stats_table(query, 3, file_name)
