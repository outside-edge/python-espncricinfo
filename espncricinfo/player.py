"""Player records from the ESPN core API and the Statsguru pages."""

import csv
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from espncricinfo import _core
from espncricinfo.exceptions import PlayerNotFoundError

_ATHLETES = "http://core.espnuk.org/v2/sports/cricket/athletes"


class Player:
    """A player, loaded from the ESPN core API athlete record.

    Example values are for ``Player(277916)``, Ajinkya Rahane.
    """

    #: ESPNcricinfo player id.
    player_id: int
    #: Name as printed on scorecards, ``'Ajinkya Rahane'``.
    name: str
    #: ``'Ajinkya'``.
    first_name: str
    #: ``'Ajinkya Madhukar Rahane'``.
    full_name: str
    #: Date of birth, or None if ESPN has none.
    date_of_birth: date | None
    #: Age in years as ESPN reports it, or None.
    age: int | None
    #: ``'Top-order batter'``, or None.
    playing_role: str | None
    #: ``'Right-hand bat'``, or None.
    batting_style: str | None
    #: ``'Right-arm medium'``, or None.
    bowling_style: str | None
    #: The core API athlete record.
    json: dict[str, Any]

    def __init__(self, player_id: int | str) -> None:
        """Load the player record.

        Args:
            player_id: ESPNcricinfo player id (the number in a profile URL).
        """
        self.player_id = int(player_id)
        self.json = self._get_json()
        record = self.json
        self.name = record["name"]
        self.first_name = record.get("firstName", "")
        self.full_name = record.get("fullName", self.name)
        born = record.get("dateOfBirth")
        self.date_of_birth = date.fromisoformat(born[:10]) if born else None
        self.age = record.get("age")
        self.playing_role = (record.get("position") or {}).get("name")
        styles = {
            style.get("type"): style.get("description")
            for style in record.get("style") or []
        }
        self.batting_style = styles.get("batting")
        self.bowling_style = styles.get("bowling")

    def __str__(self) -> str:
        """Return the player's name."""
        return self.name

    def __repr__(self) -> str:
        """Return ``Player(player_id)``."""
        return f"Player({self.player_id})"

    def _get_json(self) -> dict[str, Any]:
        response = _core.http_get(f"{_ATHLETES}/{self.player_id}")
        if response.status_code == 404:
            raise PlayerNotFoundError(f"Player not found: {self.player_id}")
        response.raise_for_status()
        return response.json()

    @cached_property
    def major_teams(self) -> list[str]:
        """Names of the player's major teams (one request per team, on first access)."""
        teams = []
        for reference in self.json.get("majorTeams", []):
            response = _core.http_get(reference["$ref"])
            response.raise_for_status()
            team = response.json()
            name = team.get("longName") or team.get("displayName") or team.get("name")
            if name:
                teams.append(name)
        return teams

    def _write_stats_table(self, query: str, table_index: int, file_name: str) -> None:
        """Write one table of the player's stats page to ``file_name`` as CSV.

        Each row's cells are on separate lines in ESPN's HTML, so a row's text
        split on newlines gives its cells (with an empty leading cell).
        """
        url = (
            "https://stats.espncricinfo.com/ci/engine/player/"
            f"{self.player_id}.html?{query}"
        )
        response = _core.http_get(url)
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
