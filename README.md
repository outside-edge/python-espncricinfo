# python-espncricinfo

[![PyPI](https://img.shields.io/pypi/v/python-espncricinfo)](https://pypi.org/project/python-espncricinfo/)
[![Downloads](https://static.pepy.tech/badge/python-espncricinfo)](https://pepy.tech/projects/python-espncricinfo)
[![CI](https://github.com/outside-edge/python-espncricinfo/actions/workflows/ci.yml/badge.svg)](https://github.com/outside-edge/python-espncricinfo/actions/workflows/ci.yml)
[![Docs](https://github.com/outside-edge/python-espncricinfo/actions/workflows/docs.yml/badge.svg)](https://outside-edge.github.io/python-espncricinfo/)
[![Python](https://img.shields.io/pypi/pyversions/python-espncricinfo)](https://pypi.org/project/python-espncricinfo/)

<!-- SPHINX-START -->

A Python client for ESPNcricinfo match, series, season, team and player data.

## Description

Match pages are loaded with Playwright (WebKit), because ESPN's CDN refuses plain HTTP clients; player, series, season and team records come from ESPN's core JSON API. A `Match` needs both a `match_id` and a `series_id`, which `Match.get_recent_matches()` and `Series(...).matches` provide.

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

## Usage

For a summary of live matches, create an instance of the `Summary` class:

```python
>>> from espncricinfo.summary import Summary
>>> s = Summary()
>>> s.matches
[MatchRef(series_id=1478874, match_id=1478914), ...]
>>> for ref in s.matches:
...     m = ref.to_match()
...     print(m.description)

# Tuple unpacking also works:
>>> for series_id, match_id in s.matches:
...     print(series_id, match_id)
```

For individual matches, pass in both the match ID and series ID. These can be discovered from `get_recent_matches()`, or read from a match page URL (the two numeric IDs in the URL path):

```python
>>> from espncricinfo.match import Match
>>> from espncricinfo.match_ref import MatchRef
>>> # Get recent matches as MatchRef objects
>>> Match.get_recent_matches(date="2026-02-06")
[MatchRef(series_id=1478874, match_id=1478914), ...]
>>> # Construct a match directly
>>> m = Match(1478914, 1478874)
>>> m.description
'IND Women v AUS Women'
>>> m.match_class
'WT20I'
>>> m.result
'IND Women won by 17 runs'
```

A full list of methods available to an instance of the `Match` class is in [the code](https://github.com/outside-edge/python-espncricinfo/blob/master/espncricinfo/match.py).

For player details, pass in the player ID (found in a player's URL - for example, [Ajinkya Rahane](http://www.espncricinfo.com/west-indies-v-india-2016/content/player/277916.html) is '277916'):

```python
>>> from espncricinfo.player import Player
>>> p = Player('277916')
>>> p.name
'Ajinkya Rahane'
```

A full list of methods available to an instance of the `Player` class is in [the code](https://github.com/outside-edge/python-espncricinfo/blob/master/espncricinfo/player.py).

For series (or league) details, pass in the series ID (found in a match URL, for example, [India's 2018 tour of England](http://www.espncricinfo.com/series/18018/game/1119549/england-vs-india-1st-test-ind-in-eng-2018) is '18018'):

```python
>>> from espncricinfo.series import Series
>>> s = Series('18018')
>>> s.name
'India tour of Ireland and England 2018'
```

Navigate from a series to its seasons, teams, and matches:

```python
from espncricinfo.series import Series

series = Series(1478874)
season = series.current_season
for team in season.teams:
    print(team.name, team.match)
for ref in series.matches:
    print(ref.series_id, ref.match_id)
```

`series.season_objects` lists all seasons. `season.match_refs` lists that season's matches, while `series.current_matches` contains only matches whose ESPN status is in progress. These match lists contain lightweight `MatchRef` objects; loading a full `Match` launches Playwright. `team.players` loads player records on demand.

## Tests

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
