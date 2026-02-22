# python-espncricinfo

A Python 3 client for ESPNCricinfo's match, summary and player information.

### Description

A Python 3 client for ESPNCricinfo match, series and player data. The library uses Playwright (WebKit) to fetch match pages and extract embedded JSON, bypassing Akamai CDN restrictions on the legacy engine API endpoints. Both a `match_id` and `series_id` are required to instantiate a `Match` — both can be obtained from `Match.get_recent_matches()`. See the Usage section for instructions, and see `match.py` for individual functions.

Disclaimer: This library is not intended for commercial use and neither it nor its creator has any affiliation with ESPNCricInfo. The [LICENSE](LICENSE.txt) for this library applies only to the code, not to the data.

The current version of this library is 0.6.1. It is very much a work in progress, and bug reports and feature requests are welcomed.

### Installation

```python
pip3 install python-espncricinfo
```

### Usage

For a summary of live matches, create an instance of the `Summary` class:

```python
>>> from espncricinfo.summary import Summary
>>> s = Summary()
>>> s.match_ids
['68079', '68209', '68081', '61375', '65429']
```

For individual matches, pass in both the match ID and series ID. These can be discovered from `get_recent_matches()`, or read from a match page URL (the two numeric IDs in the URL path):

```python
>>> from espncricinfo.match import Match
>>> # Get recent matches as (series_id, match_id) tuples
>>> Match.get_recent_matches(date="2026-02-06")
[(1478874, 1478914), ...]
>>> # Construct a match directly
>>> m = Match(1478914, 1478874)
>>> m.description
'IND Women v AUS Women'
>>> m.match_class
'WT20I'
>>> m.result
'IND Women won by 17 runs'
```

A full list of methods available to an instance of the `Match` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/match.py).

For player details, pass in the player ID (found in a player's URL - for example, [Ajinkya Rahane](http://www.espncricinfo.com/west-indies-v-india-2016/content/player/277916.html) is '277916'):

```python
>>> from espncricinfo.player import Player
>>> p = Player('277916')
>>> p.name
'Ajinkya Rahane'
```

A full list of methods available to an instance of the `Player` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/player.py).

For series (or league) details, pass in the series ID (found in a match URL, for example, [India's 2018 tour of England](http://www.espncricinfo.com/series/18018/game/1119549/england-vs-india-1st-test-ind-in-eng-2018) is '18018'):

```python
>>> from espncricinfo.series import Series
>>> s = Series('18018')
>>> s.name
'India tour of Ireland and England 2018'
```

### Tests

**Unit tests** (no network required — uses recorded fixtures):

```shell
uv run pytest tests/ -k "not integration"
```

**Integration tests** (hits live ESPN Cricinfo via Playwright):

```shell
uv run pytest tests/ --live
```

**Refreshing fixtures** (re-records fixtures from live site):

```shell
uv run python scripts/refresh_fixtures.py
```

Playwright and WebKit must be installed:

```shell
uv add --dev playwright
uv run playwright install webkit
```

### Requirements

See requirements.txt
