# python-espncricinfo

[![PyPI](https://img.shields.io/pypi/v/python-espncricinfo)](https://pypi.org/project/python-espncricinfo/)
[![Downloads](https://static.pepy.tech/badge/python-espncricinfo)](https://pepy.tech/projects/python-espncricinfo)
[![CI](https://github.com/outside-edge/python-espncricinfo/actions/workflows/ci.yml/badge.svg)](https://github.com/outside-edge/python-espncricinfo/actions/workflows/ci.yml)
[![Docs](https://github.com/outside-edge/python-espncricinfo/actions/workflows/docs.yml/badge.svg)](https://outside-edge.github.io/python-espncricinfo/)
[![Python](https://img.shields.io/pypi/pyversions/python-espncricinfo)](https://pypi.org/project/python-espncricinfo/)

<!-- SPHINX-START -->

A Python client for ESPNcricinfo match, series, season, team and player data.

## Description

Match pages are loaded with Playwright (WebKit), because ESPN's CDN refuses plain HTTP clients; player, series, season and team records come from ESPN's core JSON API. A `Match` needs only a `match_id`; `Match.get_recent_matches()` and `Series(...).matches` list them.

Disclaimer: This library is not intended for commercial use and neither it nor its creator has any affiliation with ESPNCricInfo. The [LICENSE](https://github.com/outside-edge/python-espncricinfo/blob/master/LICENSE.txt) for this library applies only to the code, not to the data.

## Installation

```shell
uv add python-espncricinfo
```

Or with pip:

```shell
pip install python-espncricinfo
```

After installation, install the Playwright WebKit browser (required for fetching match data):

```shell
uv run playwright install webkit
```

<!-- USAGE-START -->

## Recent matches

`Summary().matches` lists the matches on ESPNcricinfo's results page. Pass a date to look back; ESPN returns about two weeks of matches ending on that day.

```python
>>> from espncricinfo.match import Match
>>> refs = Match.get_recent_matches(date="2026-02-28")
>>> len(refs)
195
>>> refs[0]
MatchRef(series_id=1523975, match_id=1523981)
>>> series_id, match_id = refs[0]  # MatchRefs unpack like tuples
```

`Summary(date=...)` wraps the same call; its result is in `.matches`.

## A single match

A match needs only its match ID, the number in a match page URL. Passing the series ID too (`Match(1478914, 1478874)`, or `MatchRef.to_match()`) skips a redirect. Loading a match starts a headless WebKit browser.

```python
>>> m = Match(1478914)
>>> m.description
'IND Women v AUS Women'
>>> m.match_class
'WT20I'
>>> m.result
'IND Women won by 17 runs'
>>> m.batting_scorecard[0][0]["name"], m.batting_scorecard[0][0]["runs"]
('S Mandhana', 82)
>>> m.bowling_scorecard[0][0]["name"], m.bowling_scorecard[0][0]["wickets"]
('D Brown', 0)
```

`batting_scorecard` and `bowling_scorecard` hold one list per innings and one dict per player. `over_by_over` gives runs and wickets for every over, and each `m.innings` entry has `fours` and `sixes`.

## Players

The player ID is the number at the end of a player's profile URL.

```python
>>> from espncricinfo.player import Player
>>> p = Player(277916)
>>> p.full_name
'Ajinkya Madhukar Rahane'
>>> p.get_data(file_name="rahane_tests.csv", match_format=1, data_type="batting")
```

`get_data` writes one row per match (85 Tests for Rahane); `get_career_summary` and `get_career_averages` write the summary tables from the same Statsguru page.

## Series, seasons and teams

```python
>>> from espncricinfo.series import Series
>>> ipl = Series(1449924)
>>> ipl.name
'Indian Premier League'
>>> season = ipl.current_season
>>> season.year, len(season.teams)
(2025, 10)
>>> season.teams[0].name
'Chennai Super Kings'
```

Seasons that cross New Year, like the Big Bash League's, each have their own series ID. Look one up by the label ESPNcricinfo shows:

```python
>>> bbl = Series(8044)
>>> season = bbl.season("2024/25")  # also 2024, "2024-25" or "2024/2025"
>>> season.label, season.series_id
('2024/25', 1443056)
```

`series.season_objects` lists every season and `season.match_refs` that season's matches. `series.matches` collects MatchRefs across all seasons (1,254 for the IPL), and `series.current_matches` keeps those in progress. `team.players` loads the squad on demand. ESPN's records for some bilateral tours are incomplete, for example listing one team for a two-team series.

<!-- USAGE-END -->

## Development

<!-- DEV-START -->

**Unit tests** (no network required — uses recorded fixtures):

```shell
uv run pytest
```

**Integration tests** (hits live ESPN Cricinfo via Playwright):

```shell
uv run pytest --live
```

**Refreshing fixtures** (re-records fixtures from live site):

```shell
uv run python scripts/refresh_fixtures.py
```

Integration tests and the fixture refresh need the WebKit browser:

```shell
uv run playwright install webkit
```
